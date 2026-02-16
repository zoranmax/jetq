"""Parse Python lambda functions into expression trees.

This module uses Python's ast module to inspect lambda bytecode and convert
it into queryable expression trees that can be translated to remote queries.
"""

import ast
import inspect
import linecache
from typing import Any, Callable, Optional

from .expressions import (
    BinaryExpression,
    CallExpression,
    ConstantExpression,
    Expression,
    ExpressionType,
    LambdaExpression,
    MemberExpression,
    ParameterExpression,
    UnaryExpression,
)


class LambdaParser:
    """Parse Python lambda functions into expression trees."""

    def parse(self, func: Callable) -> LambdaExpression:
        """Parse a lambda function into an expression tree.

        Args:
            func: A Python lambda or function to parse.

        Returns:
            A LambdaExpression representing the function.

        Raises:
            ValueError: If the function cannot be parsed.
        """
        source = self._get_source(func)
        if source is None:
            raise ValueError(
                "Cannot parse lambda: source code not available. "
                "Expression trees require lambdas to be parseable."
            )

        # Parse the source code
        try:
            tree = ast.parse(source.strip())
        except SyntaxError:
            candidate = None
            if "lambda" in source:
                for line in source.splitlines():
                    if "lambda" in line:
                        candidate = self._extract_lambda_from_line(line)
                        if candidate:
                            break

            if candidate:
                tree = ast.parse(candidate.strip())
            else:
                raise

        # Find the lambda or function definition
        lambda_node = self._find_lambda(tree, func)
        if lambda_node is None:
            raise ValueError("No lambda or function definition found")

        if isinstance(lambda_node, ast.Lambda):
            return self._parse_lambda(lambda_node)

        if isinstance(lambda_node, ast.FunctionDef):
            return self._parse_function(lambda_node)

        raise ValueError("Unsupported callable node type")

    def _extract_lambda_from_line(self, line: str) -> Optional[str]:
        """Extract just the lambda expression from a line of code.

        Args:
            line: Line of code containing a lambda

        Returns:
            Just the lambda expression or None
        """
        if "lambda" not in line:
            return None

        lambda_start = line.index("lambda")
        remainder = line[lambda_start:]

        # Try progressively shorter suffixes to find valid lambda
        # Start from the end and work backwards
        for i in range(len(remainder), 0, -1):
            candidate = remainder[:i].rstrip(", )]};\n")
            if candidate:
                try:
                    # Try to parse as lambda
                    tree = ast.parse(candidate)
                    # Check if it contains a lambda
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Lambda):
                            return candidate
                except SyntaxError:
                    continue

        return None

    def _get_source(self, func: Callable) -> Optional[str]:
        """Get source code for a function using multiple strategies.

        Args:
            func: The function to get source for.

        Returns:
            Source code string or None if unavailable.
        """
        import os
        import sys

        # Strategy 1: Try inspect.getsource() - works for most cases
        try:
            source = inspect.getsource(func)
            if source:
                return source
        except (OSError, TypeError):
            pass

        # Strategy 2: Try getting from code object with direct file read
        # This works better for lambdas in Docker/mounted volume environments
        try:
            code = func.__code__
            filename = code.co_filename
            lineno = code.co_firstlineno

            # Handle relative paths - try both as-is and as absolute
            filenames_to_try = [filename]
            if not os.path.isabs(filename):
                filenames_to_try.append(os.path.abspath(filename))
            # Also try with /app prefix for Docker
            if not filename.startswith("/app"):
                filenames_to_try.append(os.path.join("/app", filename.lstrip("./")))

            for filepath in filenames_to_try:
                try:
                    with open(filepath, encoding="utf-8") as f:
                        lines = f.readlines()
                        if 0 < lineno <= len(lines):
                            line = lines[lineno - 1].strip()
                            if "lambda" in line:
                                # Try to extract just the lambda expression
                                lambda_expr = self._extract_lambda_from_line(line)
                                if lambda_expr:
                                    return lambda_expr
                                # Fallback to full line
                                return line
                            # Even if no 'lambda' keyword, return the line
                            if line:
                                return line
                except (
                    OSError,
                    FileNotFoundError,
                    UnicodeDecodeError,
                    PermissionError,
                ):
                    continue

            # Fallback to linecache if direct read fails
            for filepath in filenames_to_try:
                line = linecache.getline(filepath, lineno)
                if line:
                    line = line.strip()
                    if "lambda" in line:
                        lambda_expr = self._extract_lambda_from_line(line)
                        if lambda_expr:
                            return lambda_expr
                        return line
                    if line:
                        return line

        except (AttributeError, KeyError, IndexError, ValueError):
            pass

        # Strategy 3: Try inspect.getsourcelines()
        try:
            lines, _ = inspect.getsourcelines(func)
            if lines:
                return "".join(lines)
        except (OSError, TypeError):
            pass

        # Strategy 4: Try to find the module and read from it
        try:
            code = func.__code__
            filename = code.co_filename

            # Try to find matching module
            for _, module in list(sys.modules.items()):
                try:
                    if module and hasattr(module, "__file__") and module.__file__:
                        module_file = module.__file__
                        # Handle .pyc files
                        if module_file.endswith(".pyc"):
                            module_file = module_file[:-1]  # Remove 'c' to get .py

                        # Check if this is the right module
                        if os.path.basename(module_file) == os.path.basename(
                            filename
                        ) or os.path.abspath(module_file) == os.path.abspath(filename):
                            with open(module_file, encoding="utf-8") as f:
                                lines = f.readlines()
                                if 0 < code.co_firstlineno <= len(lines):
                                    line = lines[code.co_firstlineno - 1].strip()
                                    if "lambda" in line:
                                        lambda_expr = self._extract_lambda_from_line(
                                            line
                                        )
                                        if lambda_expr:
                                            return lambda_expr
                                        return line
                except Exception:
                    continue
        except Exception:
            pass

        return None

    def _find_lambda(
        self, node: ast.AST, func: Optional[Callable] = None
    ) -> Optional[ast.AST]:
        """Find a lambda or function definition in the AST matching the function code."""
        candidates: list[ast.AST] = []
        for child in ast.walk(node):
            if isinstance(child, ast.Lambda):
                candidates.append(child)
            elif isinstance(child, ast.FunctionDef):
                candidates.append(child)

        if not candidates:
            return None

        # If no func provided or only one candidate, return first (simplest case)
        if func is None or len(candidates) == 1:
            return candidates[0]

        try:
            target_code = func.__code__
        except AttributeError:
            return candidates[0]

        # Try to find exact bytecode match
        for cand in candidates:
            try:
                if isinstance(cand, ast.FunctionDef):
                    # Compile function definition
                    module = ast.Module(body=[cand], type_ignores=[])
                    ast.fix_missing_locations(module)
                    code = compile(module, "<string>", "exec")
                    glob: dict[str, Any] = {}
                    exec(code, glob)
                    func_from_ast = glob[cand.name]
                elif isinstance(cand, ast.Lambda):
                    # Compile lambda expression
                    expr = ast.Expression(body=cand)
                    ast.fix_missing_locations(expr)
                    code = compile(expr, "<string>", "eval")
                    func_from_ast = eval(code)
                else:
                    continue

                cand_code = func_from_ast.__code__

                # Check for match. We compare bytecode and constants.
                # Note: This might fail for closures where variables are captured differently
                # (LOAD_FAST vs LOAD_DEREF vs LOAD_GLOBAL), but works for pure lambdas.
                if (
                    cand_code.co_code == target_code.co_code
                    and cand_code.co_consts == target_code.co_consts
                ):
                    return cand

            except Exception:
                continue

        # Fallback: if no exact match found (e.g. due to closure differences),
        # return the first candidate. Use deeper logic if needed.
        return candidates[0]

    def _parse_lambda(self, node: ast.Lambda) -> LambdaExpression:
        """Parse a lambda AST node."""
        # Parse parameters
        parameters = []
        for arg in node.args.args:
            parameters.append(ParameterExpression(arg.arg))

        # Parse body
        body = self._parse_expression(node.body)

        return LambdaExpression(parameters, body)

    def _parse_function(self, node: ast.FunctionDef) -> LambdaExpression:
        """Parse a function definition AST node."""
        parameters = []
        for arg in node.args.args:
            parameters.append(ParameterExpression(arg.arg))

        return_node = None
        for stmt in node.body:
            if isinstance(stmt, ast.Return):
                return_node = stmt
                break

        if return_node is None or return_node.value is None:
            raise ValueError("Function must contain a return statement")

        body = self._parse_expression(return_node.value)
        return LambdaExpression(parameters, body)

    def _parse_expression(self, node: ast.AST) -> Expression:
        """Parse an AST node into an expression."""
        if isinstance(node, ast.Constant):
            return ConstantExpression(node.value)

        elif isinstance(node, ast.Name):
            return ParameterExpression(node.id)

        elif isinstance(node, ast.Compare):
            return self._parse_compare(node)

        elif isinstance(node, ast.BinOp):
            return self._parse_binop(node)

        elif isinstance(node, ast.UnaryOp):
            return self._parse_unaryop(node)

        elif isinstance(node, ast.BoolOp):
            return self._parse_boolop(node)

        elif isinstance(node, ast.Attribute):
            return self._parse_attribute(node)

        elif isinstance(node, ast.Subscript):
            return self._parse_subscript(node)

        elif isinstance(node, ast.Call):
            return self._parse_call(node)

        else:
            raise ValueError(f"Unsupported expression type: {type(node).__name__}")

    def _parse_compare(self, node: ast.Compare) -> Expression:
        """Parse a comparison operation."""
        left = self._parse_expression(node.left)

        # Handle chained comparisons by building nested binary expressions
        result = left
        for op, comparator in zip(node.ops, node.comparators):
            right = self._parse_expression(comparator)

            if isinstance(op, ast.Eq):
                expr_type = ExpressionType.EQUAL
            elif isinstance(op, ast.NotEq):
                expr_type = ExpressionType.NOT_EQUAL
            elif isinstance(op, ast.Lt):
                expr_type = ExpressionType.LESS_THAN
            elif isinstance(op, ast.LtE):
                expr_type = ExpressionType.LESS_THAN_OR_EQUAL
            elif isinstance(op, ast.Gt):
                expr_type = ExpressionType.GREATER_THAN
            elif isinstance(op, ast.GtE):
                expr_type = ExpressionType.GREATER_THAN_OR_EQUAL
            else:
                raise ValueError(
                    f"Unsupported comparison operator: {type(op).__name__}"
                )

            result = BinaryExpression(expr_type, result, right)

        return result

    def _parse_binop(self, node: ast.BinOp) -> BinaryExpression:
        """Parse a binary operation."""
        left = self._parse_expression(node.left)
        right = self._parse_expression(node.right)

        op_map = {
            ast.Add: ExpressionType.ADD,
            ast.Sub: ExpressionType.SUBTRACT,
            ast.Mult: ExpressionType.MULTIPLY,
            ast.Div: ExpressionType.DIVIDE,
            ast.Mod: ExpressionType.MODULO,
        }

        expr_type = op_map.get(type(node.op))
        if expr_type is None:
            raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")

        return BinaryExpression(expr_type, left, right)

    def _parse_unaryop(self, node: ast.UnaryOp) -> UnaryExpression:
        """Parse a unary operation."""
        operand = self._parse_expression(node.operand)

        if isinstance(node.op, ast.Not):
            expr_type = ExpressionType.NOT
        else:
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")

        return UnaryExpression(expr_type, operand)

    def _parse_boolop(self, node: ast.BoolOp) -> Expression:
        """Parse a boolean operation (and/or)."""
        if isinstance(node.op, ast.And):
            expr_type = ExpressionType.AND
        elif isinstance(node.op, ast.Or):
            expr_type = ExpressionType.OR
        else:
            raise ValueError(f"Unsupported boolean operator: {type(node.op).__name__}")

        # Chain multiple operands
        values = [self._parse_expression(v) for v in node.values]
        result = values[0]
        for value in values[1:]:
            result = BinaryExpression(expr_type, result, value)

        return result

    def _parse_attribute(self, node: ast.Attribute) -> MemberExpression:
        """Parse an attribute access (obj.attr)."""
        instance = self._parse_expression(node.value)
        return MemberExpression(ExpressionType.ATTRIBUTE, instance, node.attr)

    def _parse_subscript(self, node: ast.Subscript) -> MemberExpression:
        """Parse a subscript access (obj[key])."""
        instance = self._parse_expression(node.value)

        # Handle different index types across Python versions
        # Python 3.9+: node.slice is the expression directly (e.g., ast.Constant)
        # Python 3.8-: node.slice is ast.Index wrapping the expression
        try:
            # Try Python 3.9+ first - slice is the expression directly
            key = self._parse_expression(node.slice)
        except (ValueError, AttributeError):
            # Fall back to Python 3.8 - slice is ast.Index
            if hasattr(node.slice, "value"):
                key = self._parse_expression(node.slice.value)  # type: ignore[attr-defined]
            else:
                raise

        return MemberExpression(ExpressionType.INDEX, instance, key)

    def _parse_call(self, node: ast.Call) -> CallExpression:
        """Parse a function call."""
        func = self._parse_expression(node.func)
        args = [self._parse_expression(arg) for arg in node.args]
        return CallExpression(func, args)


# Global parser instance
_parser = LambdaParser()


def parse_lambda(func: Callable) -> LambdaExpression:
    """Parse a lambda function into an expression tree.

    Args:
        func: A Python lambda or function to parse.

    Returns:
        A LambdaExpression representing the function.

    Example:
        >>> from jetq.expression_parser import parse_lambda
        >>> expr = parse_lambda(lambda x: x > 5)
        >>> print(expr)
        Lambda([x], Binary(greater_than, Parameter(x), Constant(5)))
    """
    return _parser.parse(func)
