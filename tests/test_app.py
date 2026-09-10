from __future__ import annotations

from pathlib import Path

from tests.support import assert_pdf_created, run_project_python


def test_generate_pages_exposes_page_content() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic import ArithmeticApp; "
        "pages = ArithmeticApp().generate_pages(series='addsub', level=1, pages=2, seed=123); "
        "assert len(pages) == 2; "
        "assert all(len(page) == 10 for page in pages)",
    )


def test_generate_pdf_with_pages_and_seed(tmp_path: Path) -> None:
    output_path = tmp_path / "basic_fraction_variant.pdf"

    run_project_python(
        "arithmetic",
        "from namishu_arithmetic import ArithmeticApp; "
        f"ArithmeticApp().generate(series='fraction', level=1, output_path={str(output_path)!r}, pages=2, seed=999)",
    )

    assert_pdf_created(output_path)


def test_seed_does_not_mutate_global_random_state(tmp_path: Path) -> None:
    run_project_python(
        "arithmetic",
        "import random; "
        "import numpy as np; "
        "from namishu_arithmetic import ArithmeticApp; "
        "random.seed(2026); np.random.seed(2026); "
        "expected_py = random.random(); expected_np = np.random.random(); "
        "random.seed(2026); np.random.seed(2026); "
        f"ArithmeticApp().generate(series='muldiv', level=25, output_path={str(tmp_path / 'random.pdf')!r}, "
        "pages=1, seed=123); "
        "assert random.random() == expected_py; "
        "assert np.random.random() == expected_np",
    )


def test_config_override_merges_with_defaults(tmp_path: Path) -> None:
    config_path = tmp_path / "arithmetic_override.yaml"
    config_path.write_text(
        "problems_per_page:\n  default: 7\ndiversity:\n  candidate_multiplier: 2\n",
        encoding="utf-8",
    )

    run_project_python(
        "arithmetic",
        "from pathlib import Path; "
        "from namishu_arithmetic import ArithmeticApp; "
        f"app = ArithmeticApp(config_path=Path({str(config_path)!r})); "
        "assert 'page' in app.layout_cfg; "
        "pages = app.generate_pages(series='addsub', level=1, pages=1, seed=123); "
        "assert len(pages) == 1; "
        "assert len(pages[0]) == 7; "
        "assert app.main_cfg['diversity']['candidate_multiplier'] == 2",
    )


def test_app_normalizes_series(tmp_path: Path) -> None:
    output_path = tmp_path / "arithmetic_normalized_series.pdf"

    run_project_python(
        "arithmetic",
        "from namishu_arithmetic import ArithmeticApp; "
        f"ArithmeticApp().generate(series=' AddSub ', level=1, output_path={str(output_path)!r}, pages=1, seed=123)",
    )

    assert_pdf_created(output_path)
