"""Type definitions and utilities for jetq."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Iterable, Iterator, List, Optional, TypeVar

T = TypeVar("T")
TKey = TypeVar("TKey")
TValue = TypeVar("TValue")
TResult = TypeVar("TResult")
TInner = TypeVar("TInner")
TOuter = TypeVar("TOuter")

Selector = Callable[[T], TResult]
Predicate = Callable[[T], bool]
KeySelector = Callable[[T], TKey]
ValueSelector = Callable[[T], TValue]
Comparer = Callable[[T, T], int]
Aggregator = Callable[[TResult, T], TResult]


class QueryProvider(ABC):
    """Abstract base class for query providers."""

    @abstractmethod
    def create_query(self, iterable: Iterable[T]) -> "IQueryable[T]":
        """Create a queryable from an iterable."""
        pass

    @abstractmethod
    def execute_query(self, query: "IQueryable[T]") -> Iterator[T]:
        """Execute a query and return an iterator."""
        pass


class IEnumerable(Generic[T], ABC):
    """Base interface for enumerable sequences."""

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        """Return an iterator over the sequence."""
        pass


class IQueryable(IEnumerable[T], ABC):
    """Interface for queryable sequences with provider support."""

    @abstractmethod
    def get_provider(self) -> QueryProvider:
        """Get the query provider for this queryable."""
        pass

    @abstractmethod
    def get_enumerator(self) -> Iterator[T]:
        """Get an enumerator for this queryable."""
        pass


class OrderingDirection:
    """Represents the direction of ordering (ascending or descending)."""

    def __init__(self, selector: KeySelector[T, Any], descending: bool = False):
        self.selector = selector
        self.descending = descending
        self.next: Optional[OrderingDirection] = None

    def set_next(self, next_ordering: "OrderingDirection") -> "OrderingDirection":
        """Chain another ordering for secondary sorts."""
        self.next = next_ordering
        return next_ordering


class GroupingResult(Generic[TKey, T]):
    """Represents a grouping of elements by key."""

    def __init__(self, key: TKey, elements: List[T]):
        self.key = key
        self.elements = elements

    def __iter__(self) -> Iterator[T]:
        return iter(self.elements)

    def __len__(self) -> int:
        return len(self.elements)

    def to_list(self) -> List[T]:
        return self.elements.copy()


class JoinResult(Generic[TOuter, TInner, TResult]):
    """Represents a join result between outer and inner sequences."""

    def __init__(self, outer: TOuter, inner: List[TInner]):
        self.outer = outer
        self.inner = inner

    def __iter__(self) -> Iterator[TInner]:
        return iter(self.inner)

    def __len__(self) -> int:
        return len(self.inner)
