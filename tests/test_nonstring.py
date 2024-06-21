import typing

import pytest

import nonstring


def test_unique():
    """Test the function that extracts unique items while preserving order."""
    cases = {
        'a': ['a'],
        (1, 2): [1, 2],
        'ab': ['a', 'b'],
        ('a', 'b'): ['a', 'b'],
        ('a', 'b', 'a'): ['a', 'b'],
        ('a', 'b', 'a', 'c'): ['a', 'b', 'c'],
        ('a', 'b', 'b', 'a', 'c'): ['a', 'b', 'c'],
        (1, 2): [1, 2],
        (('a', 'a'), ('b', 'b')): [('a', 'a'), ('b', 'b')],
    }
    for items, expected in cases.items():
        assert list(nonstring.unique(*items)) == expected
    assert nonstring.unique(1) == [1]


def test_unique_separable():
    """Test use of the `separable` keyword argument to `unique`."""
    cases = {
        'aabac': ['a', 'b', 'c'],
        ('a', 'b', 'a'): ['a', 'b'],
        ('a', 'b', 'b', 'a', 'c'): ['a', 'b', 'c'],
        (1,): [1],
        (1, 2): [1, 2],
    }
    for arg, iftrue in cases.items():
        assert nonstring.unique(arg) == [arg]
        assert nonstring.unique(arg, separable=True) == iftrue
    with pytest.raises(nonstring.SeparableTypeError):
        nonstring.unique(1, separable=True)


def test_unwrap():
    """Test the function that removes certain outer sequence types."""
    cases = [[3], (3,), [[3]], [(3,)], ([3],), ((3,),)]
    for case in cases:
        assert nonstring.unwrap(case) == 3
    for case in [[3], [[3]], (3,), [(3,)]]:
        assert nonstring.unwrap(case, newtype=list) == [3]
        assert nonstring.unwrap(case, newtype=tuple) == (3,)
        assert isinstance(
            nonstring.unwrap(case, newtype=iter),
            typing.Iterator
        )
    for case in [[3, 4], (3, 4), [(3, 4)], ([3, 4])]:
        assert nonstring.unwrap(case, newtype=list) == [3, 4]
        assert nonstring.unwrap(case, newtype=tuple) == (3, 4)


def test_wrap():
    """Test the function that wraps an object in a list."""
    assert nonstring.wrap(1) == [1]
    assert nonstring.wrap([1]) == [1]


def test_isseparable():
    """Test the function that identifies non-string iterables."""
    separables = [[1, 2], (1, 2), range(1, 3)]
    for arg in separables:
        assert nonstring.isseparable(arg)
    nonseparables = ['a', '1, 2', 1, 1.0, slice(None), slice(1)]
    for arg in nonseparables:
        assert not nonstring.isseparable(arg)


def test_merge():
    """Test the order-preserving merge function."""
    valid = [
        [['a', 'b'], ['x', 'y'], ['a', 'b', 'x', 'y']],
        [['x', 'y', 'z'], ['x', 'y', 'z'], ['x', 'y', 'z']],
        [['x', 'y', 'z'], ['x', 'y'], ['x', 'y', 'z']],
        [['x', 'y', 'z'], ['y', 'z'], ['x', 'y', 'z']],
        [['x', 'y', 'z'], ['x', 'z'], ['x', 'y', 'z']],
        [['y', 'z'], ['x', 'y', 'z'], ['x', 'y', 'z']],
        [['y', 'z'], ['z', 'w'], ['y', 'z', 'w']],
        [['x', 'y', 'z'], ['y', 'z', 'w'], ['x', 'y', 'z', 'w']],
        [
            ['x', 'y', 'z', 'w', 'r'],
            ['a', 'x', 'b', 'c', 'y', 'w'],
            ['a', 'x', 'b', 'c', 'y', 'z', 'w', 'r'],
        ],
        [
            ['a', 'x', 'b', 't', 'y', 'c', 'z'],
            ['a', 'q', 'x', 'q', 'p', 'c', 'r'],
            ['a', 'q', 'x', 'b', 't', 'y', 'q', 'p', 'c', 'z', 'r'],
        ],
        [
            ['a', 'q', 'x', 'q', 'p', 'c', 'r'],
            ['a', 'x', 'b', 't', 'y', 'c', 'z'],
            ['a', 'q', 'x', 'q', 'p', 'b', 't', 'y', 'c', 'r', 'z'],
        ],
        ['abc', 'abd', ['abc', 'abd']],
        [['abc'], 'abd', ['abc', 'abd']],
        ['abc', ['abd'], ['abc', 'abd']],
        [['abc'], ['abd'], ['abc', 'abd']],
        [list('abc'), list('abd'), ['a', 'b', 'c', 'd']],
    ]
    for these, those, expected in valid:
        assert nonstring.merge(these, those) == expected
    invalid = [
        [['a', 'b', 'c'], ['a', 'c', 'b']],
        [['a', 'c', 'b'], ['a', 'b', 'c']],
    ]
    for these, those in invalid:
        with pytest.raises(nonstring.MergeError):
            nonstring.merge(these, those)


def test_join():
    """Test the custom string-joining function."""
    assert nonstring.join(['a']) == 'a'
    assert nonstring.join(['a', 'b']) == 'a and b'
    assert nonstring.join(['a', 'b'], 'or') == 'a or b'
    assert nonstring.join(['a', 'b', 'c']) == 'a, b, and c'
    assert nonstring.join(['a', 'b', 'c'], 'or') == 'a, b, or c'
    assert nonstring.join(['a', 'b', 'c'], quoted=True) == "'a', 'b', and 'c'"


