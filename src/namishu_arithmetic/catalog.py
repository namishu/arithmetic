"""Public level metadata shared by the CLI and generated documentation."""

from __future__ import annotations

import json
from pathlib import Path

from .app import ArithmeticApp
from .series import get_series_spec


def list_levels(series: str | None = None) -> list[dict]:
    records = json.loads((Path(__file__).parent / "data/catalog.json").read_text(encoding="utf-8"))["levels"]
    if series is not None:
        code = get_series_spec(series).code
        records = [record for record in records if record["series"] == code]
    return records


def describe_level(series: str, level: int) -> dict:
    spec = get_series_spec(series)
    spec.validate_level(level)
    record = next(item for item in list_levels(spec.code) if item["level"] == level)
    record["examples"] = ArithmeticApp().generate_pages(spec.code, level, pages=1, seed=42)[0][:3]
    record["example_seed"] = 42
    record["command"] = (
        f"arithmetic generate --series {spec.code} --level {level} --pages 1 "
        f"--seed 42 --output worksheets/{spec.code}-level-{level}.pdf"
    )
    record["notes"] = {
        "en": "Source ranges do not necessarily bound displayed values or answers. "
        "Normal mode requires defined expressions and unique rational solutions for blanks.",
        "zh-CN": "源数范围不一定限制最终显示数或答案。普通模式只保留有定义的算式和具有唯一有理数解的填空题。",
    }
    return record
