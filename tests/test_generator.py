import re
from regex_generator import RegexGenerator


def assert_all_match(examples, regex):
    re_com = re.compile(regex)
    for ex in examples:
        assert re_com.fullmatch(ex) is not None


def test_generate():
    regex_generator = RegexGenerator().generate()
    instance = next(regex_generator)
    regex = instance['regex']
    complexity = instance['complexity']
    length = instance['length']
    examples = instance['examples']
    re.compile(regex)
    assert len(regex) == length
    assert len(examples) == complexity
    assert_all_match(examples, regex)
