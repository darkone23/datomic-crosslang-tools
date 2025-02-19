from pathlib import Path
import time
import json

from rich.pretty import pprint
from lark import Lark, Transformer, Discard, Tree, Token

from dataclasses import dataclass

from frozenlist import FrozenList
from immutabledict import immutabledict



class TransitCacheControl:
    """

    private static final int CACHE_CODE_DIGITS = 44;
    private static final int BASE_CHAR_INDEX = 48;
    private static final String SUB_STR = "^";

    private String indexToCode(int index) {
        int hi = index / CACHE_CODE_DIGITS;
        int lo = index % CACHE_CODE_DIGITS;
        if (hi == 0) {
            return SUB_STR + (char)(lo + BASE_CHAR_INDEX);
        } else {
            return SUB_STR + (char)(hi + BASE_CHAR_INDEX) + (char)(lo + BASE_CHAR_INDEX);
        }
    }

    private int codeToIndex(String s) {
        int sz = s.length();
        if (sz == 2) {
            return ((int)s.charAt(1) - WriteCache.BASE_CHAR_INDEX);
        } else {
            return (((int)s.charAt(1) - WriteCache.BASE_CHAR_INDEX) * WriteCache.CACHE_CODE_DIGITS) +
                    ((int)s.charAt(2) - WriteCache.BASE_CHAR_INDEX);
        }
    }
    """

    CACHE_CODE_DIGITS = 44
    BASE_CHAR_INDEX = 48
    SUB_STR = "^"

    def __init__(self):
        self.reset()

    def reset(self):
        # print("Initializing fresh cache stack")
        self.cache = {}
        self.cursor = 0

    def ack_cache_control(self, item: list):
        # print("thanks for popping", item)
        cursor = self.cache[item]
        del self.cache[item]
        return cursor

    def syn_cache_control(self, item):
        """We need to grab our ID as soon as we see the cacheable token - not AFTER parsing the token!"""
        # print("thanks for adding", item)
        self.cache[item] = self.cursor
        self.cursor += 1
        # print(self.control_stack)

    @staticmethod
    def index_to_code(index: int) -> str:
        CACHE_CODE_DIGITS = TransitCacheControl.CACHE_CODE_DIGITS
        BASE_CHAR_INDEX = TransitCacheControl.BASE_CHAR_INDEX
        SUB_STR = TransitCacheControl.SUB_STR
        hi: int = int(index / CACHE_CODE_DIGITS)
        lo: int = index % CACHE_CODE_DIGITS
        if hi == 0:
            return SUB_STR + chr(lo + BASE_CHAR_INDEX)
        else:
            return SUB_STR + chr(hi + BASE_CHAR_INDEX) + chr(lo + BASE_CHAR_INDEX)

    @staticmethod
    def code_to_index(s: str) -> int:
        CACHE_CODE_DIGITS = TransitCacheControl.CACHE_CODE_DIGITS
        BASE_CHAR_INDEX = TransitCacheControl.BASE_CHAR_INDEX
        SUB_STR = TransitCacheControl.SUB_STR
        sz = len(s)
        if sz == 2:
            return ord(s[1]) - BASE_CHAR_INDEX
        else:
            return ((ord(s[1]) - BASE_CHAR_INDEX) * CACHE_CODE_DIGITS) + (
                ord(s[2]) - BASE_CHAR_INDEX
            )

class frozendict(immutabledict):

    def __repr__(self):
        frozenstr = super().__repr__()
        xs_part = frozenstr[11:]
        return f"frozendict({xs_part})"

class frozenlist(FrozenList):

    def __init__(self, items):
        super().__init__(items)
        self.freeze()

    def __repr__(self):
        frozenstr = super().__repr__()
        xs_part = frozenstr[25:-2]
        return f"frozenlist({xs_part})"

@dataclass(frozen=True)
class transit_tag:
    tag: str

    @staticmethod
    def tagged_value(tag: str, value):
        return (transit_tag(tag), value)

    def __len__(self):
        return len(self.tag)

    def __str__(self):
        return f":{self.tag}"

    @staticmethod
    def tag_key(name):
        return f"tag:{name}"


