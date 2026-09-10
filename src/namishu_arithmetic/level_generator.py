from __future__ import annotations

from typing import Any

from .random_state import temporary_random_seed


class LevelGenerator:
    level_map: dict[int, Any]
    series_code: str
    default_seed: int
    default_page_capacity: int

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.seed = int(config.get("seed", self.default_seed))

    def generate(self, level: int, count: int) -> list[str]:
        level_entry = self._level_entry(level)
        with temporary_random_seed(self.seed):
            if isinstance(level_entry, type):
                return level_entry().generate(count)
            return level_entry.generate(count)

    def page_capacity(self, level: int) -> int:
        level_entry = self._level_entry(level)
        configured_default = self.config.get("default_problems_per_page", self.default_page_capacity)
        level_capacity = getattr(level_entry, "page_capacity", None)
        return int(configured_default if level_capacity is None else level_capacity)

    def _level_entry(self, level: int) -> Any:
        level_entry = self.level_map.get(level)
        if level_entry is None:
            raise ValueError(f"invalid {self.series_code} level: {level}")
        return level_entry
