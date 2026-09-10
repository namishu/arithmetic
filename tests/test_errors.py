from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import run_project_python


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (
            "from namishu_arithmetic import ArithmeticApp; "
            "ArithmeticApp().generate(series='bad', level=1, output_path='bad.pdf', pages=1)",
            "series must be one of",
        ),
        (
            "from namishu_arithmetic import ArithmeticApp; "
            "ArithmeticApp().generate(series='addsub', level=0, output_path='bad.pdf', pages=1)",
            "invalid level",
        ),
        (
            "from namishu_arithmetic import ArithmeticApp; "
            "ArithmeticApp().generate(series='addsub', level=1, output_path='bad.pdf', pages=0)",
            "invalid pages",
        ),
        (
            "from namishu_arithmetic.addition_subtraction.generator import AddSubGenerator; "
            "AddSubGenerator({}).generate(25, 1)",
            "invalid addsub level",
        ),
        (
            "from namishu_arithmetic.multiplication_division.generator import MulDivGenerator; "
            "MulDivGenerator({}).generate(27, 1)",
            "invalid muldiv level",
        ),
        (
            "from namishu_arithmetic.fractions.generator import FractionGenerator; "
            "FractionGenerator({}).generate(19, 1)",
            "invalid fraction level",
        ),
        (
            "from namishu_arithmetic.operands import generate_operands; generate_operands(1, 1, 0, 1, 'bad')",
            "value_type must be",
        ),
        (
            "from namishu_arithmetic.operators import generate_operators; generate_operators(1, 3, ['+', '-'])",
            "operator_count cannot exceed",
        ),
        (
            "from namishu_arithmetic.formatter import format_problems; format_problems([[1]], [['+', '=']])",
            "operand and operator counts",
        ),
        (
            "from namishu_arithmetic.evaluator import evaluate_formula; evaluate_formula('abs(1)')",
            "unsupported formula",
        ),
    ],
)
def test_rejects_invalid_inputs(code: str, expected: str) -> None:
    run_project_python("arithmetic", code, check=False, expect=[expected])


def test_rejects_invalid_problems_per_page_config(tmp_path: Path) -> None:
    config_path = tmp_path / "bad_arithmetic_config.yaml"
    config_path.write_text("problems_per_page:\n  default: 0\n", encoding="utf-8")

    run_project_python(
        "arithmetic",
        f"from namishu_arithmetic import ArithmeticApp; ArithmeticApp(config_path={str(config_path)!r})",
        check=False,
        expect=["config.problems_per_page.default must be > 0"],
    )


def test_rejects_invalid_diversity_config(tmp_path: Path) -> None:
    config_path = tmp_path / "bad_arithmetic_diversity.yaml"
    config_path.write_text("diversity:\n  candidate_multiplier: 0\n", encoding="utf-8")

    run_project_python(
        "arithmetic",
        f"from namishu_arithmetic import ArithmeticApp; ArithmeticApp(config_path={str(config_path)!r})",
        check=False,
        expect=["config.diversity.candidate_multiplier must be > 0"],
    )
