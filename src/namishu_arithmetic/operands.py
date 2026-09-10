from __future__ import annotations

import random


def generate_operands(
    count: int,
    columns: int,
    lower: int | float,
    upper: int | float,
    value_type: str,
    *,
    decimal_places: int = 2,
) -> list[list]:
    if count < 0:
        raise ValueError("count must be >= 0")
    if columns < 0:
        raise ValueError("columns must be >= 0")
    if lower > upper:
        raise ValueError("lower must be <= upper")

    if value_type == "int":
        return [[random.randint(int(lower), int(upper)) for _ in range(columns)] for _ in range(count)]
    if value_type == "float":
        return [[round(random.uniform(lower, upper), decimal_places) for _ in range(columns)] for _ in range(count)]
    if value_type == "frac":
        max_denominator = int(max(1, upper))
        return [
            [f"{random.randint(int(lower), int(upper))}/{random.randint(1, max_denominator)}" for _ in range(columns)]
            for _ in range(count)
        ]
    raise ValueError("value_type must be one of {'int','float','frac'}")