@dataclass(frozen=True)
class keyword:
    v: str

    def __len__(self):
        return len(self.v)

    def __str__(self):
        return f":{self.v}"


@dataclass(frozen=True)
class mapkey:
    k: str

    def __len__(self):
        return len(self.k)

    def __str__(self):
        return f"{self.k}"


@dataclass(frozen=True)
class quoted:
    v: str

    def __len__(self):
        return len(self.v)

    def __str__(self):
        return f"{self.v}"


# basic json grammar needs to be extended to handle transit tagging and caching
# should support user defined extensions in the transformers

TRANSIT_STRING_GRAMMAR = """
value: "~" instruction [ chars ]

instruction: nil
         | escape_tilde
         | escape_hat
         | bool
         | base64
         | keyword
         | symbol
         | tag

nil: "_"
escape_tilde: "~"
escape_hat: "^"
bool: "?"
base64: "b"
keyword: ":"
symbol: "$"
tag: "#"

chars: /.+/
"""

TRANSIT_GRAMMAR = """
value: dict
     | list
     | transit_str
     | transit_num
     | false | true | null

false: "false"
true: "true"
null: "null"

list : "[" [ value ("," value)* ] "]"
dict : "{" [pair ("," pair)*] "}"
pair : transit_str ":" value

transit_str : ESCAPED_STRING
transit_num : SIGNED_NUMBER

%import common.SIGNED_NUMBER
%import common.ESCAPED_STRING
%import common.WS
%ignore WS
"""


class TransitSerde:

    def deserialize(self, encoded: str):
        pass


class KeywordSerde:

    def deserialize(self, encoded: str):
        return keyword(encoded)


class TagSerde:

    def deserialize(self, encoded: str):
        return transit_tag(encoded)

class QuoteTagSerde:

    def deserialize(self, encoded: str):
        return quoted(encoded)

class CompositeMapSerde:

    def deserialize(self, encoded: list):
        assert type(encoded) is frozenlist, f"Expecting a list value for composite maps: {encoded}"
        res = {}
        # print("cmap hydrate time", encoded)
        # print("look at this cmap data:", encoded)
        for n in range(int(len(encoded) / 2)):
            idx = n * 2
            (k, v) = encoded[idx:idx+2]
            res[k] = v
        return frozendict(res)
        # return quoted(encoded)


class TransitTypeResolver:

    def __init__(self):
        self.mapping = {}

    def add_serde(self, name: str, serde: TransitSerde):
        self.mapping[name] = serde

    def resolve(self, name: str, value: str | None = None):
        if value is not None and type(value) is Token:
            # print("making it a str!", type(value))
            value = str(value)
        if name in self.mapping:
            # print("looking up:", name, value)
            return self.mapping[name].deserialize(value)
        else:
            # print("tagged", name, value)
            return transit_tag.tagged_value(name, value)

    @staticmethod
    def default():
        resolver = TransitTypeResolver()
        # these names matching the lark grammar names
        resolver.add_serde("keyword", KeywordSerde())
        resolver.add_serde("tag", TagSerde())
        resolver.add_serde("tag:'", QuoteTagSerde())
        resolver.add_serde("tag:cmap", CompositeMapSerde())
        return resolver


class TransitScalarTransformer(Transformer):

    def __init__(self, resolver: TransitTypeResolver, control: TransitCacheControl):
        self.resolver = resolver
        self.control = control

    def value(self, args):
        arg_size = len(args)
        if arg_size == 1:
            (v,) = args
            # must be: escape str or nil
            # print("one args???")
            # print("you asked me to resolve a one arg mystery", v)
            res = self.resolver.resolve(k)
            self.control.syn_cache_control(res)
            return res
        elif arg_size == 2:
            (k, v) = args
            # print("two args???", k, v)
            # print("you asked me to resolve a mystery", k, v)
            res = self.resolver.resolve(k, v)
            self.control.syn_cache_control(res)
            return res
        else:
            raise ValueError(f"Unexpected transit str parser len... {len(args)}")

    def chars(self, c):
        (t,) = c
        # (c,) = t.children
        return t

    def instruction(self, s):
        (s,) = s
        return s.data

    # def str(self, s):
    #     (s,) = s
    #     return s

    # def chars(self, s):
    #     (s,) = s
    #     return s

