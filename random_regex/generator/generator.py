"""
Random FullMatch Regex Generator

NOTE:
regex for fullmatching is simpler than that for search or match

TODO:
- [X] use cuckoo filter to ignore repeat regex
- [X] generate multiple examples with length > 0
- [ ] add selection weight to different kind of special character
- [ ] speed up the generation using multi-processing

REF:
https://regex-generator.olafneumann.org/
"""
import exrex
import re
from toolz import curried
from toolz.functoolz import pipe
from .random_pattern import PatternGenerator


class RegexGenerator:
    """
    Generating random regex,
    its complexity, length, and examples
    """

    def __init__(self, max_complexity=1000, max_length=20,
                 item_count=100, bloom_fpr=0.001, bloom_cls=None):
        self._max_complexity = max_complexity
        self._max_length = max_length
        self._pattern_generator = PatternGenerator(
            **self.initial_complexities
        )
        if bloom_cls is None:
            from pybloom import ScalableBloomFilter
            self._bloom = ScalableBloomFilter(item_count, bloom_fpr)
        else:
            self._bloom = bloom_cls(item_count, bloom_fpr)

    @property
    def initial_complexities(self) -> dict:
        """
        Detail complexity parameters of
        the regex pattern generator
        """
        return {
            'set_complexity': 2,
            'union_complexity': 2,
            'amount_complexity': 4,
            'group_complexity': 10,
            'depth_complexity': 0,
            'breadth_complexity': 3,
            'special_char_prob': 0.5,
            'complex_char_prob': 0.5,
            'complex_group_prob': 0.5
        }

    def generate(self):
        """
        Generating non-repeating complexity-in-ranged random regex,
        as well as its complexity, length, and examples
        """
        return pipe(
            self.regex_producer(),
            self._complexity_filter,
            self._validity_filter,
            self._filter_repeat,
        )

    def regex_producer(self):
        """
        Generate regex and its complexity and length
        """
        return pipe(self._regex_producer(),
                    curried.map(lambda rp: {
                        'regex': rp.regex,
                        'complexity': exrex.count(rp.regex),
                        'length': len(rp.regex)
                    }))

    def _complexity_filter(self, x):
        """
        Filter regex by its complexity and length
        """
        return pipe(x,
                    curried.filter(
                        lambda x: x['complexity'] > 2 and x['complexity'] < self._max_complexity),
                    curried.filter(lambda x: x['length'] >=
                                   1 and x['length'] < self._max_length),
                    )

    def _validity_filter(self, x):
        """
        Filter the regex by the validity of generated examples
        """
        return pipe(x,
                    curried.filter(lambda x: self._can_fullmatch(x['regex'])),
                    curried.map(self._add_examples),
                    curried.filter(lambda x: isinstance(x['examples'], list)),
                    curried.filter(
                        lambda x: len(
                            x['examples']) == x['complexity']),
                    curried.filter(self._all_examples_fullmatch),
                    )

    def _regex_producer(self):
        """
        Generate random regex from the pattern generator
        """
        while True:
            yield self._pattern_generator.get_random_pattern()

    def _can_fullmatch(self, regex_str: str) -> bool:
        """
        Assert fullmatching is possible
        """
        example = exrex.getone(regex_str)
        return bool(re.compile(regex_str).fullmatch(example))

    def _add_example(self, result: dict) -> dict:
        """
        Add one single example
        """
        result['example'] = exrex.getone(result['regex'])
        while not bool(re.compile(
                result['regex']).fullmatch(result['example'])):
            result['example'] = exrex.getone(result['regex'])
        return result

    def _add_examples(self, result):
        """
        Generating of multiple examples
        """
        regex = result['regex']
        try:
            examples = []
            for example in exrex.generate(regex):
                examples.append(example)
            result['examples'] = examples
            return result
        except TypeError as e:
            if e.args[0] == 'can only concatenate list (not "str") to list':
                result['examples'] = None
                return result
            elif e.args[0] == 'can only concatenate str (not "list") to str':
                result['examples'] = None
                return result
            else:
                raise e

    def _all_examples_fullmatch(self, result: dict) -> bool:
        """
        Check whether all examples fullmatch the regex
        """
        com = re.compile(result['regex'])
        answers = []
        for example in result['examples']:
            try:
                ans = bool(com.fullmatch(example))
            except TypeError as e:
                if e.args[0] == 'expected string or bytes-like object':
                    return False
                else:
                    raise e
            answers.append(ans)
        return all(answers)

    def _filter_repeat(self, iterable):
        """
        Filter out the repeated regex pattern
        """
        for x in iterable:
            if x['regex'] not in self._bloom:
                yield x
                self._bloom.add(x['regex'])
