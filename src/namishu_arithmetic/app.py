from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .diversity import DiversityConfig, select_diverse_pages
from .evaluator import is_valid_problem
from .renderer import WorksheetRenderer
from .series import SeriesSpec, get_series_spec
from .yaml import load_yaml


@dataclass(frozen=True)
class WorksheetRequest:
    series: SeriesSpec
    level: int
    pages: int
    seed: int
    allow_undefined: bool = False


class ArithmeticApp:
    def __init__(self, config_path: str | Path | None = None):
        self.project_dir = Path(__file__).resolve().parent / "data"
        self.config_path = self.project_dir / "main.yaml"
        self.main_cfg = load_yaml(self.config_path)

        if config_path is not None:
            override_cfg = load_yaml(Path(config_path).resolve())
            self.main_cfg = self._merge_dict(self.main_cfg, override_cfg)

        if config_path is not None:
            font_path = override_cfg.get("layout", {}).get("typography", {}).get("font_path")
            if font_path:
                resolved = Path(config_path).resolve().parent / font_path
                self.main_cfg["layout"]["typography"]["font_path"] = str(resolved)

        self._validate_main_config(self.main_cfg)

        self.layout_cfg = self.main_cfg["layout"]

    def generate(
        self,
        series: str,
        level: int,
        output_path: str | Path,
        pages: int = 10,
        seed: int | None = None,
        allow_undefined: bool = False,
    ) -> Path:
        request = self._request(series=series, level=level, pages=pages, seed=seed, allow_undefined=allow_undefined)
        page_items = self._generate_pages_from_request(request)

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        WorksheetRenderer(
            layout_config=self.layout_cfg,
            series_label=request.series.display_name,
            level_label=f"Level {request.level}",
            generated_on=date.today().isoformat(),
            project_dir=self.project_dir,
            teaching_mode=request.allow_undefined,
        ).render(page_items, output)
        return output

    def generate_pages(
        self,
        series: str,
        level: int,
        pages: int = 10,
        seed: int | None = None,
        allow_undefined: bool = False,
    ) -> list[list[str]]:
        request = self._request(series=series, level=level, pages=pages, seed=seed, allow_undefined=allow_undefined)
        return self._generate_pages_from_request(request)

    def _generate_pages_from_request(self, request: WorksheetRequest) -> list[list[str]]:
        generator = request.series.generator_cls(self._series_cfg(request.series.code, request.seed))
        page_size = generator.page_capacity(request.level)
        if page_size <= 0:
            raise ValueError(f"invalid page capacity for series '{request.series.code}': {page_size}")

        diversity_cfg = DiversityConfig.from_config(self.main_cfg.get("diversity"))
        candidate_count = request.pages * page_size * diversity_cfg.candidate_multiplier
        for _ in range(6):
            candidates = [
                problem
                for problem in generator.generate(request.level, candidate_count)
                if is_valid_problem(problem, allow_undefined=request.allow_undefined)
            ]
            if len(candidates) >= request.pages * page_size:
                break
            candidate_count *= 2
        else:
            raise ValueError("could not generate enough valid problems; reduce pages or change level")
        return select_diverse_pages(
            candidates,
            page_size=page_size,
            page_count=request.pages,
            config=diversity_cfg,
        )

    def _request(
        self, series: str, level: int, pages: int, seed: int | None, allow_undefined: bool = False
    ) -> WorksheetRequest:
        if not isinstance(level, int) or level <= 0:
            raise ValueError(f"invalid level: {level}")
        if not isinstance(pages, int) or pages <= 0:
            raise ValueError(f"invalid pages: {pages}")

        spec = get_series_spec(series)
        spec.validate_level(level)
        return WorksheetRequest(
            series=spec, level=level, pages=pages, seed=self._resolve_seed(seed), allow_undefined=allow_undefined
        )

    def _series_cfg(self, series_code: str, seed: int) -> dict[str, int]:
        ppp = self.main_cfg["problems_per_page"]
        default_ppp = int(ppp["default"])
        series_ppp = int(ppp.get(series_code, default_ppp))

        return {
            "seed": int(seed),
            "default_problems_per_page": series_ppp,
        }

    def _resolve_seed(self, seed: int | None) -> int:
        if seed is not None:
            return int(seed)
        return int(time.time_ns() % (2**32 - 1))

    def _merge_dict(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        merged: dict[str, Any] = dict(base)
        for key, override_val in override.items():
            if isinstance(override_val, dict) and isinstance(merged.get(key), dict):
                merged[key] = self._merge_dict(merged[key], override_val)
            else:
                merged[key] = override_val
        return merged

    def _validate_main_config(self, cfg: dict[str, Any]) -> None:
        if not isinstance(cfg, dict):
            raise ValueError("config must be a YAML mapping")

        layout = cfg.get("layout")
        if not isinstance(layout, dict):
            raise ValueError("config.layout must be a mapping")

        required_layout_sections = ["page", "margin", "header", "footer", "typography"]
        for section in required_layout_sections:
            if section not in layout or not isinstance(layout[section], dict):
                raise ValueError(f"config.layout.{section} must be a mapping")

        ppp = cfg.get("problems_per_page")
        if not isinstance(ppp, dict) or "default" not in ppp:
            raise ValueError("config.problems_per_page.default is required")

        default_ppp = int(ppp["default"])
        if default_ppp <= 0:
            raise ValueError("config.problems_per_page.default must be > 0")

        for key, val in ppp.items():
            page_count = int(val)
            if page_count <= 0:
                raise ValueError(f"config.problems_per_page.{key} must be > 0")

        diversity = cfg.get("diversity", {})
        if diversity is not None and not isinstance(diversity, dict):
            raise ValueError("config.diversity must be a mapping")
        diversity_cfg = DiversityConfig.from_config(diversity)
        if diversity_cfg.candidate_multiplier <= 0:
            raise ValueError("config.diversity.candidate_multiplier must be > 0")
        if diversity_cfg.max_same_leading_operand_per_page <= 0:
            raise ValueError("config.diversity.max_same_leading_operand_per_page must be > 0")
        if diversity_cfg.max_special_operand_per_page < 0:
            raise ValueError("config.diversity.max_special_operand_per_page must be >= 0")
