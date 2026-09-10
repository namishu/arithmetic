from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .addition_subtraction.generator import AddSubGenerator
from .fractions.generator import FractionGenerator
from .multiplication_division.generator import MulDivGenerator


class ProblemGenerator(Protocol):
    def generate(self, level: int, count: int) -> list[str]: ...

    def page_capacity(self, level: int) -> int: ...


@dataclass(frozen=True)
class SeriesSpec:
    code: str
    display_name: str
    generator_cls: type[ProblemGenerator]
    first_level: int
    last_level: int

    @property
    def levels(self) -> range:
        return range(self.first_level, self.last_level + 1)

    def validate_level(self, level: int) -> None:
        if level not in self.levels:
            raise ValueError(f"invalid {self.code} level: {level}")


SERIES_SPECS: tuple[SeriesSpec, ...] = (
    SeriesSpec("addsub", "Addition & Subtraction", AddSubGenerator, 1, 24),
    SeriesSpec("muldiv", "Multiplication & Division", MulDivGenerator, 1, 26),
    SeriesSpec("fraction", "Fractions, Decimals & Mixed Numbers", FractionGenerator, 1, 18),
)

_SERIES_BY_CODE = {spec.code: spec for spec in SERIES_SPECS}


def series_choices() -> list[str]:
    return [spec.code for spec in SERIES_SPECS]


def get_series_spec(series: str) -> SeriesSpec:
    series_code = normalize_series(series)
    try:
        return _SERIES_BY_CODE[series_code]
    except KeyError as exc:
        choices = ", ".join(series_choices())
        raise ValueError(f"series must be one of {{{choices}}}") from exc


def normalize_series(series: str) -> str:
    return str(series).strip().lower()
