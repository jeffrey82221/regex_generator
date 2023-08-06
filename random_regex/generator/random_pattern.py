import typing
import random
import string
from regexfactory.pattern import escape, join
from regexfactory.pattern import RegexPattern
# TODO: [X] consider random special characters
from regexfactory.chars import (
    ANY,
    WHITESPACE,
    NOTWHITESPACE,
    WORD,
    NOTWORD,
    DIGIT,
    NOTDIGIT,
    # Currently, we don't consider the start/end anchor because we only do fullmatch.
    # ANCHOR_START, ANCHOR_END
)
from regexfactory.patterns import (
    # TODO: [X] Operators for matching single char:
    Range,
    Set,
    NotSet,
    # TODO: [X] Operators for long string
    Group,
    Or,
    # TODO: [X] Work on character level (need to wrap input into Group in
    # order to
    Amount,
    Multi,
    Optional
    # Commet -> no effect
)

__all__ = ['PatternGenerator']

PRINTABLES: typing.List[str] = []
PRINTABLES.extend(string.ascii_letters)
PRINTABLES.extend(string.digits)
PRINTABLES.extend(string.hexdigits)
PRINTABLES.extend(string.octdigits)
PRINTABLES.extend(string.punctuation)


class Wrapper:
    """
    Warp pattern by Amount, Multi, Optional
    """
    @staticmethod
    def wrap_into_limit_amount(pattern: RegexPattern,
                               amount_complexity: int) -> Amount:
        """
        For wraping a pattern into multiple amount pattern
        (only support limited repeativeness)
        """
        lower_bound = random.randint(0, amount_complexity)
        if random.uniform(0, 1) < 0.5:
            # fix amount
            return Amount(pattern, lower_bound, j=None, or_more=False)
        else:
            # amount of a range
            upper_bound = lower_bound + random.randint(0, amount_complexity)
            return Amount(pattern, lower_bound, j=upper_bound, or_more=False)

    @staticmethod
    def __wrap_into_amount(pattern: RegexPattern,
                           amount_complexity: int) -> Amount:
        if random.uniform(0, 1) < 0.25:
            or_more = True
        else:
            or_more = False
        lower_bound = random.randint(0, amount_complexity)
        if random.uniform(0, 1) < 0.25:
            # no upper bound
            return Amount(pattern, lower_bound, j=None, or_more=or_more)
        else:
            # with upper bound
            upper_bound = lower_bound + random.randint(0, amount_complexity)
            return Amount(pattern, lower_bound, j=upper_bound, or_more=or_more)

    @staticmethod
    def __wrap_into_multi(pattern: RegexPattern) -> Multi:
        if random.uniform(0, 1) < 0.5:
            return Multi(pattern, match_zero=True)
        else:
            return Multi(pattern, match_zero=False)


class CharGenerator:
    """
    Char-level RegexPattern Generator
    """
    special_chars_without_any = [
        WHITESPACE,
        NOTWHITESPACE,
        WORD,
        NOTWORD,
        DIGIT,
        NOTDIGIT
    ]
    printable_escapes = [escape(x) for x in PRINTABLES]

    def __init__(self, set_complexity: int, amount_complexity: int,
                 special_char_prob: float = 0.5, complex_char_prob: float = 0.5):
        assert isinstance(
            set_complexity, int) and set_complexity > 0, 'set complexity should be > 0'
        assert isinstance(
            amount_complexity, int) and amount_complexity > 0, 'amount complexity should be > 0'
        assert isinstance(
            special_char_prob, float) and special_char_prob >= 0.0 and special_char_prob <= 1.0, 'special_char_prob should be a float in range [0, 1]'
        assert isinstance(
            complex_char_prob, float) and complex_char_prob >= 0.0 and complex_char_prob <= 1.0, 'complex_char_prob should be a float in range [0, 1]'
        self._set_complexity = set_complexity
        self._amount_complexity = amount_complexity
        self._special_char_prob = special_char_prob
        self._complex_char_prob = complex_char_prob

    def get_random_chars(self, length: int) -> typing.List[RegexPattern]:
        """
        Generate a List of single char regex pattern
        with repeat select
        """
        result = [self._get_random_char() for _ in range(length)]
        return result

    def _get_random_char(self):
        """
        random select from simple char or complex char
        with complex_char_probabilty

        complex char:

        1) char wrapped by Amount

        2) char wrapped by Optional

        simple char:

        char with fix count = 1

        if x < p:
            complex char -> more complicated
        else:
            simple char
        """
        if random.uniform(0, 1) < self._complex_char_prob:
            if random.uniform(0, 1) < 0.5:
                return self._get_random_amount()
            else:
                return self._get_random_simple_char()
        else:
            return self._get_random_simple_char()

    def _get_random_amount(self) -> Amount:
        """
        warp _get_random_simple_char into Amount
        """
        char = self._get_random_simple_char()
        amount_char = Wrapper.wrap_into_limit_amount(
            char, self._amount_complexity)
        return amount_char

    def _get_random_simple_char(self) -> RegexPattern:
        """
        select by special char probability

        special:
        - in special chars 1/3
        - random range 1/3
        - random set 1/3
        if x < p:
            special char -> more complicated
        else:
            printable char
        """
        if random.uniform(0, 1) < self._special_char_prob:
            p = random.uniform(0, 1)
            if p <= 0.333:
                return CharGenerator._get_random_plain_special_char()
            elif p <= 0.666:
                return CharGenerator._get_random_range()
            else:
                return self._get_random_set()
        else:
            return CharGenerator._get_random_printables()

    @staticmethod
    def _get_random_plain_special_char() -> RegexPattern:
        return random.choice(CharGenerator.special_chars_without_any + [ANY])

    @staticmethod
    def _get_random_range() -> Range:
        """
        Generate a random regex Range pattern
        [s-e], where s and e are some printable chars
        """
        chars = random.choices(string.printable, k=2)
        if ord(chars[0]) <= ord(chars[1]):
            return Range(escape(chars[0]), escape(chars[1]))
        else:
            return Range(escape(chars[1]), escape(chars[0]))

    def _get_random_set(self) -> typing.Union[Set, NotSet]:
        """
        Generate a random Set/NotSet pattern.
        NOTE that Any (.) is not a special character in set. Hence, it is excluded.
        """
        count = random.randint(1, self._set_complexity)
        chars = CharGenerator.__get_random_non_repeating_chars(count)
        pattern = join(*chars)
        if random.uniform(0, 1) < 0.5:
            return Set(pattern)
        else:
            return NotSet(pattern)

    @staticmethod
    def __get_random_non_repeating_chars(
            count: int) -> typing.List[RegexPattern]:
        """
        Generate a list of single char regex pattern
        without repeat select
        """
        candidates = CharGenerator.special_chars_without_any + \
            CharGenerator.printable_escapes
        try:
            result = random.sample(candidates, count)
        except ValueError:
            result = CharGenerator.printable_escapes
        while (
            (WHITESPACE in result) and (NOTWHITESPACE in result)
        ) or (
            (WORD in result) and (NOTWORD in result)
        ) or (
            (DIGIT in result) and (NOTDIGIT in result)
        ):
            result = random.sample(candidates, count)
        result = sorted(result, key=lambda x: x.regex)
        return result

    @ staticmethod
    def _get_random_printables() -> RegexPattern:
        return random.choice(CharGenerator.printable_escapes)


