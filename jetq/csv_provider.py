"""CSV Query Provider for jetq using expression trees.

This module provides a query provider for CSV files that uses expression trees
to efficiently filter and query data without loading the entire file into memory.
"""

import csv
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Union

from .expression_parser import parse_lambda
from .expressions import (
    BinaryExpression,
    ConstantExpression,
    Expression,
    ExpressionType,
    ExpressionVisitor,
    MemberExpression,
)


class CsvRowFilter(ExpressionVisitor):
    """Visitor that evaluates expression trees against CSV rows.

    This visitor walks the expression tree and evaluates it against a row,
    returning True if the row matches the filter criteria.
    """

    def __init__(self, row: Dict[str, Any]):
        """Initialize with the row to evaluate against.

        Args:
            row: Dictionary representing a CSV row
        """
        self.row = row
        self.result = None

    def visit_binary(self, node: BinaryExpression) -> Any:
        """Evaluate a binary expression against the row."""
        left_val = self.visit(node.left)
        right_val = self.visit(node.right)

        op_type = node.expression_type

        # Comparison operators
        if op_type == ExpressionType.EQUAL:
            return left_val == right_val
        elif op_type == ExpressionType.NOT_EQUAL:
            return left_val != right_val
        elif op_type == ExpressionType.LESS_THAN:
            return left_val < right_val
        elif op_type == ExpressionType.LESS_THAN_OR_EQUAL:
            return left_val <= right_val
        elif op_type == ExpressionType.GREATER_THAN:
            return left_val > right_val
        elif op_type == ExpressionType.GREATER_THAN_OR_EQUAL:
            return left_val >= right_val

        # Logical operators
        elif op_type == ExpressionType.AND:
            return left_val and right_val
        elif op_type == ExpressionType.OR:
            return left_val or right_val

        # Arithmetic operators
        elif op_type == ExpressionType.ADD:
            return left_val + right_val
        elif op_type == ExpressionType.SUBTRACT:
            return left_val - right_val
        elif op_type == ExpressionType.MULTIPLY:
            return left_val * right_val
        elif op_type == ExpressionType.DIVIDE:
            return left_val / right_val
        elif op_type == ExpressionType.MODULO:
            return left_val % right_val

        return None

    def visit_constant(self, node: ConstantExpression) -> Any:
        """Return the constant value."""
        return node.value

    def visit_member(self, node: MemberExpression) -> Any:
        """Get member value from the row."""
        # Handle nested access like x["user"]["name"]
        obj = self.visit(node.instance)

        # Extract member name - it might be a ConstantExpression or a string
        if isinstance(node.member, Expression):
            member_name = self.visit(node.member)
        else:
            member_name = node.member

        if isinstance(obj, dict):
            return obj.get(member_name)
        elif hasattr(obj, member_name):
            return getattr(obj, member_name)

        return None

    def visit_parameter(self, node: Expression) -> Any:
        """Return the row itself as the parameter value."""
        return self.row

    def visit_call(self, node: Expression) -> Any:
        """Handle method calls."""
        # For CSV, we might support string methods like .startswith(), .lower(), etc.
        # This is a simplified implementation
        return None


class CsvQueryExpression:
    """Represents a CSV query with filters, projections, and pagination."""

    def __init__(self):
        self.filters: List[Expression] = []
        self.skip_count: int = 0
        self.take_count: Optional[int] = None
        self.projection: Optional[Callable] = None

    def add_filter(self, expr: Expression):
        """Add a filter expression."""
        self.filters.append(expr)

    def set_skip(self, count: int):
        """Set skip count."""
        self.skip_count = count

    def set_take(self, count: int):
        """Set take count."""
        self.take_count = count

    def set_projection(self, func: Callable):
        """Set projection function."""
        self.projection = func


