"""Query provider implementation for jetq."""

from typing import Iterable, Iterator, Optional, TypeVar

from jetq.queryable import Queryable

T = TypeVar("T")


class QueryProvider:
    """Default query provider for LINQ operations."""

    def create_query(self, iterable: Optional[Iterable[T]] = None) -> Queryable[T]:
        """Create a queryable from an iterable."""
        from .queryable import Queryable

        return Queryable(iterable or [], self)

    def execute_query(self, source: Iterable[T]) -> Iterator[T]:
        """Execute a query by iterating over the source."""
        return iter(source)
