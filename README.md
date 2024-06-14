# Nonstring Collections

This package provides utilities for working with non-string iterable containers.

## Module Functions

### `unique`

This function will remove repeated items from arguments while preserving order.

```python
>>> from nonstring import unique
>>> unique(1, 2, 3, 2, 3, 3, 1, 4, 2, 5, 5)
[1, 2, 3, 4, 5]
>>> unique(5, 5, 2, 4, 1, 3, 3, 2, 3, 2, 1)
[5, 2, 4, 1, 3]
```

It will treat a single argument as atomic (i.e., unseparable) unless the
`separable` keyword is set to true.

```python
>>> unique('aabac')
['aabac']
>>> unique('aabac', separable=True)
['a', 'b', 'c']
```

### `unwrap`

This function will remove redundant outer lists and tuples.

It can unwrap numbers enclosed in increasingly deeper lists:

```python
>>> from nonstring import unwrap
>>> cases = [[1], [[2]], [[[3]]], [[[[4]]]]]
>>> for case in cases:
...     print(unwrap(case))
... 
1
2
3
4
```

It preserves numbers and strings that are already unwrapped:

```python
>>> unwrap(42)
42
>>> unwrap('string')
'string'
```

Passing a type to `newtype` ensures a result of that type:

```python
>>> unwrap(42, newtype=tuple)
(42,)
>>> unwrap(42, newtype=list)
[42]
>>> unwrap([42], newtype=list)
[42]
>>> unwrap(([(42,)],), newtype=list)
[42]
```

It works with multiple wrapped elements:

```python
>>> unwrap([1, 2])
[1, 2]
>>> unwrap([[1, 2]])
[1, 2]
>>> unwrap(['one', 'two'])
['one', 'two']
>>> unwrap([['one', 'two']])
['one', 'two']
```

It stops at an empty `list` or `tuple`:

```python
>>> unwrap([])
[]
>>> unwrap(())
()
>>> unwrap(list())
[]
>>> unwrap(tuple())
()
>>> unwrap([[]])
[]
>>> unwrap([()])
()
>>> unwrap([], newtype=tuple)
()
```

### `wrap`

This function will wrap the argument in a list, if necessary.

```python
>>> from nonstring import wrap
>>> wrap(1)
[1]
>>> wrap([1])
[1]
>>> wrap((1,))
[1]
>>> wrap([[1]])
[[1]]
```

### `isseparable`

This function will return `True` if the argument is iterable but is not string-like.

```python
>>> from nonstring import isseparable
>>> isseparable('ab')
False
>>> isseparable(['a', 'b'])
True
```

## Wrapper

An instance of this class represents an iterable collection with members that
have meaning independent of any other members. When initialized with a
"separable" object (e.g., a `list`, `tuple`, or `set`), the new instance will
behave like the equivalent `tuple`. When initialized with a non-"separable"
object, the new instance will behave like a `tuple` containing that object.

