from __future__ import annotations

import numpy as np

from ..evaluator import evaluate_formula
from ..formatter import format_problems
from ..level_generator import LevelGenerator
from ..operands import generate_operands
from ..operators import generate_operators
from ..placeholders import insert_blank
from ..specs import LevelSpec, OperandBlock, OperatorBlock


def _int_rows(count: int, columns: int, lower: int, upper: int) -> list[list[int]]:
    return generate_operands(count=count, columns=columns, lower=lower, upper=upper, value_type="int")


def _int_column(count: int, lower: int, upper: int):
    return np.array(_int_rows(count, 1, lower, upper))


def _repeat_operators(count: int, pattern: list[str]) -> list[list[str]]:
    return [pattern] * count


def _operator_rows(count: int, operator_count: int, choices: list[str] | set[str], *, distinct: bool = True):
    return generate_operators(count=count, operator_count=operator_count, choices=choices, distinct=distinct)


def _shuffled_subset(problems: list[str], count: int) -> list[str]:
    np.random.shuffle(problems)
    return problems[:count]


def _mix_variants(count: int, variant_count: int, *factories) -> list[str]:
    per_variant_count = count // variant_count + 1
    problems: list[str] = []
    for factory in factories:
        problems.extend(factory(per_variant_count))
    return _shuffled_subset(problems, count)


def _replace_zero_dividends(dividends, divisors, upper: int) -> list[int]:
    return [np.random.randint(0, upper) if divisors[index] == 0 else dividends[index] for index in range(len(divisors))]


def _multiplication_blank_rows(rows: list[list[int]]) -> list[list[int]]:
    return [[left_factor, left_factor * hidden_factor] for left_factor, hidden_factor in rows]


def _division_from_factors(rows: list[list[int]]) -> list[list[int]]:
    return [[divisor * quotient, divisor] for divisor, quotient in rows]


def _make_first_division_integral(operands: list[int], operators) -> list[int]:
    adjusted = list(operands)
    for index, operator in enumerate(operators):
        if operator == "÷":
            divisor = adjusted[index + 1]
            if divisor == 0:
                nonzero_values = [abs(value) for value in adjusted if value != 0]
                adjusted[index + 1] = nonzero_values[0] if nonzero_values else 1
                divisor = adjusted[index + 1]
            adjusted[index] *= divisor
            break
    return adjusted


def _make_rows_with_integral_division(rows: list[list[int]], operators) -> list[list[int]]:
    return [_make_first_division_integral(row, operator_row) for row, operator_row in zip(rows, operators, strict=True)]


def _generate_division_blank_problems(
    count: int,
    lower: int,
    upper: int,
) -> list[str]:
    divisor = np.array(generate_operands(count=count, columns=1, lower=lower, upper=upper, value_type="int"))
    quotient = np.array(generate_operands(count=count, columns=1, lower=lower, upper=upper, value_type="int"))
    dividend = divisor * quotient

    hidden_divisor_rows = np.hstack((dividend, [["__"]] * count, quotient))
    hidden_divisor = format_problems(hidden_divisor_rows, [["÷", "="]] * count, skip_wrap_positions={0, 2})

    hidden_dividend_rows = np.hstack(([["__"]] * count, divisor, quotient))
    hidden_dividend = format_problems(hidden_dividend_rows, [["÷", "="]] * count, skip_wrap_positions={0, 2})

    problems = hidden_divisor + hidden_dividend
    np.random.shuffle(problems)
    return problems[:count]


def _generate_four_operation_blank_problem(lower: int, upper: int) -> str:
    operands = generate_operands(
        count=1,
        columns=4,
        lower=lower,
        upper=upper,
        value_type="int",
    )[0]
    operators = generate_operators(1, 3, choices={"+", "-", "×", "÷"})[0]
    operands = _make_first_division_integral(operands, operators)

    formula = format_problems([operands], [operators])[0]
    result = str(evaluate_formula(formula.removesuffix("=").strip()))
    operands[np.random.randint(0, 4)] = "__"
    operands.append(result)
    operators.append("=")
    return format_problems([operands], [operators])[0]


class MulDivGenerator(LevelGenerator):
    series_code = "muldiv"
    default_seed = 2001
    default_page_capacity = 12


class MultL5:
    """
    除法基础（非负） c÷a, a是1位数，非负
    注意：除数等于0的情况没有排除，这不是BUG。
    """

    def __init__(self):
        self.upper = 9

    def generate(self, count):
        factors = np.array(_int_rows(count, 2, 0, self.upper))
        divisor, quotient = factors[:, 0], factors[:, 1]
        dividend = _replace_zero_dividends(divisor * quotient, divisor, self.upper)
        rows = np.array([dividend, divisor]).T
        return format_problems(rows, _repeat_operators(count, ["÷", "="]))


