"""Unit tests for expression tree parsing and translation."""

import pytest

from jetq.expression_parser import parse_lambda
from jetq.expressions import (
    BinaryExpression,
    ConstantExpression,
    ExpressionType,
    LambdaExpression,
    MemberExpression,
    ParameterExpression,
)


class TestLambdaParser:
    """Test lambda parsing into expression trees."""

    def test_parse_simple_equality(self):
        """Test parsing x == 5."""
        expr = parse_lambda(lambda x: x == 5)

        assert isinstance(expr, LambdaExpression)
        assert len(expr.parameters) == 1
        assert expr.parameters[0].name == "x"

        body = expr.body
        assert isinstance(body, BinaryExpression)
        assert body.expression_type == ExpressionType.EQUAL

        assert isinstance(body.left, ParameterExpression)
        assert body.left.name == "x"

        assert isinstance(body.right, ConstantExpression)
        assert body.right.value == 5

    def test_parse_greater_than(self):
        """Test parsing x > 10."""
        expr = parse_lambda(lambda x: x > 10)

        body = expr.body
        assert isinstance(body, BinaryExpression)
        assert body.expression_type == ExpressionType.GREATER_THAN
        assert body.right.value == 10

    def test_parse_member_access_dict(self):
        """Test parsing x['userId']."""
        expr = parse_lambda(lambda x: x["userId"])

        body = expr.body
        assert isinstance(body, MemberExpression)
        assert body.expression_type == ExpressionType.INDEX
        assert isinstance(body.instance, ParameterExpression)
        assert isinstance(body.member, ConstantExpression)
        assert body.member.value == "userId"

    def test_parse_member_access_dict_comparison(self):
        """Test parsing x['userId'] == 1."""
        expr = parse_lambda(lambda x: x["userId"] == 1)

        body = expr.body
        assert isinstance(body, BinaryExpression)
        assert body.expression_type == ExpressionType.EQUAL

        # Left side: x['userId']
        left = body.left
        assert isinstance(left, MemberExpression)
        assert left.expression_type == ExpressionType.INDEX

        # Right side: 1
        right = body.right
        assert isinstance(right, ConstantExpression)
        assert right.value == 1

    def test_parse_logical_and(self):
        """Test parsing x > 5 and x < 10."""
        expr = parse_lambda(lambda x: x > 5 and x < 10)

        body = expr.body
        assert isinstance(body, BinaryExpression)
        assert body.expression_type == ExpressionType.AND

        # Left: x > 5
        assert body.left.expression_type == ExpressionType.GREATER_THAN
        assert body.left.right.value == 5

        # Right: x < 10
        assert body.right.expression_type == ExpressionType.LESS_THAN
        assert body.right.right.value == 10

    def test_parse_logical_or(self):
        """Test parsing x == 1 or x == 2."""
        expr = parse_lambda(lambda x: x == 1 or x == 2)

        body = expr.body
        assert isinstance(body, BinaryExpression)
        assert body.expression_type == ExpressionType.OR

    def test_parse_string_comparison(self):
        """Test parsing x['name'] == 'Alice'."""
        expr = parse_lambda(lambda x: x["name"] == "Alice")

        body = expr.body
        assert isinstance(body, BinaryExpression)
        assert body.expression_type == ExpressionType.EQUAL
        assert body.right.value == "Alice"

    def test_parse_multiple_parameters(self):
        """Test parsing (x, y) -> x + y."""
        expr = parse_lambda(lambda x, y: x + y)

        assert len(expr.parameters) == 2
        assert expr.parameters[0].name == "x"
        assert expr.parameters[1].name == "y"

        body = expr.body
        assert isinstance(body, BinaryExpression)
        assert body.expression_type == ExpressionType.ADD

    def test_parse_arithmetic(self):
        """Test parsing x * 2 + 1."""
        expr = parse_lambda(lambda x: x * 2 + 1)

        body = expr.body
        # x * 2 + 1 is parsed as (x * 2) + 1
        assert body.expression_type == ExpressionType.ADD

        # Left side should be x * 2
        left = body.left
        assert left.expression_type == ExpressionType.MULTIPLY
        assert left.right.value == 2

        # Right side should be 1
        right = body.right
        assert right.value == 1


class TestExpressionRepresentation:
    """Test expression tree string representation."""

    def test_constant_repr(self):
        """Test constant expression repr."""
        expr = ConstantExpression(42)
        assert repr(expr) == "Constant(42)"

    def test_parameter_repr(self):
        """Test parameter expression repr."""
        expr = ParameterExpression("x")
        assert repr(expr) == "Parameter(x)"

    def test_simple_expression_repr(self):
        """Test complete lambda repr."""
        expr = parse_lambda(lambda x: x == 5)
        repr_str = repr(expr)
        assert "Lambda" in repr_str
        assert "equal" in repr_str


class TestExpressionBuilder:
    """Test manual expression tree building."""

    def test_build_equality_expression(self):
        """Test building x == 5 manually."""
        from jetq.expressions import constant, equal, parameter

        x = parameter("x")
        five = constant(5)
        expr = equal(x, five)

        assert isinstance(expr, BinaryExpression)
        assert expr.expression_type == ExpressionType.EQUAL
        assert expr.left.name == "x"
        assert expr.right.value == 5

    def test_build_complex_expression(self):
        """Test building (x > 5) AND (x < 10)."""
        from jetq.expressions import and_, constant, greater_than, less_than, parameter

        x = parameter("x")
        expr = and_(greater_than(x, constant(5)), less_than(x, constant(10)))

        assert expr.expression_type == ExpressionType.AND
        assert expr.left.expression_type == ExpressionType.GREATER_THAN
        assert expr.right.expression_type == ExpressionType.LESS_THAN


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