# transformer can be responsible for cache reading layer
class TransitJsonTransformer(Transformer):

    CACHE_MAP_TOKEN = "^ "
    CACHE_TOKEN = "CACHECODE:^"

    def __cache_analysis(self, value):
        v_type = type(value)
        res = dict(should_cache=False, v_type=v_type, cache_token=None)
        if v_type is int or v_type is float:
            return res
        if v_type is str:
            v_size = len(value)
            if value == self.CACHE_MAP_TOKEN:
                res["v_type"] = "map-token"
                return res
            elif value.startswith(self.CACHE_TOKEN):
                res["cache_token"] = value[10:]
            # else:
            # res["should_cache"] = v_size > 3
            # from transit spec:
        elif v_type is mapkey:
            # Strings more than 3 characters long are also cached when they are used as keys in maps whose keys are all "stringable"
            # pass
            # print("wow a mapkey!", value)
            v_size = len(value)
            res["should_cache"] = v_size > 3
        elif v_type is keyword:
            v_size = len(value)
            res["should_cache"] = v_size > 1

        # TODO: symbols, tags

        return res

    def value(self, args):
        (s,) = args
        # print("value inspect:", s)
        cache_analysis = self.__cache_analysis(s)
        # print("do I think this is cacheable?", cache_analysis)
        if cache_analysis.get("should_cache", False):
            self.__add_to_index(s, s)
        if cache_analysis.get("cache_token"):
            token = cache_analysis["cache_token"]
            round = TransitCacheControl.code_to_index(token)
            popped = self.__cache[round]
            # print("popped!", popped)
            return popped
        return s

    def __init__(self, resolver: TransitTypeResolver | None = None):
        self.control = TransitCacheControl()
        if resolver is None:
            resolver = TransitTypeResolver.default()
        self.resolver = resolver
        self.transit = Lark(
            TRANSIT_STRING_GRAMMAR,
            start="value",
            parser="lalr",
            transformer=TransitScalarTransformer(resolver=resolver, control=self.control),
        )
        self.__cache = {}

    def transit_num(self, args):
        (n,) = args
        return float(n)

    def pair(self, args):
        (k, v) = args
        return (k, v)

    def false(self, args):
        return False

    def true(self, args):
        return True

    def null(self, args):
        return None

    # list = list
    # pair = tuple

    def __list(self, args):
        if len(args) == 0:
            # print("empty list")
            return []
        if len(args) == 1:
            (s,) = args
            # print("list of one", s)
            return [s]
        else:
            head = args[0]
            # print("list", head, args)
            if head == self.CACHE_MAP_TOKEN:
                res = {}
                for n in range(int(len(args) / 2)):
                    idx = n * 2 + 1
                    # print("searching for ", idx, args[idx:idx+2])
                    (k, v) = args[idx : idx + 2]
                    res[mapkey(k)] = v
                return res
            else:
                return args

    def __dict(self, args):
        res = {}
        for pair in args:
            (k, v) = pair
            res[mapkey(k)] = v
        return res

    def __transit_dict(self, xs):
        assert len(xs) == 1, "I don't know what to do with more than 2 entries"
        (k, v) = next(iter(xs.items()))
        tag_key = transit_tag.tag_key(k.k.tag)
        res = self.resolver.resolve(tag_key, v)
        self.__add_to_index(k.k, res)
        return res

    def dict(self, args):
        xs = self.__dict(args)
        if len(xs) and type(next(iter(xs.keys())).k) is transit_tag:
            return self.__transit_dict(xs)
        return frozendict(xs)

    def __add_to_index(self, key, res):
        # # code = TransitCacheControl.index_to_code(next)
        # # round = TransitCacheControl.code_to_index(code)
        # print("Adding to cache", res, self.control.control_stack)
        offset = self.control.ack_cache_control(key)
        self.__cache[offset] = res

    def __transit_list(self, xs):
        assert len(xs) == 2, "I don't know what to do with more than 2 entries"
        (k, v) = xs
        tag_key = transit_tag.tag_key(k.tag)
        res = self.resolver.resolve(tag_key, v)
        self.__add_to_index(k, res)
        return res

    def list(self, args):
        xs = self.__list(args)
        # print("dealing with a list", xs)
        if type(xs) is dict:
            if len(xs) and type(next(iter(xs.keys())).k) is transit_tag:
                xs = self.__transit_dict(xs)
                return frozendict(xs)
            else:
                return frozendict(xs)
        elif len(xs) and type(xs[0]) is transit_tag:
            # print("it is a transit list", xs)
            return self.__transit_list(xs)
        # print("about to make my result list:", xs)
        return frozenlist(xs)

    def transit_str(self, args):
        # self.parser.parse()
        (s,) = args
        encoded_str = str(s)
        # print("you casked me to handle trnsit str?", encoded_str)
        transit_part = encoded_str[1:-1]  # not needing "" parts of str
        if transit_part.startswith("~"):
            # special transit escaped string
            result = self.transit.parse(transit_part)
            # try:
            # except Exception as e:
            #     print("Exception parsing transit encoded str node!", e)
            #     # print(e)
            #     result = transit_part
        elif transit_part.startswith("^"):
            # special cache instruction
            remainder = transit_part[1:]
            if remainder == " ":
                result = self.CACHE_MAP_TOKEN
            else:
                result = self.CACHE_TOKEN + remainder
        else:
            result = transit_part
        return result


