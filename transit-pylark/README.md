Python parser library for reading transit data

Written with lark parsing library, mostly for educational purposes

Parsing performance is speedy but several times slower than native json

Currently only supporting decoding (not encode)

Transit design features tag annotation for extensible parsing

```sh

devenv shell run-test-suite
  
```

decoder modules included:

- [arrow](https://arrow.readthedocs.io/en/latest/index.html) for dates
- [yarl](https://pypi.org/project/yarl/) for links
- [mpmath](https://mpmath.org/) for arbitrary precision decimals

because of the complex types representable by transit:
- frozendict via [immutabledict](https://pypi.org/project/immutabledict/) for maps
- [frozenlist](https://pypi.org/project/frozenlist/) for all vectors/lists
- [frozenset](https://www.python3.info/stdlib/builtin/frozenset.html) for sets

references:

- https://cognitect.com/blog/2014/7/22/transit
- https://swannodette.github.io/2014/07/23/a-closer-look-at-transit/
- https://lark-parser.readthedocs.io/en/latest/index.html
- https://en.wikipedia.org/wiki/LALR_parser
- https://github.com/cognitect/transit-python


