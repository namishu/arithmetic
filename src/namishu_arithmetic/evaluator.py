"""Exact, restricted arithmetic evaluation and one-blank equation validation."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from fractions import Fraction


def _parse(formula: str) -> ast.AST:
    # A printed fraction is one operand, including after the division sign.
    expr = re.sub(r"(?<![\w.])(\d+/\d+)(?![\w.])", r"(\1)", formula.strip())
    return ast.parse(expr.replace("×", "*").replace("÷", "/").replace("__", "x"), mode="eval").body


def evaluate_formula(formula: str) -> Fraction:
    return _evaluate(_parse(formula))


def _evaluate(node: ast.AST, value: Fraction | None = None) -> Fraction:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return Fraction(str(node.value))
    if isinstance(node, ast.Name) and node.id == "x" and value is not None:
        return value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd | ast.USub):
        operand = _evaluate(node.operand, value)
        return -operand if isinstance(node.op, ast.USub) else operand
    if isinstance(node, ast.BinOp):
        left, right = _evaluate(node.left, value), _evaluate(node.right, value)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
    raise ValueError(f"unsupported formula: {ast.dump(node)}")


@dataclass(frozen=True)
class _Unknown:
    """(a*x+b)/(c*x+d); each supported equation contains x exactly once."""

    a: Fraction = Fraction(1)
    b: Fraction = Fraction(0)
    c: Fraction = Fraction(0)
    d: Fraction = Fraction(1)


def _symbolic(node: ast.AST) -> Fraction | _Unknown:
    if isinstance(node, ast.Name) and node.id == "x":
        return _Unknown()
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd | ast.USub):
        value = _symbolic(node.operand)
        if isinstance(node.op, ast.UAdd):
            return value
        if isinstance(value, Fraction):
            return -value
        return _Unknown(-value.a, -value.b, value.c, value.d)
    if not any(isinstance(n, ast.Name) for n in ast.walk(node)):
        return _evaluate(node)
    if not isinstance(node, ast.BinOp):
        raise ValueError("unsupported blank equation")
    left, right = _symbolic(node.left), _symbolic(node.right)
    if isinstance(left, _Unknown) and isinstance(right, _Unknown):
        raise ValueError("only one blank is supported")
    f, k = (left, right) if isinstance(left, _Unknown) else (right, left)
    if not isinstance(f, _Unknown) or not isinstance(k, Fraction):
        raise ValueError("unsupported blank equation")
    a, b, c, d = f.a, f.b, f.c, f.d
    if isinstance(node.op, ast.Add):
        return _Unknown(a + k * c, b + k * d, c, d)
    if isinstance(node.op, ast.Sub):
        return _Unknown(a - k * c, b - k * d, c, d) if f is left else _Unknown(k * c - a, k * d - b, c, d)
    if isinstance(node.op, ast.Mult):
        return _Unknown(k * a, k * b, c, d)
    if isinstance(node.op, ast.Div):
        if f is left:
            if not k:
                raise ZeroDivisionError
            return _Unknown(a, b, k * c, k * d)
        return _Unknown(k * c, k * d, a, b)
    raise ValueError("unsupported blank equation")


def solve_blank(problem: str) -> Fraction:
    if problem.count("__") != 1 or problem.count("=") != 1:
        raise ValueError("expected one blank and one equals sign")
    left, right = problem.split("=")
    expr = _parse(left)
    target = evaluate_formula(right)
    function = _symbolic(expr)
    if not isinstance(function, _Unknown):
        raise ValueError("blank must appear on the left")
    coefficient = function.a - target * function.c
    if coefficient == 0:
        raise ValueError("blank has no unique solution")
    solution = (target * function.d - function.b) / coefficient
    if _evaluate(expr, solution) != target:
        raise ValueError("blank has no valid solution")
    return solution


def is_valid_problem(problem: str, *, allow_zero_denominator: bool = True) -> bool:
    try:
        if "__" in problem:
            solve_blank(problem)
        else:
            left, right = problem.split("=")
            result = evaluate_formula(left)
            if right.strip() and result != evaluate_formula(right):
                return False
        return True
    except ZeroDivisionError:
        return allow_zero_denominator and "__" not in problem
    except (ValueError, SyntaxError):
        return False
