from __future__ import annotations

import random


def insert_blank(rows, column: int = -1, blank: str = "__") -> list[list]:
    result = [list(row) for row in rows]
    if column >= 0:
        for row in result:
            row.insert(column, blank)
    else:
        for row in result:
            idx = random.randint(0, len(row) - 1)
            row.insert(idx, blank)
    return result
