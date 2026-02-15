"""jetq - Python LINQ implementation."""

from .query_provider import QueryProvider
from .queryable import OrderedQueryable, Queryable
from .types import GroupingResult

__version__ = "0.1.0"
__author__ = "jetq Contributors"

__all__ = [
    "Queryable",
    "OrderedQueryable",
    "QueryProvider",
    "GroupingResult",
]
