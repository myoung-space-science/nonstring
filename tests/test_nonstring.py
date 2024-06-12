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
        (('a', 'b', 'b', 'a', 'c'),): ['a', 'b', 'c'],
        ((1,),): [1],
        ((1, 2),): [1, 2],
        (1, 2): [1, 2],
        (('a', 'a'), ('b', 'b')): [('a', 'a'), ('b', 'b')],
    }
    for items, expected in cases.items():
        assert list(nonstring.unique(*items)) == expected
    with pytest.raises(TypeError):
        nonstring.unique(1)


def test_unique_strict():
    """Test use of the `strict` keyword argument to `unique`."""
    result = nonstring.unique(['a', 'b', 'a'], strict=True)
    expected = [['a', 'b', 'a']]
    assert result == expected


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


@pytest.mark.xfail
def test_wrap():
    """Test the function that wraps an object in a list."""
    assert False


def test_isseparable():
    """Test the function that identifies non-string iterables."""
    separables = [[1, 2], (1, 2), range(1, 3)]
    for arg in separables:
        assert nonstring.isseparable(arg)
    nonseparables = ['a', '1, 2', 1, 1.0, slice(None), slice(1)]
    for arg in nonseparables:
        assert not nonstring.isseparable(arg)


