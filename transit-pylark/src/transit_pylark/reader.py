# from pathlib import Path
# import time
# import json

# from rich.pretty import pprint
from lark import Lark, Transformer, Discard, Tree

import time

from .cache import TransitCacheControl
from .types import (
    frozendict,
    frozenlist,
    transit_tag,
    mapkey,
    keyword,
    quoted
)
from .codecs import TransitTagResolver, TransitDecoder

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

class TransitScalarTransformer(Transformer):

    def __init__(self, resolver: TransitTagResolver, control: TransitCacheControl):
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

    def __init__(self, resolver: TransitTagResolver | None = None):
        self.control = TransitCacheControl()
        if resolver is None:
            resolver = TransitTagResolver.default()
        self.resolver = resolver
        self.transit = Lark(
            TRANSIT_STRING_GRAMMAR,
            start="value",
            parser="lalr",
            transformer=TransitScalarTransformer(resolver=resolver, control=self.control),
        )
        self.__cache = {}

    def value(self, args):
        (s,) = args
        # print("value inspect:", s)
        if self.control.enforce:
            cache_analysis = self.__cache_analysis(s)
            # print("do I think this is cacheable?", cache_analysis)
            if cache_analysis.get("should_cache", False):
                self.__commit_to_cache(s, s)
            else:
                # print("I don't think I should cache:", s)
                pass
            if cache_analysis.get("cache_token"):
                token = cache_analysis["cache_token"]
                round = TransitCacheControl.code_to_index(token)
                popped = self.__cache[round]
                # print("popped!", popped)
                return popped
        return s

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

    def __transit_tagged_dict(self, xs):
        assert len(xs) == 1, "I don't know what to do with more than 2 entries"
        (k, v) = next(iter(xs.items()))
        tag_key = transit_tag.tag_key(k.k.tag)
        res = self.resolver.resolve(tag_key, v)
        self.__commit_to_cache(k.k, res)
        return res

    def __emit_dict(self, xs):
        if len(xs) and type(next(iter(xs.keys())).k) is transit_tag:
            return self.__transit_tagged_dict(xs)
        obj = {}
        for k, v in xs.items():
            if type(k) is mapkey:
                obj[k.k] = v
            else:
                obj[k] = v
        return frozendict(obj)

    def dict(self, args):
        xs = self.__dict(args)
        return self.__emit_dict(xs)

    def __commit_to_cache(self, key, res):
        # # code = TransitCacheControl.index_to_code(next)
        # # round = TransitCacheControl.code_to_index(code)
        # print("Adding to cache", res, self.control.control_stack)
        if self.control.enforce:
            offset = self.control.ack_cache_control(key)
            self.__cache[offset] = res

    def __transit_tagged_list(self, xs):
        assert len(xs) == 2, "I don't know what to do with more than 2 entries"
        (k, v) = xs
        tag_key = transit_tag.tag_key(k.tag)
        res = self.resolver.resolve(tag_key, v)
        self.__commit_to_cache(k, res)
        return res

    def list(self, args):
        xs = self.__list(args)
        # print("dealing with a list", xs)
        if type(xs) is dict:
            return self.__emit_dict(xs)
        elif len(xs) and type(xs[0]) is transit_tag:
            # print("it is a transit list", xs)
            return self.__transit_tagged_list(xs)
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
        elif self.control.enforce and transit_part.startswith("^"):
            # special cache instruction
            remainder = transit_part[1:]
            if remainder == " ":
                result = self.CACHE_MAP_TOKEN
            else:
                result = self.CACHE_TOKEN + remainder
        else:
            result = transit_part
        return result

class TransitReader:

    def __init__(self):
        
        # from rich.pretty import pprint
        self.xformer = TransitJsonTransformer()
        self.parser: Lark = Lark(
            TRANSIT_GRAMMAR,
            start="value",
            parser="lalr",
            transformer=self.xformer,
        )


    def read(self, obj, enable_cache: bool = True):
        # TODO: wouldn't hurt to add a threading lock here
        try:
            self.xformer.control.set_enforce(enable_cache)
            return self.parser.parse(obj)
        finally:
            self.xformer.control.reset()
