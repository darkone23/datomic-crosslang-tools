from pathlib import Path
from rich.pretty import pprint
import time
from transit_pylark.reader import TransitReader
from transit_pylark.types import (
    frozendict,
    frozenlist,
    transit_tag,
    mapkey,
    keyword,
    quoted
)

from nose2.tools import params

from dataclasses import dataclass

@dataclass
class ExemplarSpec:
    name: str
    expected: any

cmap_null_key = frozendict({
    None: "null as map key",
    frozenlist([1, 2]): "Array as key to force cmap"       
})

cmap_pathological = frozenlist([
    frozendict({
        keyword(v='any-value'): frozendict({
            frozenlist(['this vector makes this a cmap']): 'any value',
            'any string': keyword(v='victim')
        })
    }),
    frozendict({keyword(v='victim'): keyword(v='any-other-value')})
])

dates_interesting = None
doubles_interesting = frozenlist([-3.14159, 3.14159, 4.0E11, 2.998E8, 6.626E-34])
doubles_small = [-5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
false = None
ints = None
ints_interesting = None
ints_interesting_neg = None
keywords = None
list_empty = None
list_mixed = None
list_nested = None
list_simple = None
map_10_items = None
map_10_nested = None
map_1935_nested = None
map_1936_nested = None
map_1937_nested = None
map_mixed = None
map_nested = None
map_numeric_keys = None
map_simple = None
map_string_keys = None
map_unrecognized_vals = None
map_vector_keys = None
maps_four_char_keyword_keys = None
maps_four_char_string_keys = None
maps_four_char_sym_keys = None
maps_three_char_keyword_keys = None
maps_three_char_string_keys = None
maps_three_char_sym_keys = None
maps_two_char_keyword_keys = None
maps_two_char_string_keys = None
maps_two_char_sym_keys = None
maps_unrecognized_keys = None
nil = None
one = None
one_date = None
one_keyword = None
one_string = None
one_symbol = None
one_uri = None
one_uuid = None
set_empty = None
set_mixed = None
set_nested = None
set_simple = None
small_ints = None
small_strings = None
strings_hash = None
strings_hat = None
strings_tilde = None
symbols = None
true = None
uris = None
uuids = None
vector_1935_keywords_repeated_twice = None
vector_1936_keywords_repeated_twice = None
vector_1937_keywords_repeated_twice = None
vector_empty = None
vector_mixed = None
vector_nested = None
vector_simple = None
vector_special_numbers = None
vector_unrecognized_vals = None
zero = None

exemplar_files = [
    ExemplarSpec("cmap_null_key", cmap_null_key),
    ExemplarSpec("cmap_pathological", cmap_pathological),
    # ExemplarSpec("dates_interesting", dates_interesting),
    ExemplarSpec("doubles_interesting", doubles_interesting),
    ExemplarSpec("doubles_small", doubles_small),
    # ExemplarSpec("false", false),
    # ExemplarSpec("ints", ints),
    # ExemplarSpec("ints_interesting", ints_interesting),
    # ExemplarSpec("ints_interesting_neg", ints_interesting_neg),
    # ExemplarSpec("keywords", keywords),
    # ExemplarSpec("list_empty", list_empty),
    # ExemplarSpec("list_mixed", list_mixed),
    # ExemplarSpec("list_nested", list_nested),
    # ExemplarSpec("list_simple", list_simple),
    # ExemplarSpec("map_10_items", map_10_items),
    # ExemplarSpec("map_10_nested", map_10_nested),
    # ExemplarSpec("map_1935_nested", map_1935_nested),
    # ExemplarSpec("map_1936_nested", map_1936_nested),
    # ExemplarSpec("map_1937_nested", map_1937_nested),
    # ExemplarSpec("map_mixed", map_mixed),
    # ExemplarSpec("map_nested", map_nested),
    # ExemplarSpec("map_numeric_keys", map_numeric_keys),
    # ExemplarSpec("map_simple", map_simple),
    # ExemplarSpec("map_string_keys", map_string_keys),
    # ExemplarSpec("map_unrecognized_vals", map_unrecognized_vals),
    # ExemplarSpec("map_vector_keys", map_vector_keys),
    # ExemplarSpec("maps_four_char_keyword_keys", maps_four_char_keyword_keys),
    # ExemplarSpec("maps_four_char_string_keys", maps_four_char_string_keys),
    # ExemplarSpec("maps_four_char_sym_keys", maps_four_char_sym_keys),
    # ExemplarSpec("maps_three_char_keyword_keys", maps_three_char_keyword_keys),
    # ExemplarSpec("maps_three_char_string_keys", maps_three_char_string_keys),
    # ExemplarSpec("maps_three_char_sym_keys", maps_three_char_sym_keys),
    # ExemplarSpec("maps_two_char_keyword_keys", maps_two_char_keyword_keys),
    # ExemplarSpec("maps_two_char_string_keys", maps_two_char_string_keys),
    # ExemplarSpec("maps_two_char_sym_keys", maps_two_char_sym_keys),
    # ExemplarSpec("maps_unrecognized_keys", maps_unrecognized_keys),
    # ExemplarSpec("nil", nil),
    # ExemplarSpec("one", one),
    # ExemplarSpec("one_date", one_date),
    # ExemplarSpec("one_keyword", one_keyword),
    # ExemplarSpec("one_string", one_string),
    # ExemplarSpec("one_symbol", one_symbol),
    # ExemplarSpec("one_uri", one_uri),
    # ExemplarSpec("one_uuid", one_uuid),
    # ExemplarSpec("set_empty", set_empty),
    # ExemplarSpec("set_mixed", set_mixed),
    # ExemplarSpec("set_nested", set_nested),
    # ExemplarSpec("set_simple", set_simple),
    # ExemplarSpec("small_ints", small_ints),
    # ExemplarSpec("small_strings", small_strings),
    # ExemplarSpec("strings_hash", strings_hash),
    # ExemplarSpec("strings_hat", strings_hat),
    # ExemplarSpec("strings_tilde", strings_tilde),
    # ExemplarSpec("symbols", symbols),
    # ExemplarSpec("true", true),
    # ExemplarSpec("uris", uris),
    # ExemplarSpec("uuids", uuids),
    # ExemplarSpec("vector_1935_keywords_repeated_twice", vector_1935_keywords_repeated_twice),
    # ExemplarSpec("vector_1936_keywords_repeated_twice", vector_1936_keywords_repeated_twice),
    # ExemplarSpec("vector_1937_keywords_repeated_twice", vector_1937_keywords_repeated_twice),
    # ExemplarSpec("vector_empty", vector_empty),
    # ExemplarSpec("vector_mixed", vector_mixed),
    # ExemplarSpec("vector_nested", vector_nested),
    # ExemplarSpec("vector_simple", vector_simple),
    # ExemplarSpec("vector_special_numbers", vector_special_numbers),
    # ExemplarSpec("vector_unrecognized_vals", vector_unrecognized_vals),
    # ExemplarSpec("zero", zero),
]

reader = TransitReader()

@params(*exemplar_files)
def test_exemplar(spec: ExemplarSpec):
    verbose_file = f"./tests/test_data/simple/{spec.name}.verbose.json"
    verbose_txt = Path(verbose_file).read_text()
    verbose_tree = reader.read(verbose_txt)
    assert verbose_tree == spec.expected, f"verbose: {verbose_tree} did not match {spec.expected}"

    cache_file = verbose_file.replace(".verbose.json", ".json")
    cache_txt = Path(cache_file).read_text()
    cache_tree = reader.read(cache_txt)
    assert cache_tree == spec.expected, f"cache: {cache_tree} did not match {spec.expected}"







