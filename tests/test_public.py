from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest
from pypdf import PdfReader

from namishu_arithmetic import SERIES_SPECS, ArithmeticApp
from namishu_arithmetic.catalog import describe_level, list_levels
from namishu_arithmetic.evaluator import evaluate_formula, is_valid_problem, solve_blank


def cli(*args, cwd=None):
    return subprocess.run(
        [sys.executable, "-m", "namishu_arithmetic", *map(str, args)], capture_output=True, text=True, cwd=cwd
    )


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("1/2 ÷ 3/4", Fraction(2, 3)),
        (" 0.1 + 0.2 ", Fraction(3, 10)),
        ("7 ÷ 2", Fraction(7, 2)),
        ("-1/2 ÷ (-3/4)", Fraction(2, 3)),
        ("(2 + 3) × (4 - 7)", Fraction(-15)),
    ],
)
def test_exact_arithmetic(expression, expected):
    assert evaluate_formula(expression) == expected


@pytest.mark.parametrize(
    ("problem", "expected"),
    [
        ("40 + __ = 7", -33),
        ("__ - 1 = 17", 18),
        ("1/2 ÷ __ = 3/4", Fraction(2, 3)),
        ("(-6 + __) × (-1) = 15", -9),
        ("2 × 3 - 8 ÷ __ = 2", 2),
        ("__ × 0.1 = 0.3", 3),
    ],
)
def test_unique_solutions(problem, expected):
    assert solve_blank(problem) == expected


@pytest.mark.parametrize(
    "problem",
    [
        "1 ÷ 0 =",
        "1 ÷ 0/4 =",
        "0 × __ = 0",
        "0 × __ = 1",
        "0 ÷ __ = 0",
        "1 ÷ __ = 0",
        "__ ÷ 0 = 1",
        "__ + 2 =",
        "3 × 4 = 11",
        "1 + 2 = 4",
        "__ ÷ 0/4 = 1",
    ],
)
def test_invalid_equations_are_rejected(problem):
    assert not is_valid_problem(problem)


def test_undefined_mode_is_explicit(monkeypatch):
    with pytest.raises(ZeroDivisionError):
        evaluate_formula("1 ÷ 0")
    assert is_valid_problem("1 ÷ 0 =", allow_undefined=True)
    assert not is_valid_problem("__ ÷ 0 = 1", allow_undefined=True)
    app = ArithmeticApp()
    normal = app.generate_pages("muldiv", 5, pages=2, seed=42)
    assert all(is_valid_problem(p) for page in normal for p in page)
    from namishu_arithmetic.multiplication_division.generator import MulDivGenerator

    monkeypatch.setattr(MulDivGenerator, "generate", lambda self, level, count: ["1 ÷ 0 ="] * count)
    teaching = app.generate_pages("muldiv", 5, pages=1, seed=42, allow_undefined=True)
    assert all(p == "1 ÷ 0 =" for p in teaching[0])
    with pytest.raises(ValueError, match="could not generate enough"):
        app.generate_pages("muldiv", 5, pages=1, seed=42)


@pytest.mark.parametrize("seed", [0, 42, 2026])
def test_all_presets_produce_valid_complete_pages(seed):
    app = ArithmeticApp()
    for spec in SERIES_SPECS:
        generator = spec.generator_cls(app._series_cfg(spec.code, seed))
        for level in spec.levels:
            pages = app.generate_pages(spec.code, level, pages=1, seed=seed)
            assert len(pages[0]) == generator.page_capacity(level), (spec.code, level)
            for problem in pages[0]:
                assert is_valid_problem(problem), (spec.code, level, problem)
                if "__" in problem:
                    answer = solve_blank(problem)
                    left, right = problem.replace("__", f"({answer})").split("=")
                    assert evaluate_formula(left) == evaluate_formula(right)


