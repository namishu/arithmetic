from __future__ import annotations

import random
from collections.abc import Sequence

import numpy as np


def generate_operators(
    count: int,
    operator_count: int,
    choices: set[str] | Sequence[str],
    *,
    distinct: bool = True,
    include_equals: bool = False,
):
    choices_list = sorted(choices) if isinstance(choices, set) else list(choices)
    if count < 0:
        raise ValueError("count must be >= 0")
    if operator_count < 0:
        raise ValueError("operator_count must be >= 0")
    if not choices_list and operator_count > 0:
        raise ValueError("choices cannot be empty")
    if distinct:
        if operator_count > len(choices_list):
            raise ValueError("operator_count cannot exceed len(choices) when distinct=True")
        operators = [random.sample(choices_list, operator_count) for _ in range(count)]
    else:
        operators = [[random.choice(choices_list) for _ in range(operator_count)] for _ in range(count)]
    if include_equals:
        operators = np.hstack((operators, [["="]] * count))
    return operators
