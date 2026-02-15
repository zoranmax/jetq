"""Main Queryable class implementing LINQ operators."""

from collections import defaultdict
from functools import reduce
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    from .query_provider import QueryProvider

T = TypeVar("T")
TKey = TypeVar("TKey")
TValue = TypeVar("TValue")
TResult = TypeVar("TResult")
TInner = TypeVar("TInner")
TOuter = TypeVar("TOuter")

Selector = Callable[[T], TResult]
Predicate = Callable[[T], bool]
KeySelector = Callable[[T], TKey]
Aggregator = Callable[[TResult, T], TResult]


class OrderedQueryable(Generic[T]):
    """A queryable that maintains ordering information for secondary sorts."""

    def __init__(
        self, source: "Queryable[T]", orderings: List[Tuple[KeySelector, bool]]
    ):
        self.source = source
        self.orderings = orderings  # List of (key_selector, is_descending)

    def _execute_sort(self, items: List[T]) -> List[T]:
        """Apply all orderings to the items."""
        for key_selector, is_descending in reversed(self.orderings):
            items.sort(key=key_selector, reverse=is_descending)
        return items

    def __iter__(self) -> Iterator[T]:
        """Iterate over sorted items."""
        items = list(self.source)
        yield from self._execute_sort(items)

    def then_by(self, key_selector: KeySelector[T, Any]) -> "OrderedQueryable[T]":
        """Add a secondary ascending sort."""
        self.orderings.append((key_selector, False))
        return self

    def then_by_descending(
        self, key_selector: KeySelector[T, Any]
    ) -> "OrderedQueryable[T]":
        """Add a secondary descending sort."""
        self.orderings.append((key_selector, True))
        return self

    # Delegate other methods to Queryable
    def where(self, predicate: Predicate[T]) -> "Queryable[T]":
        """Filter elements."""
        return Queryable(self).where(predicate)

    def select(self, selector: Selector[T, TResult]) -> "Queryable[TResult]":
        """Project elements."""
        return Queryable(self).select(selector)

    def to_list(self) -> List[T]:
        """Convert to list."""
        return list(self)

    def to_dict(self, key_selector: KeySelector[T, Any]) -> Dict[Any, T]:
        """Convert to dictionary."""
        return {key_selector(item): item for item in self}

    def count(self, predicate: Optional[Predicate[T]] = None) -> int:
        """Count elements."""
        if predicate is None:
            return sum(1 for _ in self)
        return sum(1 for item in self if predicate(item))