class PatternGenerator:
    """
    Generate Random Groups wrapped by following things:

    TODO:
    - [X] Group,
    - [X] Or,
    - [X] Amount, # Work on character level (need to wrap input into Group in order to become string-level)
    - [X] Multi,
    - [X] Optional
    """

    def __init__(self, set_complexity: int, union_complexity: int, amount_complexity: int,
                 group_complexity: int, depth_complexity: int, breadth_complexity: int,
                 special_char_prob: float = 0.5, complex_char_prob: float = 0.5, complex_group_prob: float = 0.5):
        assert breadth_complexity >= 1, 'breadth complexity should be larger than 1'
        assert set_complexity >= 1, 'set complexity should be larger than 1'
        assert isinstance(
            complex_group_prob, float) and complex_group_prob >= 0.0 and complex_group_prob <= 1.0, 'complex_group_prob should be a float in range [0, 1]'
        self._set_complexity = set_complexity
        self._union_complexity = union_complexity
        self._amount_complexity = amount_complexity
        self._group_complexity = group_complexity
        self._depth_complexity = depth_complexity
        self._breadth_complexity = breadth_complexity
        self._complex_group_prob = complex_group_prob
        self.__char_generator = CharGenerator(
            set_complexity,
            amount_complexity,
            special_char_prob=special_char_prob,
            complex_char_prob=complex_char_prob
        )

    def get_random_pattern(self, recurse: int = 0) -> RegexPattern:
        """
        Generate random pattern
        """
        group_count = random.randint(1, self._breadth_complexity)
        groups = self.get_random_groups(group_count, recurse=recurse)
        pattern = join(*groups)
        return pattern

    def get_random_groups(self, group_count: int,
                          recurse: int = 0) -> typing.List[Group]:
        """
        Generate random group pattern that includes Or/Amount/Multi/Optional patterns
        """
        candidates: typing.List[Group] = []
        weights = []
        while len(candidates) < group_count:
            group = self._get_random_group_pattern(recurse=recurse)
            candidates.append(group)
            weights.append(1. - self._complex_group_prob)
            # 1) Or-wrapped groups
            candidates.append(self._get_random_union_groups(recurse=recurse))
            # 2) Limited-Amount-wrapped groups
            candidates.append(
                Group(
                    Wrapper.wrap_into_limit_amount(
                        group,
                        self._amount_complexity)))
            # candidates.append(Group(Wrapper.wrap_into_multi(group)))
            # 3) Optional-wrapped groups
            candidates.append(Group(Optional(group)))
            weights.extend([self._complex_group_prob / 3.] * 3)
        return random.choices(candidates, k=group_count,
                              weights=tuple(weights))

    def _get_random_union_groups(self, recurse: int = 0) -> Group:
        """
        Get random Or-wrapped group patterns
        """
        group_count = random.randint(0, self._union_complexity)
        groups = self._get_random_groups(group_count, recurse=recurse)
        return Group(Or(*groups))

    def _get_random_groups(self, group_count: int,
                           recurse: int = 0) -> typing.List[Group]:
        groups = []
        for _ in range(group_count):
            group = self._get_random_group_pattern(recurse=recurse)
            groups.append(group)
        return groups

    def _get_random_group_pattern(self, recurse: int = 0) -> Group:
        """
        A string mixing normal chars with special chars
        """
        if recurse > self._depth_complexity:
            length = random.randint(0, self._group_complexity)
            return Group(
                join(*self.__char_generator.get_random_chars(length)))
        else:
            return Group(self.get_random_pattern(recurse=recurse + 1))
