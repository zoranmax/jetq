"""Expression tree support for translating Python expressions to remote queries.

This module provides classes to build Abstract Syntax Trees (ASTs) from Python
lambda functions, enabling query providers to translate LINQ operations into
remote query languages (SQL, OData, REST query parameters, etc.).
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, ClassVar, List, Optional, TypeVar, Union

T = TypeVar("T")


class ExpressionType(Enum):
    """Types of expressions in the AST."""

    # Literals and constants
    CONSTANT = "constant"
    PARAMETER = "parameter"

    # Binary operations
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    MODULO = "modulo"

    # Comparison operations
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"

    # Logical operations
    AND = "and"
    OR = "or"
    NOT = "not"

    # Member access
    ATTRIBUTE = "attribute"
    INDEX = "index"

    # Function calls
    CALL = "call"
    LAMBDA = "lambda"


class Expression(ABC):
    """Base class for all expression tree nodes."""

    def __init__(self, expression_type: ExpressionType):
        self.expression_type = expression_type

    @abstractmethod
    def __repr__(self) -> str:
        """Return string representation of the expression."""
        pass


class ConstantExpression(Expression):
    """Represents a constant value."""

    def __init__(self, value: Any):
        super().__init__(ExpressionType.CONSTANT)
        self.value = value

    def __repr__(self) -> str:
        return f"Constant({self.value!r})"


class ParameterExpression(Expression):
    """Represents a parameter (e.g., lambda parameter)."""

    def __init__(self, name: str, param_type: Optional[type] = None):
        super().__init__(ExpressionType.PARAMETER)
        self.name = name
        self.param_type = param_type

    def __repr__(self) -> str:
        return f"Parameter({self.name})"


class BinaryExpression(Expression):
    """Represents a binary operation (left op right)."""

    def __init__(
        self, expression_type: ExpressionType, left: Expression, right: Expression
    ):
        super().__init__(expression_type)
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"Binary({self.expression_type.value}, {self.left}, {self.right})"


class UnaryExpression(Expression):
    """Represents a unary operation (op operand)."""

    def __init__(self, expression_type: ExpressionType, operand: Expression):
        super().__init__(expression_type)
        self.operand = operand

    def __repr__(self) -> str:
        return f"Unary({self.expression_type.value}, {self.operand})"


class MemberExpression(Expression):
    """Represents member access (object.member or object['key'])."""

    def __init__(
        self,
        expression_type: ExpressionType,
        instance: Expression,
        member: Union[str, Expression],
    ):
        super().__init__(expression_type)
        self.instance = instance
        self.member = member

    def __repr__(self) -> str:
        return f"Member({self.instance}.{self.member})"


class CallExpression(Expression):
    """Represents a function or method call."""

    def __init__(
        self,
        function: Expression,
        arguments: List[Expression],
    ):
        super().__init__(ExpressionType.CALL)
        self.function = function
        self.arguments = arguments

    def __repr__(self) -> str:
        args = ", ".join(repr(arg) for arg in self.arguments)
        return f"Call({self.function}, [{args}])"


class LambdaExpression(Expression):
    """Represents a lambda function with parameters and body."""

    def __init__(self, parameters: List[ParameterExpression], body: Expression):
        super().__init__(ExpressionType.LAMBDA)
        self.parameters = parameters
        self.body = body

    def __repr__(self) -> str:
        params = ", ".join(p.name for p in self.parameters)
        return f"Lambda([{params}], {self.body})"


class ExpressionVisitor(ABC):
    """Base class for visiting and transforming expression trees."""

    class_var: ClassVar[str]  # unassigned

    def visit(self, expression: Expression) -> Any:
        """Visit an expression node."""
        method_name = f"visit_{expression.expression_type.value}"
        method = getattr(self, method_name, self.generic_visit)
        return method(expression)

    def generic_visit(self, expression: Expression) -> Any:
        """Default visit method."""
        raise NotImplementedError(
            f"No visit method for {expression.expression_type.value}"
        )

    def visit_constant(self, expression: ConstantExpression) -> Any:
        """Visit a constant expression."""
        return expression.value

    def visit_parameter(self, expression: ParameterExpression) -> Any:
        """Visit a parameter expression."""
        return expression.name

    def visit_equal(self, expression: BinaryExpression) -> Any:
        """Visit an equality expression."""
        return self.visit_binary(expression)

    def visit_not_equal(self, expression: BinaryExpression) -> Any:
        """Visit a not-equal expression."""
        return self.visit_binary(expression)

    def visit_less_than(self, expression: BinaryExpression) -> Any:
        """Visit a less-than expression."""
        return self.visit_binary(expression)

    def visit_less_than_or_equal(self, expression: BinaryExpression) -> Any:
        """Visit a less-than-or-equal expression."""
        return self.visit_binary(expression)

    def visit_greater_than(self, expression: BinaryExpression) -> Any:
        """Visit a greater-than expression."""
        return self.visit_binary(expression)

    def visit_greater_than_or_equal(self, expression: BinaryExpression) -> Any:
        """Visit a greater-than-or-equal expression."""
        return self.visit_binary(expression)

    def visit_and(self, expression: BinaryExpression) -> Any:
        """Visit a logical AND expression."""
        return self.visit_binary(expression)

    def visit_or(self, expression: BinaryExpression) -> Any:
        """Visit a logical OR expression."""
        return self.visit_binary(expression)

    def visit_not(self, expression: UnaryExpression) -> Any:
        """Visit a logical NOT expression."""
        return self.visit_unary(expression)

    def visit_add(self, expression: BinaryExpression) -> Any:
        """Visit an addition expression."""
        return self.visit_binary(expression)

    def visit_subtract(self, expression: BinaryExpression) -> Any:
        """Visit a subtraction expression."""
        return self.visit_binary(expression)

    def visit_multiply(self, expression: BinaryExpression) -> Any:
        """Visit a multiplication expression."""
        return self.visit_binary(expression)

    def visit_divide(self, expression: BinaryExpression) -> Any:
        """Visit a division expression."""
        return self.visit_binary(expression)

    def visit_modulo(self, expression: BinaryExpression) -> Any:
        """Visit a modulo expression."""
        return self.visit_binary(expression)

    def visit_attribute(self, expression: MemberExpression) -> Any:
        """Visit an attribute access expression."""
        return self.visit_member(expression)

    def visit_index(self, expression: MemberExpression) -> Any:
        """Visit an index access expression."""
        return self.visit_member(expression)

    def visit_call(self, expression: CallExpression) -> Any:
        """Visit a function call expression."""
        func = self.visit(expression.function)
        args = [self.visit(arg) for arg in expression.arguments]
        return func, args

    def visit_lambda(self, expression: LambdaExpression) -> Any:
        """Visit a lambda expression."""
        return self.visit(expression.body)

    def visit_binary(self, expression: BinaryExpression) -> Any:
        """Visit a binary expression."""
        left = self.visit(expression.left)
        right = self.visit(expression.right)
        return (expression.expression_type, left, right)

    def visit_unary(self, expression: UnaryExpression) -> Any:
        """Visit a unary expression."""
        operand = self.visit(expression.operand)
        return (expression.expression_type, operand)

    def visit_member(self, expression: MemberExpression) -> Any:
        """Visit a member access expression."""
        instance = self.visit(expression.instance)
        member = expression.member
        return (instance, member)


# Helper functions for building expressions
def constant(value: Any) -> ConstantExpression:
    """Create a constant expression."""
    return ConstantExpression(value)


def parameter(name: str, param_type: Optional[type] = None) -> ParameterExpression:
    """Create a parameter expression."""
    return ParameterExpression(name, param_type)


def equal(left: Expression, right: Expression) -> BinaryExpression:
    """Create an equality expression."""
    return BinaryExpression(ExpressionType.EQUAL, left, right)


def not_equal(left: Expression, right: Expression) -> BinaryExpression:
    """Create a not-equal expression."""
    return BinaryExpression(ExpressionType.NOT_EQUAL, left, right)


def less_than(left: Expression, right: Expression) -> BinaryExpression:
    """Create a less-than expression."""
    return BinaryExpression(ExpressionType.LESS_THAN, left, right)


def greater_than(left: Expression, right: Expression) -> BinaryExpression:
    """Create a greater-than expression."""
    return BinaryExpression(ExpressionType.GREATER_THAN, left, right)


def and_(left: Expression, right: Expression) -> BinaryExpression:
    """Create a logical AND expression."""
    return BinaryExpression(ExpressionType.AND, left, right)


def or_(left: Expression, right: Expression) -> BinaryExpression:
    """Create a logical OR expression."""
    return BinaryExpression(ExpressionType.OR, left, right)


def not_(operand: Expression) -> UnaryExpression:
    """Create a logical NOT expression."""
    return UnaryExpression(ExpressionType.NOT, operand)


def attribute(instance: Expression, member: str) -> MemberExpression:
    """Create an attribute access expression."""
    return MemberExpression(ExpressionType.ATTRIBUTE, instance, member)


def index(instance: Expression, key: Expression) -> MemberExpression:
    """Create an index access expression."""
    return MemberExpression(ExpressionType.INDEX, instance, key)


def call(function: Expression, *arguments: Expression) -> CallExpression:
    """Create a function call expression."""
    return CallExpression(function, list(arguments))


def lambda_(
    parameters: List[ParameterExpression], body: Expression
) -> LambdaExpression:
    """Create a lambda expression."""
    return LambdaExpression(parameters, body)
