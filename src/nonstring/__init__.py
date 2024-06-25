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


class MergeError(Exception):
    """An error occurred while merging iterable objects."""


X = typing.TypeVar('X')
Y = typing.TypeVar('Y')


def merge(
    these: typing.Iterable[X],
    those: typing.Iterable[Y],
) -> typing.List[typing.Union[X, Y]]:
    """Merge two iterable containers while respecting order.
    
    Parameters
    ----------
    these, those
        The iterable containers to merge.

    Returns
    -------
    `list`
        A list containing the unique members of the arguments, in the order in
        which they would appear after expanding both arguments.

    Raises
    ------
    `ValueError`
        The arguments contain repeated items in different order.
    """
    x = wrap(these)
    y = wrap(those)
    repeated = set(x) & set(y)
    if repeated:
        ab = [i for i in x if i in y]
        ba = [i for i in y if i in x]
        if ab != ba:
            raise MergeError(
                "Repeated entries must appear in the same order"
            ) from None
        s = []
        za = zb = 0
        for v in ab:
            ia = x.index(v)
            ib = y.index(v)
            s.extend(x[za:ia] + y[zb:ib])
            s.append(v)
            za = ia + 1
            zb = ib + 1
        s.extend(x[za:] + y[zb:])
        return s
    x.extend(y)
    return x


def join(x: typing.Iterable[T], c: str='and', /, quoted: bool=False):
    """Join objects as strings, with a conjunction before the final item.
    
    Parameters
    ----------
    x : iterable of `~T`
        The objects to join. This function will convert `x` into a `list` and
        will convert each member of `x` into its string representation.
    
    c : string
        The conjunction to insert before the final item, if `x` contains more
        than one string.

    quoted : bool, default=False
        If true, quote each string in `x`.

    Notes
    -----
    - This function will insert the conjunction as given. It is the user's
      responsibility to pass an appropriate argument.
    - This function implements the `quoted` option by calling `repr` on each
      string in `x`.
    """
    f = repr if quoted else str
    y = list(x)
    if len(y) == 1:
        return f(y[0])
    if len(y) == 2:
        return f"{f(y[0])} {c} {f(y[1])}"
    substr = ', '.join(f(i) for i in y[:-1])
    return f"{substr}, {c} {f(y[-1])}"


def size(x, /) -> int:
    """Compute the size of a potentially nested collection.
    
    Parameters
    ----------
    x
        Any non-string iterable container.

    Notes
    -----
    - The non-string restriction on `x` exists to restrict this function to
      array-like objects (e.g., lists of lists). Such objects are considered
      "separable".

    Raises
    ------
    TypeError
        `x` is not iterable or is not separable

    See Also
    --------
    `~isseparable`
    """
    try:
        iter(x)
    except TypeError as err:
        raise TypeError(
            f"Cannot compute the size of {x}"
        ) from err
    if not isseparable(x):
        raise TypeError(
            f"Argument must be a separable collection, not {type(x)}"
        ) from None
    count = 0
    for y in x:
        try:
            iter(y)
        except TypeError:
            count += 1
        else:
            count += size(y)
    return count


