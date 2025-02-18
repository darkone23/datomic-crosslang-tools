from pathlib import Path
import json

from rich.pretty import pprint
from lark import Lark, Transformer, Discard

from dataclasses import dataclass


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
        return len(self.v)

    def __str__(self):
        return f"{self.v}"


# basic json grammar needs to be extended to handle transit tagging and caching
# should support user defined extensions in the transformers

TRANSIT_STRING_GRAMMAR = """
value: nil
     | tag
     | bool_t
     | bool_f
     | base64
     | keyword
     | symbol

nil:  "~_"
tag:  "~#" chars
bool_t:  "~?t"
bool_f:  "~?f"
base64:  "~b" chars
keyword:  "~:" chars
symbol:  "~$" chars
chars: /.+/
raw_str: /.+/
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


class TransitScalarTransformer(Transformer):

    def value(self, args):
        (v,) = args
        return v

    def keyword(self, s):
        (s,) = s
        return keyword(f"{s}")

    def str(self, s):
        (s,) = s
        return s

    def chars(self, s):
        (s,) = s
        return s


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


# transformer can be responsible for cache reading layer
class TransitJsonTransformer(Transformer):

    def __cache_analysis(self, value):
        v_type = type(value)
        res = dict(should_cache=False, v_type=v_type, cache_token=None)
        if v_type is int or v_type is float:
            return res
        if v_type is str:
            v_size = len(value)
            if value == "CACHE_MAP_TOKEN":
                res["v_type"] = "map-token"
                return res
            elif value.startswith("CACHECODE:^"):
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
            next = self.__cache_idx
            # code = TransitCacheControl.index_to_code(next)
            # round = TransitCacheControl.code_to_index(code)
            self.__cache[next] = s
            self.__cache_idx += 1
            # print("yes", code, round)
        if cache_analysis.get("cache_token"):
            token = cache_analysis["cache_token"]
            round = TransitCacheControl.code_to_index(token)
            popped = self.__cache[round]
            # print("popped!", popped)
            return popped
        return s

    def __init__(self):
        self.transit = Lark(
            TRANSIT_STRING_GRAMMAR,
            start="value",
            parser="lalr",
            transformer=TransitScalarTransformer(),
        )
        self.__cache = {}
        self.__cache_idx = 0

    def transit_num(self, args):
        (n,) = args
        return float(n)

    def dict(self, args):
        res = {}
        for pair in args:
            (k, v) = pair
            res[mapkey(k)] = v
        return res

    def pair(self, args):
        (k, v) = args
        return (k, v)

    # list = list
    # pair = tuple

    def list(self, args):
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
            if head == "CACHE_MAP_TOKEN":
                res = {}
                for n in range(int(len(args) / 2)):
                    idx = n * 2 + 1
                    # print("searching for ", idx, args[idx:idx+2])
                    (k, v) = args[idx : idx + 2]
                    res[mapkey(k)] = v
                return res
            else:
                return args

    def transit_str(self, args):
        # self.parser.parse()
        (s,) = args
        encoded_str = str(s)
        # print("you casked me to handle trnsit str?", encoded_str)
        transit_part = encoded_str[1:-1]  # not needing "" parts of str
        if transit_part.startswith("~"):
            try:
                result = self.transit.parse(transit_part)
            except Exception as e:
                print("Oh no an exception!", e)
                result = transit_part
        elif transit_part.startswith("^"):
            remainder = transit_part[1:]
            if remainder == " ":
                result = f"CACHE_MAP_TOKEN"
            else:
                result = f"CACHECODE:^{remainder}"
        else:
            result = transit_part
        return result


def main():
    import time

    # from rich.pretty import pprint

    transit_txt = Path(
        "./test_data/example.json"  # cached version of data
    ).read_text()  # """["~:a","~:ab","~:abc","~:abcd","~:abcde","~:a1","~:b2","~:c3","~:a_b"]"""
    # transit_txt = Path("./test_data/example.verbose.json").read_text() # """["~:a","~:ab","~:abc","~:abcd","~:abcde","~:a1","~:b2","~:c3","~:a_b"]"""
    transformer = TransitJsonTransformer()
    parser = Lark(
        TRANSIT_GRAMMAR, start="value", parser="lalr", transformer=transformer
    )

    print("Parsing json document of len", len(transit_txt))

    start = time.monotonic()

    tree = parser.parse(transit_txt)
    # print(tree.pretty())

    print("Transforming document after n seconds: ", time.monotonic() - start)

    pprint(tree)
    # result = transformer.transform(tree)
    # print(result.pretty())

    # json.loads(transit_txt)

    print("Took n seconds:", time.monotonic() - start)


if __name__ == "__main__":
    main()
