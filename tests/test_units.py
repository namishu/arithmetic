from __future__ import annotations

import pytest

from tests.support import run_project_python


def test_operands_boundaries() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic.operands import generate_operands; "
        "assert generate_operands(0, 2, 0, 1, 'int') == []; "
        "assert generate_operands(2, 0, 0, 1, 'int') == [[], []]; "
        "rows = generate_operands(20, 2, -2, 0, 'frac'); "
        "assert all('/' in value for row in rows for value in row); "
        "assert all(int(value.split('/')[1]) >= 1 for row in rows for value in row)",
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        "dict(count=-1, columns=1, lower=0, upper=1, value_type='int')",
        "dict(count=1, columns=-1, lower=0, upper=1, value_type='int')",
        "dict(count=1, columns=1, lower=2, upper=1, value_type='int')",
    ],
)
def test_operands_reject_invalid_ranges(kwargs: str) -> None:
    run_project_python(
        "arithmetic",
        f"from namishu_arithmetic.operands import generate_operands; generate_operands(**{kwargs})",
        check=False,
        expect=["ValueError"],
    )


def test_operators_boundaries() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic.operators import generate_operators; "
        "ops = generate_operators(5, 2, ['+', '-'], include_equals=True); "
        "assert all(len(row) == 3 and row[-1] == '=' for row in ops); "
        "ops = generate_operators(5, 3, ['+', '-'], distinct=False); "
        "assert all(len(row) == 3 for row in ops); "
        "assert all(len(set(row)) < len(row) for row in ops)",
    )


def test_level_specs_generate_expected_counts() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic.specs import LevelSpec, MixedLevelSpec, OperandBlock, OperatorBlock, VariantSpec; "
        "spec = LevelSpec(OperandBlock(2, 0, 2), OperatorBlock(operators=['+', '='])); "
        "assert len(spec.generate(3)) == 3; "
        "sub = LevelSpec(OperandBlock(2, 0, 2), OperatorBlock(operators=['-', '='])); "
        "mixed = MixedLevelSpec([VariantSpec(spec), VariantSpec(sub)]); "
        "assert len(mixed.generate(5)) == 5",
    )


def test_formatter_boundaries() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic.formatter import format_problems; "
        "assert format_problems([[1, -2, '-3/4']], [['+', '=']]) == ['1 + (-2) = (-3/4)']; "
        "assert format_problems([[-1, -2]], [['+', '=']], "
        "skip_wrap_positions={0, 1}) == ['-1 + -2 =']; "
        "assert format_problems([[1, 2, 3]], [['+', '×', '=']], "
        "parentheses_pairs=[(0, 2)]) == ['(1 + 2) × 3 =']",
    )


def test_formatter_rejects_row_count_mismatch() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic.formatter import format_problems; format_problems([[1, 2]], [['+', '='], ['-', '=']])",
        check=False,
        expect=["row counts"],
    )


def test_evaluator_boundaries() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic.evaluator import evaluate_formula; "
        "assert evaluate_formula('2 × 3 + 8 ÷ 2') == 10; "
        "assert evaluate_formula('1 ÷ 2') == __import__('fractions').Fraction(1, 2)",
    )


def test_placeholder_insert_blank_does_not_mutate_input() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic.placeholders import insert_blank; "
        "rows = [[1, 2, 3]]; "
        "assert insert_blank(rows, column=1) == [[1, '__', 2, 3]]; "
        "assert rows == [[1, 2, 3]]",
    )