class MultL6:
    """
    除法基础（非负） c÷a, a是1位数
    注意：除数等于0的情况没有排除，这不是BUG。
    """

    def __init__(self):
        self.upper = 9

    def generate(self, count):
        factors = np.array(_int_rows(count, 2, -self.upper, self.upper))
        divisor, quotient = factors[:, 0], factors[:, 1]
        dividend = _replace_zero_dividends(divisor * quotient, divisor, self.upper)
        rows = np.array([dividend, divisor]).T
        return format_problems(rows, _repeat_operators(count, ["÷", "="]))


class MultL7:
    """
    除法填空 c÷__=b 或 __÷a=b, ab是1位数，非负
    注意：除数等于0的情况没有排除，这不是BUG。
    """

    def __init__(self):
        self.upper = 9

    def generate(self, count):
        return _generate_division_blank_problems(count, 0, self.upper)


class MultL8:
    """
    除法填空 c÷__=b 或 __÷a=b, ab是1位数
    注意：除数等于0的情况没有排除，这不是BUG。
    """

    def __init__(self):
        self.upper = 9

    def generate(self, count):
        return _generate_division_blank_problems(count, -self.upper, self.upper)


class MultL9:
    """
    乘法加减 a×b+c×d 或 a×b-c×d, abcd是1位数
    """

    def __init__(self):
        self.upper = 9

    def generate(self, count):
        rows = _int_rows(count, 4, -self.upper, self.upper)
        operators = np.hstack(
            (
                [["×"]] * count,
                _operator_rows(count, 1, ["+", "-"]),
                [["×", "="]] * count,
            )
        )
        return format_problems(rows, operators)


class MultL10:
    """
    乘法填空 a×__+c×d=e 或 a×b-__×d=e, abcd是1位数
    """

    def __init__(self):
        self.upper = 9

    def _hidden_second_factor_after_plus(self, count):
        left_factor = _int_column(count, -self.upper, self.upper)
        hidden_factor = _int_column(count, -self.upper, self.upper)
        right_left_factor = _int_column(count, -self.upper, self.upper)
        right_right_factor = _int_column(count, -self.upper, self.upper)
        result = left_factor * hidden_factor + right_left_factor * right_right_factor
        rows = np.hstack((left_factor, [["__"]] * count, right_left_factor, right_right_factor, result))
        return format_problems(rows, _repeat_operators(count, ["×", "+", "×", "="]), skip_wrap_positions={0, 4})

    def _hidden_left_factor_after_minus(self, count):
        left_factor = _int_column(count, -self.upper, self.upper)
        right_factor = _int_column(count, -self.upper, self.upper)
        hidden_factor = _int_column(count, -self.upper, self.upper)
        final_factor = _int_column(count, -self.upper, self.upper)
        result = left_factor * right_factor - hidden_factor * final_factor
        rows = np.hstack((left_factor, right_factor, [["__"]] * count, final_factor, result))
        return format_problems(rows, _repeat_operators(count, ["×", "-", "×", "="]), skip_wrap_positions={0, 4})

    def generate(self, count):
        return _mix_variants(count, 2, self._hidden_second_factor_after_plus, self._hidden_left_factor_after_minus)


class MultL11:
    """
    四则运算 a×b+c÷d 或 a×b-c÷d, abd是一位数
    注意：除数等于0的情况没有排除，这不是BUG。
    """

    def __init__(self):
        self.upper = 9

    def generate(self, count):
        source = np.array(_int_rows(count, 4, -self.upper, self.upper))
        left_factor, right_factor, quotient, divisor = source[:, 0], source[:, 1], source[:, 2], source[:, 3]
        dividend = _replace_zero_dividends(divisor * quotient, divisor, self.upper)
        rows = np.array([left_factor, right_factor, dividend, divisor]).T
        operators = np.hstack(
            (
                [["×"]] * count,
                _operator_rows(count, 1, ["+", "-"]),
                [["÷", "="]] * count,
            )
        )
        return format_problems(rows, operators)


