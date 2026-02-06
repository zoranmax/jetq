"""PLINQ - Python LINQ implementation."""

from .queryable import Queryable, OrderedQueryable
from .query_provider import QueryProvider
from .types import GroupingResult

__version__ = "0.1.0"
__author__ = "PLINQ Contributors"

__all__ = [
    "Queryable",
    "OrderedQueryable",
    "QueryProvider",
    "GroupingResult",
]
