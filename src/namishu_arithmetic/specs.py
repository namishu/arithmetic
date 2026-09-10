from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal, Protocol

import numpy as np

from .formatter import format_problems
from .operands import generate_operands
from .operators import generate_operators
from .placeholders import insert_blank

OperandType = Literal["int", "float", "frac"]


class RowSource(Protocol):
    def generate(self, count: int) -> list[list]: ...


@dataclass(frozen=True)
class OperandBlock:
    columns: int
    lower: int | float
    upper: int | float
    value_type: OperandType = "int"
    decimal_places: int = 2

    def generate(self, count: int) -> list[list]:
        return generate_operands(
            count=count,
            columns=self.columns,
            lower=self.lower,
            upper=self.upper,
            value_type=self.value_type,
            decimal_places=self.decimal_places,
        )


@dataclass(frozen=True)
class MixedOperandBlock:
    columns: int
    lower: int | float
    upper: int | float
    value_types: tuple[OperandType, ...] = ("frac", "float", "int")
    decimal_places: int = 2

    def generate(self, count: int) -> list[list]:
        rows = []
        for _ in range(count):
            row = []
            for _ in range(self.columns):
                value_type = np.random.choice(self.value_types)
                cell = generate_operands(
                    count=1,
                    columns=1,
                    lower=self.lower,
                    upper=self.upper,
                    value_type=value_type,
                    decimal_places=self.decimal_places,
                )[0][0]
                row.append(cell)
            rows.append(row)
        return rows


@dataclass(frozen=True)
class OperatorBlock:
    operators: list[str] | None = None
    choices: list[str] | None = None
    operator_count: int | None = None
    distinct: bool = True
    include_equals: bool = True

    def generate(self, count: int) -> list[list[str]]:
        if self.operators is not None:
            return [self.operators] * count
        if self.choices is None or self.operator_count is None:
            raise ValueError("operator block requires operators or choices/operator_count")
        return generate_operators(
            count=count,
            operator_count=self.operator_count,
            choices=self.choices,
            distinct=self.distinct,
            include_equals=self.include_equals,
        )


@dataclass(frozen=True)
class LevelSpec:
    operands: RowSource
    operators: OperatorBlock
    page_capacity: int | None = None
    prefix_operands: tuple[RowSource, ...] = ()
    insert_blank: bool = False
    blank_column: int = -1
    skip_wrap_positions: set[int] | None = None
    parentheses_pairs: list[tuple[int, int]] | None = None
    transform_rows: Callable[[list[list]], list[list]] | None = None

    def generate(self, count: int) -> list[str]:
        blocks = [block.generate(count) for block in (*self.prefix_operands, self.operands)]
        rows = np.hstack(blocks).tolist() if len(blocks) > 1 else blocks[0]
        if self.transform_rows is not None:
            rows = self.transform_rows(rows)
        if self.insert_blank:
            rows = insert_blank(rows, column=self.blank_column)
        return format_problems(
            rows,
            self.operators.generate(count),
            skip_wrap_positions=self.skip_wrap_positions,
            parentheses_pairs=self.parentheses_pairs,
        )


@dataclass(frozen=True)
class MixedLevelSpec:
    variants: list[LevelSpec] = field(default_factory=list)

    def generate(self, count: int) -> list[str]:
        if not self.variants:
            raise ValueError("mixed level requires at least one variant")

        problems: list[str] = []
        per_variant = count // len(self.variants)
        for index, variant in enumerate(self.variants):
            variant_count = count - per_variant * index if index == len(self.variants) - 1 else per_variant
            problems.extend(variant.generate(variant_count))

        np.random.shuffle(problems)
        return problems[:count]