class MultL12:
    """
    四则填空 a×__+c÷d=e 或 a×b-c÷__=e 或 a×b+__÷d=e, abd是一位数。
    注意：除数等于0的情况没有排除，这不是BUG。
    """

    def __init__(self):
        self.upper = 9

    def _hidden_multiplier_plus_division(self, count):
        source = np.array(_int_rows(count, 4, -self.upper, self.upper))
        left_factor, hidden_factor, quotient, divisor = source[:, 0], source[:, 1], source[:, 2], source[:, 3]
        dividend = _replace_zero_dividends(divisor * quotient, divisor, self.upper)
        result = left_factor * hidden_factor + quotient
        rows = np.array([left_factor, dividend, divisor, result]).T
        return format_problems(rows, _repeat_operators(count, ["× __ +", "÷", "="]), skip_wrap_positions={0, 3})

    def _hidden_divisor_after_minus(self, count):
        source = np.array(_int_rows(count, 4, -self.upper, self.upper))
        left_factor, right_factor, quotient, divisor = source[:, 0], source[:, 1], source[:, 2], source[:, 3]
        dividend = quotient * divisor
        result = left_factor * right_factor - quotient
        rows = np.array([left_factor, right_factor, dividend, result]).T
        return format_problems(rows, _repeat_operators(count, ["×", "-", "÷ __ ="]), skip_wrap_positions={0, 3})

    def _hidden_dividend_after_plus(self, count):
        source = np.array(_int_rows(count, 4, -self.upper, self.upper))
        left_factor, right_factor, quotient, divisor = source[:, 0], source[:, 1], source[:, 2], source[:, 3]
        result = left_factor * right_factor + quotient
        rows = np.array([left_factor, right_factor, divisor, result]).T
        return format_problems(rows, _repeat_operators(count, ["×", "+ __ ÷", "="]), skip_wrap_positions={0, 3})

    def generate(self, count):
        return _mix_variants(
            count,
            3,
            self._hidden_multiplier_plus_division,
            self._hidden_divisor_after_minus,
            self._hidden_dividend_after_plus,
        )


class MultL13:
    """
    乘法加减 a×(b+c) 或 a×(b-c), abc是1位数, c非负
    """

    def __init__(self):
        self.upper = 9

    def generate(self, count):
        left_terms = _int_rows(count, 2, -self.upper, self.upper)
        parenthesized_term = _int_column(count, -self.upper, self.upper)
        rows = np.hstack((left_terms, parenthesized_term))
        operators = np.hstack(
            (
                [["×"]] * count,
                _operator_rows(count, 1, ["+", "-"]),
                [["="]] * count,
            )
        )
        return format_problems(rows, operators, skip_wrap_positions={0, 1}, parentheses_pairs={(2, 4)})


class MultL14:
    """
    四则填空 (a+__)×c=d 或 (a-__)×c=d, acd是一位数。
    """

    def __init__(self):
        self.upper = 9

    def generate(self, count):
        source = np.array(_int_rows(count, 3, -self.upper, self.upper))
        left_term, hidden_term, multiplier = source[:, 0], source[:, 1], source[:, 2]
        plus_minus_operators = _operator_rows(count, 1, ["+", "-"], distinct=False)
        result = np.array(
            [
                (
                    left_term[index] + hidden_term[index]
                    if plus_minus_operators[index][0] == "+"
                    else left_term[index] - hidden_term[index]
                )
                * multiplier[index]
                for index in range(count)
            ]
        )
        operators = np.hstack((plus_minus_operators, [["×", "="]] * count))
        rows = insert_blank(np.array([left_term, multiplier, result]).T.tolist(), 1)
        return format_problems(rows, operators, skip_wrap_positions={0, 3}, parentheses_pairs=[(0, 2)])


class MultL15:
    """
    四则运算 (a+b)×(c+d)
    abcd是一位数。
    """

    def __init__(self):
        self.upper = 9

    def generate(self, count):
        rows = _int_rows(count, 4, -self.upper, self.upper)
        operators = np.hstack(
            (
                _operator_rows(count, 1, ["+", "-"]),
                [["×"]] * count,
                _operator_rows(count, 1, ["+", "-"]),
                [["="]] * count,
            )
        )
        return format_problems(rows, operators, skip_wrap_positions={0, 2}, parentheses_pairs=[(0, 2), (4, 6)])


class MultL16:
    """
    四则填空 (a+__)×(c+d)=e, abcd是一位数。
    """

    def __init__(self):
        self.upper = 9

    def generate(self, count):
        source = np.array(_int_rows(count, 4, -self.upper, self.upper))
        left_term = source[:, 0]
        hidden_term = source[:, 1]
        right_left_term = source[:, 2]
        right_right_term = source[:, 3]
        left_operators = _operator_rows(count, 1, ["+", "-"], distinct=False)
        right_operators = _operator_rows(count, 1, ["+", "-"], distinct=False)
        result = np.array(
            [
                (
                    left_term[index] + hidden_term[index]
                    if left_operators[index][0] == "+"
                    else left_term[index] - hidden_term[index]
                )
                * (
                    right_left_term[index] + right_right_term[index]
                    if right_operators[index][0] == "+"
                    else right_left_term[index] - right_right_term[index]
                )
                for index in range(count)
            ]
        )
        rows = insert_blank(np.array([left_term, right_left_term, right_right_term, result]).T.tolist(), 1)
        operators = np.hstack((left_operators, [["×"]] * count, right_operators, [["="]] * count))
        return format_problems(rows, operators, skip_wrap_positions={0, 2, 4}, parentheses_pairs=[(0, 2), (4, 6)])


