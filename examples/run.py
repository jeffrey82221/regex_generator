import re
from random_regex import RegexGenerator

regex_generator = RegexGenerator().generate()


def assert_all_match(examples, regex):
    re_com = re.compile(regex)
    for ex in examples:
        assert re_com.fullmatch(ex) is not None


for i, instance in enumerate(regex_generator):

    regex = instance['regex']
    complexity = instance['complexity']
    length = instance['length']
    examples = instance['examples']
    re.compile(regex)
    assert len(regex) == length
    assert len(examples) == complexity
    assert_all_match(examples, regex)
    print(regex)
    if i > 1000:
        break
