import collections.abc
import typing


class SeparableTypeError(Exception):
    """The object is not separable."""


T = typing.TypeVar('T')


@typing.overload
def unique(
    arg: typing.List[T],
    *,
    separable: bool=False,
) -> typing.List[T]: ...

@typing.overload
def unique(
    arg: T,
    *,
    separable: typing.Literal[True],
) -> typing.List[T]: ...

@typing.overload
def unique(*args: T, separable: bool=False) -> typing.List[T]: ...

def unique(*args, separable=False):
    """Remove repeated items from `args` while preserving order.
    
    Parameters
    ----------
    *args
        The items to compare.

    separable : bool, default=false
        If false, this function will operate on the object as given. If true,
        and `args` comprises a single iterable object, this function will
        extract that object under the assumption that the caller wants to remove
        repeated items from the given iterable object.
    """
    items = (
        args[0] if (separable and len(args) == 1)
        else args
    )
    try:
        iter(items)
    except TypeError as err:
        raise SeparableTypeError(
            f"Cannot separate object of type {items.__class__.__qualname__!r}"
        ) from err
    collection = []
    for item in items:
        if item not in collection:
            collection.append(item)
    return collection


_Wrapped = typing.TypeVar('_Wrapped', bound=typing.Iterable)


@typing.overload
def unwrap(obj: typing.Union[T, typing.Iterable[T]]) -> T: ...


@typing.overload
def unwrap(
    obj: typing.Union[T, typing.Iterable[T]],
    newtype: typing.Type[_Wrapped]=None,
) -> _Wrapped: ...


def unwrap(obj, newtype=None):
    """Remove redundant outer lists and tuples.

    This function will strip away enclosing instances of `list` or `tuple`, as
    long as they contain a single item, until it finds an object of a different
    type, a `list` or `tuple` containing multiple items, or an empty `list` or
    `tuple`.

    Parameters
    ----------
    obj : Any
        The object to "unwrap".

    newtype : type
        An iterable type into which to store the result. Specifying this allows
        the caller to ensure that the result is an iterable object after
        unwrapping interior iterables.

    Returns
    -------
    Any
        The element enclosed in multiple instances of `list` or `tuple`, or a
        (possibly empty) `list` or `tuple`.
    """
    seed = [obj]
    wrapped = (list, tuple)
    while isinstance(seed, wrapped) and len(seed) == 1:
        seed = seed[0]
    if newtype is not None:
        return newtype(wrap(seed))
    return seed


def wrap(
    arg: typing.Optional[typing.Union[T, typing.Iterable[T]]],
) -> typing.List[T]:
    """Wrap `arg` in a list, if necessary.

    In most cases, this function will try to iterate over `arg`. If that
    operation succeeds, it will simply return `arg`; if the attempt to iterate
    raises a `TypeError`, it will assume that `arg` is a scalar and will return
    a one-element list containing `arg`. If `arg` is `None`, this function will
    return an empty list. If `arg` is a string, this function will return a
    one-element list containing `arg`.
    """
    if arg is None:
        return []
    if isinstance(arg, str):
        return [arg]
    try:
        iter(arg)
    except TypeError:
        return [arg]
    else:
        return list(arg)


class Wrapper(collections.abc.Collection, typing.Generic[T]):
    """A collection of independent members.

    This class represents an iterable collection with members that have meaning
    independent of any other members. When initialized with a "separable" object
    (e.g., a `list`, `tuple`, or `set`), the new instance will behave like the
    equivalent `tuple`. When initialized with a non-"separable" object, the new
    instance will behave like a `tuple` containing that object.

    See Also
    --------
    `~isseparable`
    """

    def __init__(
        self,
        this: typing.Optional[typing.Union[T, typing.Iterable[T]]],
        /,
    ) -> None:
        """Initialize a wrapped object from `this`"""
        self._arg = this
        self._wrapped = tuple(wrap(this))

    def __iter__(self) -> typing.Iterator[T]:
        """Called for iter(self)."""
        return iter(self._wrapped)

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self._wrapped)

    def __contains__(self, __x: object) -> bool:
        """Called for __x in self."""
        return __x in self._wrapped

    def __eq__(self, other) -> bool:
        """True if two wrapped objects have equal arguments."""
        if isinstance(other, Wrapper):
            return sorted(self) == sorted(other)
        return NotImplemented

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return self._arg


def isseparable(x, /):
    """True if `x` is iterable but is not string-like.

    This function identifies iterable collections with members that have meaning
    independent of any other members. For example, a list of numbers is
    "separable" whereas a string is not, despite the fact that both objects are
    iterable collections.

    The motivation for this distinction is to make it easier to treat single
    numbers and strings equivalently to iterables of numbers and strings.
    """
    try:
        iter(x)
    except TypeError:
        return False
    return not isinstance(x, (str, bytes))


