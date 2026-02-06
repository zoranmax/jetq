"""Query provider implementation for PLINQ."""

from typing import Iterable, Iterator, TypeVar, Any
from abc import ABC, abstractmethod

T = TypeVar('T')


class QueryProvider:
    """Default query provider for LINQ operations."""
    
    def create_query(self, iterable: Iterable[T]) -> 'Queryable[T]':
        """Create a queryable from an iterable."""
        from .queryable import Queryable
        return Queryable(iterable, self)
    
    def execute_query(self, source: Iterable[T]) -> Iterator[T]:
        """Execute a query by iterating over the source."""
        return iter(source)
