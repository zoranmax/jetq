"""REST API Query Provider - translates LINQ queries to REST API calls.

This demonstrates how expression trees enable remote query execution by
translating where/select/order operations into REST query parameters.
"""

import json
import urllib.parse
import urllib.request
from typing import Any, Callable, Dict, Iterator, List, Optional, TypeVar

from .expression_parser import parse_lambda
from .expressions import (
    BinaryExpression,
    ConstantExpression,
    Expression,
    ExpressionType,
    ExpressionVisitor,
    MemberExpression,
)
from .queryable import Queryable

T = TypeVar("T")


class QueryExpression:
    """Represents a query that can be translated to a REST API call."""

    def __init__(self, base_url: str, resource_path: str):
        self.base_url = base_url
        self.resource_path = resource_path
        self.filters: List[Expression] = []
        self.projections: List[str] = []
        self.order_by_field: Optional[str] = None
        self.order_descending: bool = False
        self.skip_count: Optional[int] = None
        self.take_count: Optional[int] = None

    def add_filter(self, predicate_expr: Expression):
        """Add a filter condition."""
        self.filters.append(predicate_expr)

    def add_projection(self, field: str):
        """Add a field to project."""
        self.projections.append(field)

    def set_ordering(self, field: str, descending: bool = False):
        """Set ordering."""
        self.order_by_field = field
        self.order_descending = descending

    def set_skip(self, count: int):
        """Set number of records to skip."""
        self.skip_count = count

    def set_take(self, count: int):
        """Set number of records to take."""
        self.take_count = count


class RestQueryTranslator(ExpressionVisitor):
    """Translates expression trees to REST API query parameters.

    This is a simple implementation that generates query strings.
    Real implementations would support specific REST APIs like OData, JSON:API, etc.
    """

    def __init__(self):
        self.param_name: Optional[str] = None

    def translate_filter(self, predicate_expr: Expression) -> Dict[str, str]:
        """Translate a filter expression to query parameters.

        For example: lambda x: x['userId'] == 1
        Becomes: {'userId': '1'}
        """
        params = {}

        if isinstance(predicate_expr, BinaryExpression):
            if predicate_expr.expression_type == ExpressionType.EQUAL:
                # Extract field name and value
                field = self._extract_field_name(predicate_expr.left)
                value = self._extract_constant_value(predicate_expr.right)

                if field and value is not None:
                    params[field] = str(value)

            elif predicate_expr.expression_type == ExpressionType.AND:
                # Handle AND by merging both sides
                left_params = self.translate_filter(predicate_expr.left)
                right_params = self.translate_filter(predicate_expr.right)
                params.update(left_params)
                params.update(right_params)

        return params

    def _extract_field_name(self, expr: Expression) -> Optional[str]:
        """Extract field name from member access expression."""
        if isinstance(expr, MemberExpression):
            if expr.expression_type == ExpressionType.INDEX:
                # x['fieldName']
                if isinstance(expr.member, ConstantExpression):
                    return str(expr.member.value)
            elif expr.expression_type == ExpressionType.ATTRIBUTE:
                # x.fieldName
                return str(expr.member)
        return None

    def _extract_constant_value(self, expr: Expression) -> Any:
        """Extract constant value from expression."""
        if isinstance(expr, ConstantExpression):
            return expr.value
        return None


