from __future__ import annotations

from ..level_generator import LevelGenerator
from ..specs import LevelSpec, MixedLevelSpec, OperandBlock, OperatorBlock


def _addition_as_subtraction(rows: list[list[int]]) -> list[list[int]]:
    return [[first + second, first] for first, second in rows]


def _three_terms_as_subtractions(rows: list[list[int]]) -> list[list[int]]:
    return [[first + second + third, first, second] for first, second, third in rows]


def _plus_then_minus(rows: list[list[int]]) -> list[list[int]]:
    return [[first, second + third, second] for first, second, third in rows]


def _minus_then_plus(rows: list[list[int]]) -> list[list[int]]:
    return [[first + third, first, second] for first, second, third in rows]


class AddSubGenerator(LevelGenerator):
    series_code = "addsub"
    default_seed = 1001
    default_page_capacity = 10


_LEVEL_MAP = {
    1: LevelSpec(OperandBlock(2, 0, 10), OperatorBlock(operators=["+", "="])),
    2: LevelSpec(
        OperandBlock(2, 0, 10),
        OperatorBlock(operators=["-", "="]),
        transform_rows=_addition_as_subtraction,
    ),
    3: MixedLevelSpec(
        [
            LevelSpec(OperandBlock(2, 0, 10), OperatorBlock(operators=["+", "="])),
            LevelSpec(
                OperandBlock(2, 0, 10),
                OperatorBlock(operators=["-", "="]),
                transform_rows=_addition_as_subtraction,
            ),
        ]
    ),
    4: LevelSpec(OperandBlock(3, 0, 10), OperatorBlock(operators=["+", "+", "="])),
    5: LevelSpec(
        OperandBlock(3, 0, 10),
        OperatorBlock(operators=["-", "-", "="]),
        transform_rows=_three_terms_as_subtractions,
    ),
    6: MixedLevelSpec(
        [
            LevelSpec(OperandBlock(3, 0, 10), OperatorBlock(operators=["+", "+", "="])),
            LevelSpec(
                OperandBlock(3, 0, 10),
                OperatorBlock(operators=["-", "-", "="]),
                transform_rows=_three_terms_as_subtractions,
            ),
        ]
    ),
    7: MixedLevelSpec(
        [
            LevelSpec(
                OperandBlock(3, 0, 10),
                OperatorBlock(operators=["+", "-", "="]),
                transform_rows=_plus_then_minus,
            ),
            LevelSpec(
                OperandBlock(3, 0, 10),
                OperatorBlock(operators=["-", "+", "="]),
                transform_rows=_minus_then_plus,
            ),
            LevelSpec(OperandBlock(3, 0, 10), OperatorBlock(operators=["+", "+", "="])),
        ]
    ),
    8: LevelSpec(
        operands=OperandBlock(1, 0, 15),
        prefix_operands=(OperandBlock(1, -15, 15),),
        operators=OperatorBlock(operators=["-", "="]),
    ),
    9: MixedLevelSpec(
        [
            LevelSpec(OperandBlock(2, 0, 15), OperatorBlock(operators=["-", "="])),
            LevelSpec(
                operands=OperandBlock(1, 0, 15),
                prefix_operands=(OperandBlock(1, -15, -1),),
                operators=OperatorBlock(operators=["+", "="]),
            ),
        ]
    ),
    10: MixedLevelSpec(
        [
            LevelSpec(
                operands=OperandBlock(1, 0, 15),
                prefix_operands=(OperandBlock(1, -15, -1),),
                operators=OperatorBlock(operators=["-", "="]),
            ),
            LevelSpec(
                operands=OperandBlock(1, 0, 15),
                prefix_operands=(OperandBlock(1, -15, -1),),
                operators=OperatorBlock(operators=["+", "="]),
            ),
            LevelSpec(OperandBlock(2, 0, 15), OperatorBlock(operators=["-", "="])),
        ]
    ),
    11: LevelSpec(
        operands=OperandBlock(2, 0, 10),
        prefix_operands=(OperandBlock(1, -10, 10),),
        operators=OperatorBlock(operators=["-", "-", "="]),
    ),
    12: LevelSpec(OperandBlock(3, 0, 10), OperatorBlock(choices=["+", "-"], operator_count=2)),
    13: LevelSpec(
        operands=OperandBlock(2, 0, 10),
        prefix_operands=(OperandBlock(1, -10, -1),),
        operators=OperatorBlock(choices=["+", "-"], operator_count=2),
    ),
    14: LevelSpec(
        operands=OperandBlock(1, -20, -1),
        prefix_operands=(OperandBlock(1, 0, 20),),
        operators=OperatorBlock(choices=["+", "-"], operator_count=1),
    ),
    15: LevelSpec(OperandBlock(2, -20, -1), OperatorBlock(choices=["+", "-"], operator_count=1)),
    16: LevelSpec(OperandBlock(3, -15, 15), OperatorBlock(operators=["+", "+", "="])),
    17: LevelSpec(OperandBlock(2, 0, 40), OperatorBlock(operators=["+", "="]), insert_blank=True),
    18: LevelSpec(OperandBlock(2, 0, 40), OperatorBlock(operators=["-", "="]), insert_blank=True),
    19: LevelSpec(
        OperandBlock(2, 0, 40),
        OperatorBlock(choices=["+", "-"], operator_count=1),
        insert_blank=True,
    ),
    20: LevelSpec(
        OperandBlock(2, 0, 30),
        OperatorBlock(choices=["+", "-"], operator_count=1),
        insert_blank=True,
    ),
    21: LevelSpec(
        operands=OperandBlock(1, 0, 30),
        prefix_operands=(OperandBlock(1, -30, 30),),
        operators=OperatorBlock(choices=["+ __ =", "- __ ="], operator_count=1, include_equals=False),
    ),
    22: LevelSpec(
        OperandBlock(3, 0, 30),
        OperatorBlock(choices=["+", "-"], operator_count=2),
        insert_blank=True,
    ),
    23: LevelSpec(
        operands=OperandBlock(2, 0, 30),
        prefix_operands=(OperandBlock(1, -30, 30),),
        operators=OperatorBlock(operators=["-", "+", "="]),
        insert_blank=True,
    ),
    24: LevelSpec(
        OperandBlock(3, -30, 30),
        OperatorBlock(choices=["+", "-"], operator_count=2),
        insert_blank=True,
        skip_wrap_positions={0, 3},
    ),
}

AddSubGenerator.level_map = _LEVEL_MAP
