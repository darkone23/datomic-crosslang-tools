
from pathlib import Path
from rich.pretty import pprint
import time
from transit_pylark.core import (
    TransitReader
)


import unittest

exemplar_files = [
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

class TransitExampleRunner:

    def __init__(self, reader: TransitReader, source: Path):
        self.name = source.name
        self.transit_txt = (
            source.read_text()
        )  # """["~:a","~:ab","~:abc","~:abcd","~:abcde","~:a1","~:b2","~:c3","~:a_b"]"""
        self.reader = reader

    def run_parse(self):

        payload_size = len(self.transit_txt)
        # print(f"Parsing {self.name} json document of len", payload_size)

        start = time.monotonic()

        tree = self.reader.read(self.transit_txt)
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


class TransitTestSuite(unittest.TestCase):

    def test_basic_example(self):

        # s = 'hello world'
        # self.assertEqual(s.split(), ['hello', 'world'])
        # # check that s.split fails when the separator is not a string
        # with self.assertRaises(TypeError):
        #     s.split(2)

        verbose_files = [ "./tests/test_data/example.verbose.json" ]

        reader = TransitReader()

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
                tool = TransitExampleRunner(reader, source)
                parse_results = tool.run_parse()
                results.append(parse_results)

            tree_0 = results[0]["tree"]
            tree_1 = results[1]["tree"]

            for run in results:
                # pprint(run["tree"]) # lost pretty printing w/ frozen[dict|list]
                del run["tree"]  # just print out stats for now
                pprint(run)

            self.assertEqual(tree_0, tree_1)

if __name__ == '__main__':
    import nose2
    nose2.main()