class RestQueryProvider:
    """Query provider that executes queries against REST APIs.

    Example usage:
        provider = RestQueryProvider("https://jsonplaceholder.typicode.com")
        posts = provider.create_query("posts")

        # This will translate to: GET /posts?userId=1
        result = posts.where(lambda p: p['userId'] == 1).to_list()
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.translator = RestQueryTranslator()

    def create_query(self, resource_path: str) -> "RestQueryable[Dict[str, Any]]":
        """Create a queryable for a REST resource."""
        query_expr = QueryExpression(self.base_url, resource_path)
        return RestQueryable(query_expr, self)

    def execute_query(self, query_expr: QueryExpression) -> Iterator[Dict]:
        """Execute the query by making an HTTP request."""
        # Build URL with query parameters
        url = f"{query_expr.base_url}/{query_expr.resource_path}"

        # Translate filters to query parameters
        params = {}
        for filter_expr in query_expr.filters:
            filter_params = self.translator.translate_filter(filter_expr)
            params.update(filter_params)

        # Add pagination parameters
        if query_expr.skip_count is not None:
            params["_start"] = str(query_expr.skip_count)
        if query_expr.take_count is not None:
            params["_limit"] = str(query_expr.take_count)

        # Add sorting parameters (JSONPlaceholder style)
        if query_expr.order_by_field:
            params["_sort"] = query_expr.order_by_field
            params["_order"] = "desc" if query_expr.order_descending else "asc"

        # Build full URL
        if params:
            query_string = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_string}"
        else:
            full_url = url

        print(f"[REST Provider] Executing: {full_url}")

        # Make HTTP request
        try:
            with urllib.request.urlopen(full_url, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            # Return iterator over results
            if isinstance(data, list):
                return iter(data)
            else:
                return iter([data])
        except Exception as e:
            raise RuntimeError(f"REST query failed: {e}") from e


class RestQueryable(Queryable[T]):
    """A queryable that builds expression trees for remote execution.

    This extends Queryable to intercept operations and build up a query
    expression that can be translated to REST API calls.
    """

    def __init__(self, query_expr: QueryExpression, provider: RestQueryProvider):
        self._query_expr = query_expr
        self._provider = provider
        self._executed = False
        self._results: Optional[List[T]] = None

        # Don't initialize with an iterable yet
        super().__init__([], provider)

    def where(self, predicate: Callable[[T], bool]) -> "RestQueryable[T]":
        """Add a filter condition by parsing the lambda."""
        # Parse the lambda into an expression tree
        expr = parse_lambda(predicate)
        self._query_expr.add_filter(expr.body)

        # Return a new queryable with updated expression
        return RestQueryable(self._query_expr, self._provider)

    def skip(self, count: int) -> "RestQueryable[T]":
        """Skip N records on the server."""
        self._query_expr.set_skip(count)
        return RestQueryable(self._query_expr, self._provider)

    def take(self, count: int) -> "RestQueryable[T]":
        """Take N records from the server."""
        self._query_expr.set_take(count)
        return RestQueryable(self._query_expr, self._provider)

    def __iter__(self) -> Iterator[T]:
        """Execute the query when enumerated."""
        if not self._executed:
            self._results = list(self._provider.execute_query(self._query_expr))  # type: ignore
            self._executed = True

        return iter(self._results or [])
        return list(self)


# Example usage
def example_rest_query():
    """Example of using REST query provider with expression trees."""

    # Create a provider for JSONPlaceholder API
    provider = RestQueryProvider("https://jsonplaceholder.typicode.com")

    # Create a queryable for posts
    posts = provider.create_query("posts")

    print("Example 1: Filter by userId")
    print("-" * 50)
    # This translates to: GET /posts?userId=1
    result = posts.where(lambda p: p["userId"] == 1).to_list()
    print(f"Found {len(result)} posts for userId=1")
    print()

    print("Example 2: Filter and paginate")
    print("-" * 50)
    # This translates to: GET /posts?userId=1&_limit=3
    result = posts.where(lambda p: p["userId"] == 1).take(3).to_list()
    print(f"Found {len(result)} posts (limited to 3)")
    print()

    print("Example 3: Without expression trees (fetch all then filter)")
    print("-" * 50)
    # For comparison, the old way without expression trees
    import urllib.request

    with urllib.request.urlopen(
        "https://jsonplaceholder.typicode.com/posts"
    ) as response:
        all_posts = json.loads(response.read().decode("utf-8"))
    filtered = [p for p in all_posts if p["userId"] == 1]
    print(f"Fetched {len(all_posts)} posts, filtered to {len(filtered)}")
    print("^ This is inefficient - downloaded all data!")


if __name__ == "__main__":
    example_rest_query()