class CsvQueryProvider:
    """Query provider for CSV files using expression trees.

    This provider reads CSV files efficiently using expression trees to
    filter rows during reading, avoiding loading the entire file into memory.

    Example:
        >>> provider = CsvQueryProvider("data.csv")
        >>> query = provider.create_query()
        >>> results = query.where(lambda row: row["age"] > 30).to_list()
    """

    def __init__(
        self,
        filepath: Union[str, Path],
        type_converters: Optional[Dict[str, Callable]] = None,
        encoding: str = "utf-8",
    ):
        """Initialize CSV query provider.

        Args:
            filepath: Path to the CSV file
            type_converters: Dictionary mapping column names to type conversion functions
                           e.g., {"age": int, "price": float}
            encoding: File encoding (default: 'utf-8')
        """
        self.filepath = Path(filepath)
        self.type_converters = type_converters or {}
        self.encoding = encoding
        self._headers: Optional[List[str]] = None

    @property
    def headers(self) -> List[str]:
        """Get CSV headers (cached)."""
        if self._headers is None:
            with open(self.filepath, encoding=self.encoding) as f:
                reader = csv.reader(f)
                self._headers = next(reader)
        return self._headers

    def read_rows(
        self,
        filters: Optional[List[Expression]] = None,
        skip: int = 0,
        take: Optional[int] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Read rows from CSV file with filtering.

        Args:
            filters: List of filter expressions to apply
            skip: Number of matching rows to skip
            take: Maximum number of rows to return

        Yields:
            Dictionaries representing CSV rows
        """
        with open(self.filepath, encoding=self.encoding) as f:
            reader = csv.DictReader(f)

            matched_count = 0
            returned_count = 0

            for row in reader:
                # Apply type conversions
                for col, converter in self.type_converters.items():
                    if col in row and row[col]:
                        try:
                            row[col] = converter(row[col])
                        except (ValueError, TypeError):
                            pass  # Keep original value if conversion fails

                # Apply filters
                if filters:
                    matches = True
                    matched_count_filters = 0
                    for filter_expr in filters:
                        evaluator = CsvRowFilter(row)
                        result = evaluator.visit(filter_expr)
                        # print(f"DEBUG: Row {row['name']} Filter {matched_count_filters} result: {result} for expr: {filter_expr}")
                        if not result:
                            matches = False
                            break
                        matched_count_filters += 1

                    if not matches:
                        continue

                # Apply skip
                if matched_count < skip:
                    matched_count += 1
                    continue

                matched_count += 1
                yield row

                returned_count += 1

                # Apply take limit
                if take is not None and returned_count >= take:
                    break

    def create_query(
        self, iterable: Optional[Iterable[Dict[str, Any]]] = None
    ) -> "CsvQueryable":
        """Create a new queryable for this CSV file.

        Args:
            iterable: Ignored for CSV providers; kept for interface compatibility.

        Returns:
            CsvQueryable instance
        """
        return CsvQueryable(self)

    def execute(self, query_expr: CsvQueryExpression) -> List[Dict[str, Any]]:
        """Execute a CSV query expression.

        Args:
            query_expr: The query expression to execute

        Returns:
            List of matching rows
        """
        rows = self.read_rows(
            filters=query_expr.filters if query_expr.filters else None,
            skip=query_expr.skip_count,
            take=query_expr.take_count,
        )

        results = list(rows)

        # Apply projection if specified
        if query_expr.projection:
            results = [query_expr.projection(row) for row in results]

        return results


class CsvQueryable:
    """Queryable interface for CSV files with expression tree support.

    This class provides a LINQ-like interface for querying CSV files
    using lambda expressions that are converted to expression trees.

    Example:
        >>> csv = CsvQueryable("data.csv")
        >>> results = csv.where(lambda r: r["age"] > 30).take(10).to_list()
    """

    def __init__(
        self,
        source: Union[str, Path, CsvQueryProvider],
        query_expr: Optional[CsvQueryExpression] = None,
        type_converters: Optional[Dict[str, Callable]] = None,
        encoding: str = "utf-8",
    ):
        """Initialize CSV queryable.

        Args:
            source: Path to CSV file or existing CsvQueryProvider
            query_expr: Optional existing query expression
            type_converters: Type converters (only used if source is a path)
            encoding: File encoding (only used if source is a path)
        """
        if isinstance(source, (str, Path)):
            self._provider = CsvQueryProvider(source, type_converters, encoding)
        elif isinstance(source, CsvQueryProvider):
            self._provider = source
        else:
            raise TypeError("Source must be a file path or CsvQueryProvider")

        self._query_expr = query_expr or CsvQueryExpression()

    def where(self, predicate: Callable[[Dict[str, Any]], bool]) -> "CsvQueryable":
        """Filter rows using a predicate.

        Args:
            predicate: Lambda function to filter rows

        Returns:
            New CsvQueryable with filter applied

        Example:
            >>> csv.where(lambda r: r["age"] > 30)
        """
        # Parse lambda to expression tree
        expr = parse_lambda(predicate)

        # Create new query with the filter
        new_query = CsvQueryExpression()
        new_query.filters = self._query_expr.filters.copy()
        new_query.filters.append(expr)
        new_query.skip_count = self._query_expr.skip_count
        new_query.take_count = self._query_expr.take_count
        new_query.projection = self._query_expr.projection

        return CsvQueryable(self._provider, new_query)

    def skip(self, count: int) -> "CsvQueryable":
        """Skip a number of rows.

        Args:
            count: Number of rows to skip

        Returns:
            New CsvQueryable with skip applied
        """
        new_query = CsvQueryExpression()
        new_query.filters = self._query_expr.filters.copy()
        new_query.skip_count = count
        new_query.take_count = self._query_expr.take_count
        new_query.projection = self._query_expr.projection

        return CsvQueryable(self._provider, new_query)

    def take(self, count: int) -> "CsvQueryable":
        """Take only a number of rows.

        Args:
            count: Maximum number of rows to return

        Returns:
            New CsvQueryable with take applied
        """
        new_query = CsvQueryExpression()
        new_query.filters = self._query_expr.filters.copy()
        new_query.skip_count = self._query_expr.skip_count
        new_query.take_count = count
        new_query.projection = self._query_expr.projection

        return CsvQueryable(self._provider, new_query)

    def select(self, selector: Callable[[Dict[str, Any]], Any]) -> "CsvQueryable":
        """Project rows using a selector.

        Args:
            selector: Function to transform each row

        Returns:
            New CsvQueryable with projection applied

        Example:
            >>> csv.select(lambda r: {"name": r["name"], "age": r["age"]})
        """
        new_query = CsvQueryExpression()
        new_query.filters = self._query_expr.filters.copy()
        new_query.skip_count = self._query_expr.skip_count
        new_query.take_count = self._query_expr.take_count
        new_query.projection = selector

        return CsvQueryable(self._provider, new_query)

    def to_list(self) -> List[Any]:
        """Execute the query and return results as a list.

        Returns:
            List of matching rows
        """
        return self._provider.execute(self._query_expr)

    def first(self) -> Optional[Any]:
        """Get the first matching row.

        Returns:
            First matching row or None
        """
        results = self.take(1).to_list()
        return results[0] if results else None

    def count(self) -> int:
        """Count matching rows.

        Returns:
            Number of matching rows
        """
        return len(self.to_list())

    def __iter__(self):
        """Make queryable iterable."""
        return iter(self.to_list())


def from_csv(
    filepath: Union[str, Path],
    type_converters: Optional[Dict[str, Callable]] = None,
    encoding: str = "utf-8",
) -> CsvQueryable:
    """Create a queryable from a CSV file.

    Convenience function to quickly create a CSV queryable.

    Args:
        filepath: Path to the CSV file
        type_converters: Dictionary mapping column names to type conversion functions
        encoding: File encoding

    Returns:
        CsvQueryable instance

    Example:
        >>> from jetq.csv_provider import from_csv
        >>> data = from_csv("data.csv", type_converters={"age": int, "price": float})
        >>> results = data.where(lambda r: r["age"] > 30).to_list()
    """
    provider = CsvQueryProvider(filepath, type_converters, encoding)
    return provider.create_query()