def test_catalog_matches_public_presets():
    records = list_levels()
    expected = {(spec.code, level) for spec in SERIES_SPECS for level in spec.levels}
    assert {(r["series"], r["level"]) for r in records} == expected
    assert len(records) == 68
    app = ArithmeticApp()
    for record in records:
        spec = next(s for s in SERIES_SPECS if s.code == record["series"])
        actual = spec.generator_cls(app._series_cfg(spec.code, 42)).page_capacity(record["level"])
        assert record["default_problems_per_page"] == actual
        assert record["rules"]["en"] and record["rules"]["zh-CN"]
    assert len(describe_level("fraction", 10)["examples"]) == 3


def test_cli_json_generation_from_unrelated_directory(tmp_path):
    result = cli(
        "generate",
        "--series",
        "fraction",
        "--level",
        10,
        "--pages",
        2,
        "--seed",
        42,
        "--output",
        "decimal.pdf",
        "--json",
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stderr
    item = json.loads(result.stdout)["files"][0]
    assert Path(item["output"]) == tmp_path / "decimal.pdf"
    assert item["seed"] == 42 and item["problems_per_page"] == 14
    reader = PdfReader(item["output"])
    assert len(reader.pages) == 2
    assert "Level 10" in reader.pages[0].extract_text()
    before = (tmp_path / "decimal.pdf").read_bytes()
    result = cli("generate", "--output", "decimal.pdf", cwd=tmp_path)
    assert result.returncode == 2 and "already exists" in result.stderr
    assert (tmp_path / "decimal.pdf").read_bytes() == before


def test_cli_discovery_and_errors():
    result = cli("list", "--json")
    assert result.returncode == 0
    assert len(json.loads(result.stdout)["levels"]) == 68
    result = cli("describe", "--series", "fraction", "--level", 10, "--json")
    assert json.loads(result.stdout)["operand_types"] == ["decimal"]
    result = cli("generate", "--all", "--output", "one.pdf")
    assert result.returncode == 2 and "cannot be combined" in result.stderr
    result = cli("describe", "--series", "addsub", "--level", 99)
    assert result.returncode == 2 and "invalid addsub level" in result.stderr


def test_cli_batch_generates_all_levels(tmp_path):
    result = cli("generate", "--all", "--pages", 1, "--seed", 42, "--output-dir", tmp_path / "all", "--json")
    assert result.returncode == 0, result.stderr
    files = json.loads(result.stdout)["files"]
    assert len(files) == 68
    assert len(list((tmp_path / "all").rglob("*.pdf"))) == 68
    for item in files:
        assert len(PdfReader(item["output"]).pages) == 1


def test_config_path_and_standard_font_override(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "custom.yaml").write_text(
        "layout:\n  typography:\n    font_name: Times-Roman\nproblems_per_page:\n  default: 7\n",
        encoding="utf-8",
    )
    result = cli("generate", "--config", "config/custom.yaml", "--pages", 1, "--json", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    item = json.loads(result.stdout)["files"][0]
    assert item["problems_per_page"] == 7
    fonts = PdfReader(item["output"]).pages[0]["/Resources"]["/Font"]
    assert any(font.get_object()["/BaseFont"] == "/Times-Roman" for font in fonts.values())


def test_default_pdf_has_symbols_without_embedded_fonts(tmp_path):
    app = ArithmeticApp()
    for series, level, symbol in [("muldiv", 1, "×"), ("muldiv", 5, "÷"), ("fraction", 1, "/")]:
        path = app.generate(series, level, tmp_path / f"{series}-{level}.pdf", pages=1, seed=42)
        page = PdfReader(path).pages[0]
        assert symbol in page.extract_text()
        for font_ref in page["/Resources"]["/Font"].values():
            font = font_ref.get_object()
            assert font["/BaseFont"] == "/Helvetica"
            descriptor = font.get("/FontDescriptor", {})
            if hasattr(descriptor, "get_object"):
                descriptor = descriptor.get_object()
            assert not any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3"))


def test_teaching_pdf_is_labeled(tmp_path):
    path = ArithmeticApp().generate("muldiv", 5, tmp_path / "teaching.pdf", pages=1, allow_undefined=True)
    assert "Identify undefined expressions" in PdfReader(path).pages[0].extract_text()
