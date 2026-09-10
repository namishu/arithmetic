from __future__ import annotations

from pathlib import Path

from tests.support import assert_pdf_created, run_project_python


def test_all_series_levels_generate(tmp_path: Path) -> None:
    run_project_python(
        "arithmetic",
        "from pathlib import Path; "
        "from namishu_arithmetic import ArithmeticApp, SERIES_SPECS; "
        f"tmp_dir = Path({str(tmp_path)!r}); "
        "app = ArithmeticApp()\n"
        "for spec in SERIES_SPECS:\n"
        "    for level in spec.levels:\n"
        "        app.generate(series=spec.code, level=level, "
        "output_path=tmp_dir / f'basic_{spec.code}_{level}.pdf', pages=1, seed=123)",
    )

    pdfs = list(tmp_path.glob("basic_*.pdf"))
    assert len(pdfs) == 68
    for pdf in pdfs:
        assert_pdf_created(pdf)


def test_series_specs_match_generator_levels() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic import SERIES_SPECS\n"
        "for spec in SERIES_SPECS:\n"
        "    generator_levels = sorted(spec.generator_cls.level_map)\n"
        "    spec_levels = list(spec.levels)\n"
        "    assert generator_levels == spec_levels, (spec.code, generator_levels, spec_levels)",
    )


def test_addsub_key_level_shapes() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic.addition_subtraction.generator import AddSubGenerator; "
        "generator = AddSubGenerator({'seed': 123}); "
        "level2 = generator.generate(2, 50); "
        "assert all(' - ' in problem and problem.endswith('=') for problem in level2)\n"
        "for problem in level2:\n"
        "    left, right = [int(part.strip()) for part in problem[:-1].split('-')]\n"
        "    assert left - right >= 0\n"
        "level21 = generator.generate(21, 50); "
        "assert all((' + __ = ' in problem or ' - __ = ' in problem) for problem in level21)",
    )


def test_fraction_page_capacity_overrides() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic.fractions.generator import FractionGenerator; "
        "generator = FractionGenerator({'default_problems_per_page': 9}); "
        "assert generator.page_capacity(1) == 9\n"
        "for level in [8, 9, 17, 18]:\n"
        "    assert generator.page_capacity(level) == 12",
    )


def test_muldiv_four_operation_division_is_nonzero() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic.multiplication_division.generator import MulDivGenerator; "
        "generator = MulDivGenerator({'seed': 123}); "
        "problems = []\n"
        "for level in [23, 24, 25, 26]:\n"
        "    problems.extend(generator.generate(level, 200))\n"
        "assert all('÷ 0' not in problem for problem in problems)",
    )


def test_generators_are_deterministic() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic.addition_subtraction.generator import AddSubGenerator; "
        "from namishu_arithmetic.fractions.generator import FractionGenerator; "
        "a = AddSubGenerator({'seed': 123}).generate(3, 8); "
        "b = AddSubGenerator({'seed': 123}).generate(3, 8); "
        "assert a == b; "
        "f = FractionGenerator({'default_problems_per_page': 9}); "
        "assert f.page_capacity(1) == 9; "
        "assert f.page_capacity(8) == 12",
    )
