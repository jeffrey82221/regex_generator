import re
from random_regex import RegexGenerator


def test_generate():
    regex_generator = RegexGenerator(bloom_max_item_count=10).generate()
    instance = next(regex_generator)
    regex = instance['regex']
    complexity = instance['complexity']
    length = instance['length']
    examples = instance['examples']
    re_com = re.compile(regex)
    assert len(regex) == length
    assert len(examples) == complexity
    for ex in examples:
        assert re_com.fullmatch(ex) is not None
