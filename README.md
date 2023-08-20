# regex_generator
Generate Random Regex

# Install 

```bash
pip install random-regex
```


# Usage


```python
import re
from random_regex import RegexGenerator
from rbloom import Bloom # This is a faster bloom filter implemented in rust.s
regex_generator = RegexGenerator(bloom_cls=Bloom).generate()


def assert_all_match(examples, regex):
    re_com = re.compile(regex)
    for ex in examples:
        assert re_com.fullmatch(ex) is not None


for i, instance in enumerate(regex_generator):
    if i > 1000:
        break
    regex = instance['regex']
    complexity = instance['complexity']
    length = instance['length']
    examples = instance['examples']
    re.compile(regex)
    assert len(regex) == length
    assert len(examples) == complexity
    assert_all_match(examples, regex)
    print(regex)
```
>>
```
((?:(([\s]C\s))))
((\sR2{1,3}\+[m]))
((3{1}[\(-y]a\[))
((\d{1,1}[^08]1A))
(([3-c]))
(([^Rp][CJ]f))
(((G[/]){4,7}))
((.))
(((?:(D2[Qh]))?))
(((!\s)){3})
(([9d])([9d]))
((\s))((\s))
((\d))
((a\s)(a\s)(a\s))
...
```