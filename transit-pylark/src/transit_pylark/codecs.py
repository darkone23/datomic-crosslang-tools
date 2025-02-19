
from .types import (
    keyword,
    transit_tag,
    quoted,
    frozenlist,
    frozendict
)

import lark

class TransitDecoder:

    def decode(self, encoded: str):
        pass

class KeywordDecoder(TransitDecoder):

    def decode(self, encoded: str):
        return keyword(encoded)


class TagDecoder(TransitDecoder):

    def decode(self, encoded: str):
        return transit_tag(encoded)

class QuoteTagDecoder(TransitDecoder):

    def decode(self, encoded: str):
        return quoted(encoded)

class CompositeMapDecoder(TransitDecoder):

    def decode(self, encoded: list):
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


class TransitTagResolver:

    def __init__(self):
        self.mapping = {}

    def add_decoder(self, name: str, serde: TransitDecoder):
        self.mapping[name] = serde

    def resolve(self, name: str, value):
        if value is not None and type(value) is lark.Token:
            # print("making it a str!", type(value))
            value = str(value)
        if name in self.mapping:
            # print("looking up:", name, value)
            return self.mapping[name].decode(value)
        else:
            # print("tagged", name, value)
            return transit_tag.tagged_value(name, value)

    @staticmethod
    def default():
        resolver = TransitTagResolver()
        # these names matching the lark grammar names
        resolver.add_decoder("keyword", KeywordDecoder())
        resolver.add_decoder("tag", TagDecoder())
        resolver.add_decoder("tag:'", QuoteTagDecoder())
        resolver.add_decoder("tag:cmap", CompositeMapDecoder())
        return resolver


