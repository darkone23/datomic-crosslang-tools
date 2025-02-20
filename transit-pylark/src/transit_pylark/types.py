from dataclasses import dataclass

from frozenlist import FrozenList
from immutabledict import immutabledict

class frozendict(immutabledict):

    def __repr__(self):
        frozenstr = super().__repr__()
        xs_part = frozenstr[11:]
        return f"frozendict({xs_part}"

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

