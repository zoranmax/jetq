"""jetq - Python LINQ implementation."""

from .csv_provider import CsvQueryable, CsvQueryProvider, from_csv
from .expression_parser import LambdaParser, parse_lambda

# Expression tree support (experimental)
from .expressions import (
    BinaryExpression,
    ConstantExpression,
    Expression,
    ExpressionType,
    ExpressionVisitor,
    LambdaExpression,
    MemberExpression,
    ParameterExpression,
    UnaryExpression,
)
from .query_provider import QueryProvider
from .queryable import OrderedQueryable, Queryable
from .rest_provider import RestQueryable, RestQueryProvider
from .types import GroupingResult

__version__ = "0.1.0"
__author__ = "jetq Contributors"

__all__ = [
    "Queryable",
    "OrderedQueryable",
    "QueryProvider",
    "GroupingResult",
    # Expression tree support
    "Expression",
    "ExpressionType",
    "ExpressionVisitor",
    "BinaryExpression",
    "ConstantExpression",
    "LambdaExpression",
    "MemberExpression",
    "ParameterExpression",
    "UnaryExpression",
    "parse_lambda",
    "LambdaParser",
    # CSV provider support
    "CsvQueryProvider",
    "CsvQueryable",
    "from_csv",
    "RestQueryProvider",
    "RestQueryable",
]
