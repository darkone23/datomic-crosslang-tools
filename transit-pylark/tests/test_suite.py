
from pathlib import Path
from rich.pretty import pprint
import time
from transit_pylark.reader import TransitReader

import unittest


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
