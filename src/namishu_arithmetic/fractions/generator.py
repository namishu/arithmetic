from __future__ import annotations

from ..level_generator import LevelGenerator
from ..specs import LevelSpec, MixedOperandBlock, OperandBlock, OperatorBlock


def _decimal_rows_as_division(rows: list[list]) -> list[list]:
    return [[round(divisor * quotient, 2), divisor] for divisor, quotient in rows]


class FractionGenerator(LevelGenerator):
    series_code = "fraction"
    default_seed = 3001
    default_page_capacity = 10


_LEVEL_MAP = {
    1: LevelSpec(OperandBlock(2, 0, 20, "frac"), OperatorBlock(choices=["+", "-"], operator_count=1)),
    2: LevelSpec(OperandBlock(3, 0, 20, "frac"), OperatorBlock(choices=["+", "-"], operator_count=2)),
    3: LevelSpec(
        OperandBlock(3, 0, 20, "frac"),
        OperatorBlock(choices=["+", "-"], operator_count=2),
        insert_blank=True,
    ),
    4: LevelSpec(OperandBlock(2, -20, 20, "frac"), OperatorBlock(operators=["×", "="])),
    5: LevelSpec(OperandBlock(2, -20, 20, "frac"), OperatorBlock(operators=["÷", "="])),
    6: LevelSpec(OperandBlock(3, -10, 10, "frac"), OperatorBlock(choices=["×", "÷"], operator_count=2)),
    7: LevelSpec(
        OperandBlock(3, -10, 10, "frac"),
        OperatorBlock(choices=["×", "÷"], operator_count=2),
        insert_blank=True,
        skip_wrap_positions={0, 3},
    ),
    8: LevelSpec(
        OperandBlock(4, -10, 10, "frac"),
        OperatorBlock(choices=["+", "-", "×", "÷"], operator_count=3),
        page_capacity=12,
    ),
    9: LevelSpec(
        OperandBlock(4, -10, 10, "frac"),
        OperatorBlock(choices=["+", "-", "×", "÷"], operator_count=3),
        page_capacity=12,
        insert_blank=True,
        skip_wrap_positions={0, 4},
    ),
    10: LevelSpec(
        OperandBlock(2, -20, 20, "float", decimal_places=1),
        OperatorBlock(choices=["+", "-"], operator_count=1),
    ),
    11: LevelSpec(MixedOperandBlock(3, -10, 10), OperatorBlock(choices=["+", "-"], operator_count=2)),
    12: LevelSpec(
        MixedOperandBlock(3, -20, 20),
        OperatorBlock(choices=["+", "-"], operator_count=2),
        insert_blank=True,
        skip_wrap_positions={0, 3},
    ),
    13: LevelSpec(OperandBlock(2, -20, 20, "float", decimal_places=1), OperatorBlock(operators=["×", "="])),
    14: LevelSpec(
        OperandBlock(2, -10, 10, "float", decimal_places=1),
        OperatorBlock(operators=["÷", "="]),
        transform_rows=_decimal_rows_as_division,
    ),
    15: LevelSpec(MixedOperandBlock(3, -10, 10, decimal_places=1), OperatorBlock(operators=["×", "÷", "="])),
    16: LevelSpec(
        MixedOperandBlock(3, -20, 20, decimal_places=1),
        OperatorBlock(operators=["×", "÷", "="]),
        insert_blank=True,
        skip_wrap_positions={0, 3},
    ),
    17: LevelSpec(
        MixedOperandBlock(4, -10, 10, decimal_places=1),
        OperatorBlock(choices=["+", "-", "×", "÷"], operator_count=3),
        page_capacity=12,
    ),
    18: LevelSpec(
        MixedOperandBlock(4, -10, 10, decimal_places=1),
        OperatorBlock(choices=["+", "-", "×", "÷"], operator_count=3),
        page_capacity=12,
        insert_blank=True,
        skip_wrap_positions={0, 4},
    ),
}

FractionGenerator.level_map = _LEVEL_MAP