class TransitExampleRunner:

    def __init__(self, parser: Lark, source: Path):
        self.name = source.name
        self.transit_txt = (
            source.read_text()
        )  # """["~:a","~:ab","~:abc","~:abcd","~:abcde","~:a1","~:b2","~:c3","~:a_b"]"""
        self.parser: Lark = parser

    def run_parse(self):

        payload_size = len(self.transit_txt)
        # print(f"Parsing {self.name} json document of len", payload_size)

        start = time.monotonic()

        tree = self.parser.parse(self.transit_txt)
        # print(tree.pretty())

        parse_time = time.monotonic() - start
        # print(f"Transforming {self.name} document after n seconds: ", parse_time)

        # pprint(tree)
        # result = transformer.transform(tree)
        # print(result.pretty())

        # json.loads(transit_txt)

        # print(f"Total {self.name} took n seconds:", time.monotonic() - start)

        return dict(
            name=self.name,
            size=payload_size,
            parse_time=parse_time,
            tree=tree,
        )


def main():

    # from rich.pretty import pprint
    xformer = TransitJsonTransformer()
    parser = Lark(
        TRANSIT_GRAMMAR,
        start="value",
        parser="lalr",
        transformer=xformer,
    )

    verbose_files = [
        "./test_data/simple/cmap_null_key.verbose.json",
        "./test_data/simple/cmap_pathological.verbose.json",
        "./test_data/simple/dates_interesting.verbose.json",
        "./test_data/simple/doubles_interesting.verbose.json",
        "./test_data/simple/doubles_small.verbose.json",
        "./test_data/simple/false.verbose.json",
        "./test_data/simple/ints.verbose.json",
        "./test_data/simple/ints_interesting.verbose.json",
        "./test_data/simple/ints_interesting_neg.verbose.json",
        "./test_data/simple/keywords.verbose.json",
        "./test_data/simple/list_empty.verbose.json",
        "./test_data/simple/list_mixed.verbose.json",
        "./test_data/simple/list_nested.verbose.json",
        "./test_data/simple/list_simple.verbose.json",
        "./test_data/simple/map_10_items.verbose.json",
        "./test_data/simple/map_10_nested.verbose.json",
        "./test_data/simple/map_1935_nested.verbose.json",
        "./test_data/simple/map_1936_nested.verbose.json",
        "./test_data/simple/map_1937_nested.verbose.json",
        "./test_data/simple/map_mixed.verbose.json",
        "./test_data/simple/map_nested.verbose.json",
        "./test_data/simple/map_numeric_keys.verbose.json",
        "./test_data/simple/map_simple.verbose.json",
        "./test_data/simple/map_string_keys.verbose.json",
        "./test_data/simple/map_unrecognized_vals.verbose.json",
        "./test_data/simple/map_vector_keys.verbose.json",
        "./test_data/simple/maps_four_char_keyword_keys.verbose.json",
        "./test_data/simple/maps_four_char_string_keys.verbose.json",
        "./test_data/simple/maps_four_char_sym_keys.verbose.json",
        "./test_data/simple/maps_three_char_keyword_keys.verbose.json",
        "./test_data/simple/maps_three_char_string_keys.verbose.json",
        "./test_data/simple/maps_three_char_sym_keys.verbose.json",
        "./test_data/simple/maps_two_char_keyword_keys.verbose.json",
        "./test_data/simple/maps_two_char_string_keys.verbose.json",
        "./test_data/simple/maps_two_char_sym_keys.verbose.json",
        "./test_data/simple/maps_unrecognized_keys.verbose.json",
        "./test_data/simple/nil.verbose.json",
        "./test_data/simple/one.verbose.json",
        "./test_data/simple/one_date.verbose.json",
        "./test_data/simple/one_keyword.verbose.json",
        "./test_data/simple/one_string.verbose.json",
        "./test_data/simple/one_symbol.verbose.json",
        "./test_data/simple/one_uri.verbose.json",
        "./test_data/simple/one_uuid.verbose.json",
        "./test_data/simple/set_empty.verbose.json",
        "./test_data/simple/set_mixed.verbose.json",
        "./test_data/simple/set_nested.verbose.json",
        "./test_data/simple/set_simple.verbose.json",
        "./test_data/simple/small_ints.verbose.json",
        "./test_data/simple/small_strings.verbose.json",
        "./test_data/simple/strings_hash.verbose.json",
        "./test_data/simple/strings_hat.verbose.json",
        "./test_data/simple/strings_tilde.verbose.json",
        "./test_data/simple/symbols.verbose.json",
        "./test_data/simple/true.verbose.json",
        "./test_data/simple/uris.verbose.json",
        "./test_data/simple/uuids.verbose.json",
        "./test_data/simple/vector_1935_keywords_repeated_twice.verbose.json",
        "./test_data/simple/vector_1936_keywords_repeated_twice.verbose.json",
        "./test_data/simple/vector_1937_keywords_repeated_twice.verbose.json",
        "./test_data/simple/vector_empty.verbose.json",
        "./test_data/simple/vector_mixed.verbose.json",
        "./test_data/simple/vector_nested.verbose.json",
        "./test_data/simple/vector_simple.verbose.json",
        "./test_data/simple/vector_special_numbers.verbose.json",
        "./test_data/simple/vector_unrecognized_vals.verbose.json",
        "./test_data/simple/zero.verbose.json",
    ]

    verbose_files = [ "./test_data/example.verbose.json" ]

    for f in verbose_files:


        transit_cache_example = Path(
            f.replace(".verbose.json", ".json")
            # transit cache encoded data
            # "./test_data/example.json"
            # "./test_data/simple/nil.json"
        )

        transit_verbose_example = Path(
            f
            # transit verbose encoded data
            # f
            # "./test_data/example.verbose.json"
            # "./test_data/simple/nil.verbose.json"
        )

        results = []
        for source in [
            transit_cache_example,
            transit_verbose_example,
        ]:
            # print("Running example:", source)
            tool = TransitExampleRunner(parser, source)

            results.append(tool.run_parse())
            xformer.control.reset()

        tree_0 = results[0]["tree"]
        tree_1 = results[1]["tree"]

        for run in results:
            # pprint(run["tree"]) # lost pretty printing w/ frozen[dict|list]
            del run["tree"]  # just print out stats for now
            pprint(run)

        assert tree_0 == tree_1, "parsed trees are identical!"


if __name__ == "__main__":
    main()
