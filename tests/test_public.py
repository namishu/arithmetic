from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest
from pypdf import PdfReader

from namishu_arithmetic import SERIES_SPECS, ArithmeticApp
from namishu_arithmetic.catalog import describe_level, list_levels
from namishu_arithmetic.evaluator import evaluate_formula, is_valid_problem, solve_blank


def cli(*args, cwd=None, env=None):
    return subprocess.run(
        [sys.executable, "-m", "namishu_arithmetic", *map(str, args)], capture_output=True, text=True, cwd=cwd, env=env
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
    assert not is_valid_problem(problem, allow_zero_denominator=False)


def test_zero_denominators_can_be_excluded(monkeypatch):
    with pytest.raises(ZeroDivisionError):
        evaluate_formula("1 ÷ 0")
    assert is_valid_problem("1 ÷ 0 =", allow_zero_denominator=True)
    assert not is_valid_problem("__ ÷ 0 = 1", allow_zero_denominator=True)
    app = ArithmeticApp()
    normal = app.generate_pages("muldiv", 5, pages=2, seed=42, allow_zero_denominator=False)
    assert all(is_valid_problem(p, allow_zero_denominator=False) for page in normal for p in page)
    from namishu_arithmetic.multiplication_division.generator import MulDivGenerator

    monkeypatch.setattr(MulDivGenerator, "generate", lambda self, level, count: ["1 ÷ 0 ="] * count)
    allowed = app.generate_pages("muldiv", 5, pages=1, seed=42)
    assert all(p == "1 ÷ 0 =" for p in allowed[0])
    with pytest.raises(ValueError, match="could not generate enough"):
        app.generate_pages("muldiv", 5, pages=1, seed=42, allow_zero_denominator=False)


@pytest.mark.parametrize("seed", [0, 42, 2026])
def test_all_presets_produce_valid_complete_pages(seed):
    app = ArithmeticApp()
    for spec in SERIES_SPECS:
        generator = spec.generator_cls(app._series_cfg(spec.code, seed))
        for level in spec.levels:
            pages = app.generate_pages(spec.code, level, pages=1, seed=seed, allow_zero_denominator=False)
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
        assert isinstance(record["rules"], str) and record["rules"]
        assert isinstance(record["title"], str) and record["title"]
        assert not re.search(r"[\u3400-\u9fff]", json.dumps(record, ensure_ascii=False))
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
    result = cli("generate", "--series", "fraction", "--level", 10, "--output", "decimal.pdf", cwd=tmp_path)
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
        reader = PdfReader(item["output"])
        assert len(reader.pages) == 1
        assert not re.search(r"[㐀-鿿]", reader.pages[0].extract_text())


def test_config_path_and_page_capacity_override(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "custom.yaml").write_text(
        "problems_per_page:\n  default: 7\n",
        encoding="utf-8",
    )
    result = cli(
        "generate",
        "--series",
        "addsub",
        "--level",
        1,
        "--config",
        "config/custom.yaml",
        "--pages",
        1,
        "--json",
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stderr
    item = json.loads(result.stdout)["files"][0]
    assert item["problems_per_page"] == 7


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


def test_pdf_footer_has_no_teaching_label(tmp_path):
    path = ArithmeticApp().generate("muldiv", 5, tmp_path / "teaching.pdf", pages=1, allow_zero_denominator=True)
    assert "Identify undefined expressions" not in PdfReader(path).pages[0].extract_text()


@pytest.mark.parametrize("encoding", ["cp1252", "ascii"])
@pytest.mark.parametrize(
    "command",
    [
        ("list", "--json"),
        ("describe", "--series", "fraction", "--level", "10", "--json"),
    ],
)
def test_catalog_json_is_english_with_legacy_stdout(encoding, command):
    result = cli(*command, env={**os.environ, "PYTHONIOENCODING": encoding})
    assert result.returncode == 0, result.stderr
    assert result.stdout.isascii()
    data = json.loads(result.stdout)
    assert data["schema_version"] == 2
    assert "zh-CN" not in result.stdout
    assert not re.search(r"[\u3400-\u9fff]", json.dumps(data, ensure_ascii=False))
    item = data["levels"][0] if "levels" in data else data
    assert isinstance(item["title"], str) and isinstance(item["rules"], str)
    if "notes" in item:
        assert isinstance(item["notes"], str)


def test_cli_text_is_english():
    for command in [("list",), ("describe", "--series", "addsub", "--level", "1")]:
        result = cli(*command)
        assert result.returncode == 0, result.stderr
        assert "Two-number addition" in result.stdout
        assert not re.search(r"[\u3400-\u9fff]", result.stdout)
        result = cli(*command, "--lang", "zh-CN")
        assert result.returncode == 2
        assert "unrecognized arguments" in result.stderr


@pytest.mark.parametrize("selection", [(), ("--series", "addsub"), ("--level", "1")])
def test_generate_requires_explicit_exercise(tmp_path, selection):
    result = cli("generate", *selection, cwd=tmp_path)
    assert result.returncode == 2
    assert "requires both --series and --level" in result.stderr
    assert "arithmetic list" in result.stderr and "arithmetic describe" in result.stderr
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("selection", [("--series", "addsub"), ("--level", "1")])
def test_generate_all_rejects_individual_selection(tmp_path, selection):
    result = cli("generate", "--all", *selection, cwd=tmp_path)
    assert result.returncode == 2
    assert "cannot be combined" in result.stderr
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("setting", ["font_name: Times-Roman", "font_path: custom.ttf"])
def test_font_overrides_are_rejected(tmp_path, setting):
    config = tmp_path / "font.yaml"
    config.write_text(f"layout:\n  typography:\n    {setting}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="font configuration is not supported"):
        ArithmeticApp(config_path=config)


@pytest.mark.parametrize("disallow", [False, True])
def test_cli_zero_denominator_option(tmp_path, disallow):
    args = ["--disallow-zero-denominator"] if disallow else []
    result = cli(
        "generate",
        "--series",
        "muldiv",
        "--level",
        "5",
        "--pages",
        "1",
        "--seed",
        "0",
        "--output",
        tmp_path / "division.pdf",
        "--json",
        *args,
    )
    assert result.returncode == 0, result.stderr
    manifest = json.loads(result.stdout)
    assert manifest["schema_version"] == 2
    assert manifest["files"][0]["allow_zero_denominator"] is (not disallow)

    text = PdfReader(tmp_path / "division.pdf").pages[0].extract_text()
    if disallow:
        assert "÷ 0 =" not in text
    else:
        assert "5 ÷ 0 =" in text


@pytest.mark.parametrize("problem", ["1 ÷ 0 =", "1/0 + 2 =", "3 ÷ (2 - 2) ="])
def test_zero_denominator_filter(problem):
    assert is_valid_problem(problem)
    assert not is_valid_problem(problem, allow_zero_denominator=False)