class Queryable(Generic[T]):
    """Main LINQ query class for chaining query operations."""

    def __init__(self, source: Iterable[T], provider: Optional[Any] = None):
        """Initialize a Queryable.

        Args:
            source: The data source to query.
            provider: The query provider (optional, uses default if not provided).
        """
        self.source = source
        self.provider = provider or self._get_default_provider()

    @staticmethod
    def _get_default_provider() -> "QueryProvider":
        """Get the default query provider."""
        from .query_provider import QueryProvider

        return QueryProvider()

    def __iter__(self) -> Iterator[T]:
        """Make the queryable iterable."""
        if isinstance(self.source, Queryable):
            yield from iter(self.source)
        else:
            yield from iter(self.source)

    # ==================== Filtering ====================

    def where(self, predicate: Predicate[T]) -> "Queryable[T]":
        """Filter elements based on a predicate.

        Args:
            predicate: Function that returns True for elements to keep.

        Returns:
            A new Queryable with filtered elements.
        """
        return Queryable(item for item in self if predicate(item))

    def distinct(
        self, key_selector: Optional[KeySelector[T, Any]] = None
    ) -> "Queryable[T]":
        """Remove duplicate elements.

        Args:
            key_selector: Optional function to determine uniqueness.
            If None, uses element equality.

        Returns:
            A new Queryable with unique elements.
        """

        def distinct_generator():
            seen = set()
            for item in self:
                key = key_selector(item) if key_selector else item
                if key not in seen:
                    seen.add(key)
                    yield item

        return Queryable(distinct_generator())

    def skip(self, count: int) -> "Queryable[T]":
        """Skip the first N elements.

        Args:
            count: Number of elements to skip.

        Returns:
            A new Queryable with skipped elements.
        """
        return Queryable((item for i, item in enumerate(self) if i >= count))

    def take(self, count: int) -> "Queryable[T]":
        """Take the first N elements.

        Args:
            count: Number of elements to take.

        Returns:
            A new Queryable with limited elements.
        """

        def take_generator():
            for i, item in enumerate(self):
                if i >= count:
                    break
                yield item

        return Queryable(take_generator())

    def skip_while(self, predicate: Predicate[T]) -> "Queryable[T]":
        """Skip elements while predicate is true.

        Args:
            predicate: Function to test elements.

        Returns:
            A new Queryable with skipped elements.
        """

        def skip_while_generator():
            skipping = True
            for item in self:
                if skipping and predicate(item):
                    continue
                skipping = False
                yield item

        return Queryable(skip_while_generator())

    def take_while(self, predicate: Predicate[T]) -> "Queryable[T]":
        """Take elements while predicate is true.

        Args:
            predicate: Function to test elements.

        Returns:
            A new Queryable with limited elements.
        """

        def take_while_generator():
            for item in self:
                if not predicate(item):
                    break
                yield item

        return Queryable(take_while_generator())

    # ==================== Projection ====================

    def select(self, selector: Selector[T, TResult]) -> "Queryable[TResult]":
        """Project each element to a new form.

        Args:
            selector: Function to transform each element.

        Returns:
            A new Queryable with projected elements.
        """
        return Queryable(selector(item) for item in self)

    def select_many(
        self, selector: Callable[[T], Iterable[TResult]]
    ) -> "Queryable[TResult]":
        """Project each element to an iterable and flatten the result.

        Args:
            selector: Function that returns an iterable for each element.

        Returns:
            A new Queryable with flattened elements.
        """
        return Queryable(chain.from_iterable(selector(item) for item in self))

    def cast(self, target_type: type) -> "Queryable[T]":
        """Cast each element to a target type.

        Args:
            target_type: The type to cast to.

        Returns:
            A new Queryable with casted elements.
        """
        return Queryable(target_type(item) for item in self)

    # ==================== Ordering ====================

    def order_by(self, key_selector: KeySelector[T, Any]) -> OrderedQueryable[T]:
        """Sort elements in ascending order.

        Args:
            key_selector: Function to extract sort key from each element.

        Returns:
            An OrderedQueryable that can be further sorted with then_by().
        """
        return OrderedQueryable(self, [(key_selector, False)])

    def order_by_descending(
        self, key_selector: KeySelector[T, Any]
    ) -> OrderedQueryable[T]:
        """Sort elements in descending order.

        Args:
            key_selector: Function to extract sort key from each element.

        Returns:
            An OrderedQueryable that can be further sorted with then_by().
        """
        return OrderedQueryable(self, [(key_selector, True)])

    def reverse(self) -> "Queryable[T]":
        """Reverse the order of elements.

        Returns:
            A new Queryable with reversed elements.
        """
        return Queryable(reversed(list(self)))

    # ==================== Grouping ====================

    def group_by(
        self, key_selector: KeySelector[T, TKey]
    ) -> "Queryable[GroupingResult[TKey, T]]":
        """Group elements by key.

        Args:
            key_selector: Function to extract grouping key from each element.

        Returns:
            A new Queryable of GroupingResult objects.
        """
        groups = defaultdict(list)
        for item in self:
            key = key_selector(item)
            groups[key].append(item)

        from .types import GroupingResult

        return Queryable([GroupingResult(key, items) for key, items in groups.items()])

    # ==================== Joining ====================

    def join(
        self,
        inner: Iterable[TInner],
        outer_key_selector: KeySelector[T, Any],
        inner_key_selector: KeySelector[TInner, Any],
        result_selector: Callable[[T, TInner], TResult],
    ) -> "Queryable[TResult]":
        """Join two sequences on matching keys.

        Args:
            inner: The inner sequence to join with.
            outer_key_selector: Function to extract join key from outer elements.
            inner_key_selector: Function to extract join key from inner elements.
            result_selector: Function to create result from matched pairs.

        Returns:
            A new Queryable with joined results.
        """
        inner_list = list(inner)
        inner_dict = defaultdict(list)
        for item in inner_list:
            key = inner_key_selector(item)
            inner_dict[key].append(item)

        result = []
        for outer_item in self:
            key = outer_key_selector(outer_item)
            for inner_item in inner_dict[key]:
                result.append(result_selector(outer_item, inner_item))

        return Queryable(result)

    def group_join(
        self,
        inner: Iterable[TInner],
        outer_key_selector: KeySelector[T, Any],
        inner_key_selector: KeySelector[TInner, Any],
        result_selector: Callable[[T, List[TInner]], TResult],
    ) -> "Queryable[TResult]":
        """Join two sequences and group the inner results.

        Args:
            inner: The inner sequence to join with.
            outer_key_selector: Function to extract join key from outer elements.
            inner_key_selector: Function to extract join key from inner elements.
            result_selector: Function to create result from outer element and grouped inner elements.

        Returns:
            A new Queryable with grouped join results.
        """
        inner_list = list(inner)
        inner_dict = defaultdict(list)
        for item in inner_list:
            key = inner_key_selector(item)
            inner_dict[key].append(item)

        result = []
        for outer_item in self:
            key = outer_key_selector(outer_item)
            inner_group = inner_dict[key]
            result.append(result_selector(outer_item, inner_group))

        return Queryable(result)

    # ==================== Aggregation ====================

    def count(self, predicate: Optional[Predicate[T]] = None) -> int:
        """Count the number of elements.

        Args:
            predicate: Optional function to count only matching elements.

        Returns:
            The count of elements.
        """
        if predicate is None:
            return sum(1 for _ in self)
        return sum(1 for item in self if predicate(item))

    def sum(
        self, selector: Optional[Selector[T, Union[int, float]]] = None
    ) -> Union[int, float]:
        """Sum elements or a projection of elements.

        Args:
            selector: Optional function to extract numeric values. If None, assumes elements are numeric.

        Returns:
            The sum of elements.
        """
        if selector is None:
            return sum(self)  # type: ignore
        return sum(selector(item) for item in self)

    def average(
        self, selector: Optional[Selector[T, Union[int, float]]] = None
    ) -> float:
        """Calculate the average of elements or a projection.

        Args:
            selector: Optional function to extract numeric values.

        Returns:
            The average value.
        """
        items = list(self)
        if not items:
            raise ValueError("Sequence is empty")

        if selector is None:
            total = sum(items)  # type: ignore
        else:
            total = sum(selector(item) for item in items)  # type: ignore[misc]

        return total / len(items)

    def min(self, selector: Optional[Selector[T, Any]] = None) -> T:
        """Find the minimum element.

        Args:
            selector: Optional function to extract comparison values.

        Returns:
            The minimum element.
        """
        if selector is None:
            return min(self)  # type: ignore
        return min(self, key=selector)  # type: ignore

    def max(self, selector: Optional[Selector[T, Any]] = None) -> T:
        """Find the maximum element.

        Args:
            selector: Optional function to extract comparison values.

        Returns:
            The maximum element.
        """
        if selector is None:
            return max(self)  # type: ignore
        return max(self, key=selector)  # type: ignore

    def aggregate(
        self, func: Aggregator[TResult, T], seed: Optional[TResult] = None
    ) -> TResult:
        """Apply an accumulator function over the sequence.

        Args:
            func: Accumulator function that takes (accumulator, element).
            seed: Initial value (optional).

        Returns:
            The accumulated result.
        """
        if seed is None:
            return reduce(func, self)  # type: ignore
        return reduce(func, self, seed)  # type: ignore

    # ==================== Set Operations ====================

    def union(self, other: Iterable[T]) -> "Queryable[T]":
        """Produce the union of two sequences.

        Args:
            other: The sequence to union with.

        Returns:
            A new Queryable with unique elements from both sequences.
        """
        seen = set()

        def union_generator():
            for item in self:
                if item not in seen:
                    seen.add(item)
                    yield item
            for item in other:
                if item not in seen:
                    seen.add(item)
                    yield item

        return Queryable(union_generator())

    def intersect(self, other: Iterable[T]) -> "Queryable[T]":
        """Produce the intersection of two sequences.

        Args:
            other: The sequence to intersect with.

        Returns:
            A new Queryable with common elements.
        """
        other_set = set(other)
        seen = set()

        def intersect_generator():
            for item in self:
                if item in other_set and item not in seen:
                    seen.add(item)
                    yield item

        return Queryable(intersect_generator())

    def except_(self, other: Iterable[T]) -> "Queryable[T]":
        """Produce the difference of two sequences.

        Args:
            other: The sequence to exclude.

        Returns:
            A new Queryable with elements in this sequence but not in other.
        """
        other_set = set(other)
        seen = set()

        def except_generator():
            for item in self:
                if item not in other_set and item not in seen:
                    seen.add(item)
                    yield item

        return Queryable(except_generator())

    # ==================== Element Access ====================

    def first(self, predicate: Optional[Predicate[T]] = None) -> T:
        """Get the first element.

        Args:
            predicate: Optional function to find first matching element.

        Returns:
            The first element.

        Raises:
            IndexError: If no elements match.
        """
        if predicate is None:
            for item in self:
                return item
            raise IndexError("Sequence is empty")

        for item in self:
            if predicate(item):
                return item
        raise IndexError("No matching element found")

    def first_or_default(
        self, predicate: Optional[Predicate[T]] = None, default: Optional[T] = None
    ) -> Optional[T]:
        """Get the first element or a default value.

        Args:
            predicate: Optional function to find first matching element.
            default: Default value if no element found.

        Returns:
            The first element or default value.
        """
        try:
            return self.first(predicate)
        except IndexError:
            return default

    def last(self, predicate: Optional[Predicate[T]] = None) -> T:
        """Get the last element.

        Args:
            predicate: Optional function to find last matching element.

        Returns:
            The last element.

        Raises:
            IndexError: If no elements match.
        """
        result = None
        found = False

        if predicate is None:
            for item in self:
                result = item
                found = True
        else:
            for item in self:
                if predicate(item):
                    result = item
                    found = True

        if not found:
            raise IndexError(
                "Sequence is empty"
                if predicate is None
                else "No matching element found"
            )

        assert result is not None
        return result

    def last_or_default(
        self, predicate: Optional[Predicate[T]] = None, default: Optional[T] = None
    ) -> Optional[T]:
        """Get the last element or a default value.

        Args:
            predicate: Optional function to find last matching element.
            default: Default value if no element found.

        Returns:
            The last element or default value.
        """
        try:
            return self.last(predicate)
        except IndexError:
            return default

    def single(self, predicate: Optional[Predicate[T]] = None) -> T:
        """Get the single element.

        Args:
            predicate: Optional function to find matching element.

        Returns:
            The single element.

        Raises:
            ValueError: If zero or more than one element matches.
        """
        count = 0
        result = None

        if predicate is None:
            for item in self:
                count += 1
                if count > 1:
                    raise ValueError("Sequence contains more than one element")
                result = item
        else:
            for item in self:
                if predicate(item):
                    count += 1
                    if count > 1:
                        raise ValueError(
                            "Sequence contains more than one matching element"
                        )
                    result = item

        if count == 0:
            raise ValueError(
                "Sequence is empty"
                if predicate is None
                else "No matching element found"
            )

        assert result is not None
        return result

    def single_or_default(
        self, predicate: Optional[Predicate[T]] = None, default: Optional[T] = None
    ) -> Optional[T]:
        """Get the single element or a default value.

        Args:
            predicate: Optional function to find matching element.
            default: Default value if no element found.

        Returns:
            The single element or default value.

        Raises:
            ValueError: If more than one element matches.
        """
        try:
            return self.single(predicate)
        except ValueError as e:
            if "more than one" in str(e):
                raise
            return default

    def element_at(self, index: int) -> T:
        """Get the element at a specific index.

        Args:
            index: The zero-based index.

        Returns:
            The element at the index.

        Raises:
            IndexError: If index is out of range.
        """
        for i, item in enumerate(self):
            if i == index:
                return item
        raise IndexError("Index out of range")

    def element_at_or_default(
        self, index: int, default: Optional[T] = None
    ) -> Optional[T]:
        """Get the element at a specific index or a default value.

        Args:
            index: The zero-based index.
            default: Default value if index is out of range.

        Returns:
            The element at the index or default value.
        """
        try:
            return self.element_at(index)
        except IndexError:
            return default

    # ==================== Quantifiers ====================

    def any(self, predicate: Optional[Predicate[T]] = None) -> bool:
        """Check if any element matches the predicate.

        Args:
            predicate: Optional function to test elements.

        Returns:
            True if any element matches, False otherwise.
        """
        if predicate is None:
            return any(True for _ in self)
        return any(predicate(item) for item in self)

    def all(self, predicate: Predicate[T]) -> bool:
        """Check if all elements match the predicate.

        Args:
            predicate: Function to test elements.

        Returns:
            True if all elements match, False otherwise.
        """
        return all(predicate(item) for item in self)

    def contains(
        self, value: T, key_selector: Optional[KeySelector[T, Any]] = None
    ) -> bool:
        """Check if the sequence contains a value.

        Args:
            value: The value to check for.
            key_selector: Optional function to extract comparison key.

        Returns:
            True if the value is in the sequence, False otherwise.
        """
        if key_selector is None:
            return value in self  # type: ignore

        target_key = key_selector(value)
        for item in self:
            if key_selector(item) == target_key:
                return True
        return False

    # ==================== Conversion ====================

    def to_list(self) -> List[T]:
        """Convert the queryable to a list.

        Returns:
            A list containing all elements.
        """
        return list(self)

    def to_set(self) -> Set[T]:
        """Convert the queryable to a set.

        Returns:
            A set containing unique elements.
        """
        return set(self)

    def to_dict(self, key_selector: KeySelector[T, TKey]) -> Dict[TKey, T]:
        """Convert the queryable to a dictionary.

        Args:
            key_selector: Function to extract keys from elements.

        Returns:
            A dictionary mapping keys to elements.
        """
        return {key_selector(item): item for item in self}

    def to_dict_by_key_value(
        self, key_selector: KeySelector[T, TKey], value_selector: Selector[T, TValue]
    ) -> Dict[TKey, TValue]:
        """Convert the queryable to a dictionary with transformed values.

        Args:
            key_selector: Function to extract keys from elements.
            value_selector: Function to extract values from elements.

        Returns:
            A dictionary mapping keys to transformed values.
        """
        return {key_selector(item): value_selector(item) for item in self}

    def to_tuple(self) -> Tuple[T, ...]:
        """Convert the queryable to a tuple.

        Returns:
            A tuple containing all elements.
        """
        return tuple(self)


# Import at the end to avoid circular imports
from .types import GroupingResult  # noqa: E402
