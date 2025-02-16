
from pathlib import Path
import json

from lark import Lark, Transformer, Discard

from dataclasses import dataclass

@dataclass(frozen=True)
class keyword:
    v: str

    def __str__(self):
        return f":{self.v}"

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

list : "[" [value ("," value)*] "]"
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

    def keyword(self, s):
        (s, ) = s
        return keyword(f"{s}")

    def str(self, s):
        (s, ) = s
        return s
    
    def chars(self, s):
        (s, ) = s
        return s

# transformer can be responsible for cache reading layer
class TransitJsonTransformer(Transformer):
    def __init__(self):
        self.transit = Lark(TRANSIT_STRING_GRAMMAR, start='value', parser='lalr', transformer=TransitScalarTransformer())

    def transit_num(self, args):
        (n, ) = args
        return float(n)

    # dict = dict
    # list = list
    # pair = tuple

    def transit_str(self, args):
        # self.parser.parse()
        encoded_str = str(args[0])
        # print("you casked me to handle trnsit str?", encoded_str)
        transit_part = encoded_str[1:-1] # not needing "" parts of str
        if transit_part.startswith("~"):
            try:
                result = self.transit.parse(transit_part)
            except Exception as e:
                print("Oh no an exception!", e)
                result = transit_part
        else:
            result = transit_part
        return result


def main():
    import time
    # from rich.pretty import pprint
    
    transit_txt = Path("./test_data/example.verbose.json").read_text() # """["~:a","~:ab","~:abc","~:abcd","~:abcde","~:a1","~:b2","~:c3","~:a_b"]"""
    # transit_txt = Path("./test_data/example.json").read_text() # """["~:a","~:ab","~:abc","~:abcd","~:abcde","~:a1","~:b2","~:c3","~:a_b"]"""
    transformer=TransitJsonTransformer()
    parser = Lark(TRANSIT_GRAMMAR, start="value", parser='lalr', transformer=transformer)

    start = time.monotonic()
    print("Parsing json document of len", len(transit_txt))

    tree = parser.parse(transit_txt)
    print(tree.pretty())
    
    print("Transforming document after n seconds: ", time.monotonic() - start)

    # result = transformer.transform(tree)
    # print(result.pretty())

    
    # json.loads(transit_txt)

    print("Took n seconds:", time.monotonic() - start)

if __name__ == "__main__":
    main()