class MultL18:
    """
    连乘填空 a×__×c=d 或 a×b×__=d
    abc是1位数
    """

    def __init__(self):
        self.upper = 9

    def _hidden_middle_factor(self, count):
        rows = _int_rows(count, 3, -self.upper, self.upper)
        rows = [[a, c, a * b * c] for a, b, c in rows]
        return format_problems(rows, _repeat_operators(count, ["× __ ×", "="]), skip_wrap_positions={0, 2})

    def _hidden_final_factor(self, count):
        rows = _int_rows(count, 3, -self.upper, self.upper)
        rows = [[a, b, a * b * c] for a, b, c in rows]
        return format_problems(rows, _repeat_operators(count, ["×", "× __ ="]), skip_wrap_positions={0, 2})

    def generate(self, count):
        return _mix_variants(count, 2, self._hidden_middle_factor, self._hidden_final_factor)


class MultL22:
    """
    除法填空 a÷__=c 或 __÷b=c, bc是两位数
    """

    def __init__(self):
        self.upper = 30

    def generate(self, count):
        return _generate_division_blank_problems(count, -self.upper, self.upper)


class MultL23:
    """
    四则运算 a @ b @ c @ d = ?
    其中 @ in {+,-,×,÷}, a,b,c,d 非负
    """

    def __init__(self):
        self.upper = 30

    def generate(self, count):
        rows = _int_rows(count, 4, 0, self.upper)
        operators = generate_operators(count=count, operator_count=3, choices=["+", "-", "×", "÷"], include_equals=True)
        rows = _make_rows_with_integral_division(rows, operators)
        return format_problems(rows, operators)


class MultL24:
    """
    四则运算 a @ b @ c @ d = ?
    其中 @ in {+,-,×,÷}, a,b,c,d 可以为负
    """

    def __init__(self):
        self.upper = 30

    def generate(self, count):
        rows = _int_rows(count, 4, -self.upper, self.upper)
        operators = generate_operators(count=count, operator_count=3, choices=["+", "-", "×", "÷"], include_equals=True)
        rows = _make_rows_with_integral_division(rows, operators)
        return format_problems(rows, operators)


class MultL25:
    """
    四则运算填空 a @ b @ c @ __ = d
    其中 @ in {+,-,×,÷}, a,b,c,d 非负，填空的位置随机
    """

    def __init__(self):
        self.upper = 30

    def generate(self, count):
        return [_generate_four_operation_blank_problem(0, self.upper) for _ in range(count)]


class MultL26:
    """四则填空：
    a@b@?@c=d, @ in {+,-,×,÷}
    """

    def __init__(self):
        self.upper = 30

    def generate(self, count):
        return [_generate_four_operation_blank_problem(-self.upper, self.upper) for _ in range(count)]


_LEVEL_MAP = {
    1: LevelSpec(OperandBlock(2, 0, 9), OperatorBlock(operators=["×", "="])),
    2: LevelSpec(OperandBlock(2, -9, 9), OperatorBlock(operators=["×", "="])),
    3: LevelSpec(
        OperandBlock(2, 0, 9),
        OperatorBlock(operators=["× __ ="]),
        transform_rows=_multiplication_blank_rows,
    ),
    4: LevelSpec(
        OperandBlock(2, -9, 9),
        OperatorBlock(operators=["× __ ="]),
        transform_rows=_multiplication_blank_rows,
        skip_wrap_positions={0, 1},
    ),
    5: MultL5,
    6: MultL6,
    7: MultL7,
    8: MultL8,
    9: MultL9,
    10: MultL10,
    11: MultL11,
    12: MultL12,
    13: MultL13,
    14: MultL14,
    15: MultL15,
    16: MultL16,
    17: LevelSpec(OperandBlock(3, -9, 9), OperatorBlock(operators=["×", "×", "="])),
    18: MultL18,
    19: LevelSpec(OperandBlock(2, -30, 30), OperatorBlock(operators=["×", "="])),
    20: LevelSpec(
        OperandBlock(2, -30, 30),
        OperatorBlock(operators=["× __ ="]),
        transform_rows=_multiplication_blank_rows,
        skip_wrap_positions={0, 1},
    ),
    21: LevelSpec(
        OperandBlock(2, -30, 30),
        OperatorBlock(operators=["÷", "="]),
        transform_rows=_division_from_factors,
    ),
    22: MultL22,
    23: MultL23,
    24: MultL24,
    25: MultL25,
    26: MultL26,
}

MulDivGenerator.level_map = _LEVEL_MAP
