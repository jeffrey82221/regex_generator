import re
from random_regex import RegexGenerator
import pickle
import os
import pytest


@pytest.fixture
def bloom_cls():
    import rbloom
    import pybloom
    import bloom_filter
    import bloom_filter2
    return {
        'rbloom': rbloom.Bloom,
        'pybloom': pybloom.BloomFilter,
        'pybloom-scalable': pybloom.ScalableBloomFilter,
        'bloom-filter': bloom_filter.BloomFilter,
        'bloom-filter2': bloom_filter2.BloomFilter,
    }


def test_generate(bloom_cls):
    for bloom in bloom_cls.values():
        regex_generator = RegexGenerator(bloom_cls=bloom).generate()
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


def test_pickle(bloom_cls):
    for key, value in bloom_cls.items():
        if key == 'rbloom':
            continue
        regex_generator = RegexGenerator(bloom_cls=value)
        with open('regex_generator.pkl', 'wb') as f:
            pickle.dump(regex_generator, f)
    os.remove('regex_generator.pkl')
