from __future__ import annotations

import numbers


def format_problems(
    operands,
    operators,
    *,
    wrap_negative: bool = True,
    skip_wrap_positions: set | None = None,
    parentheses_pairs: set | list | None = None,
) -> list[str]:
    if len(operands) != len(operators):
        raise ValueError("operand and operator row counts do not match")

    problems = []
    for operand_row, operator_row in zip(operands, operators, strict=True):
        if wrap_negative:
            operand_row = _wrap_negative_values(operand_row, skip_wrap_positions)
        row = _interleave_operands_and_operators(operand_row, operator_row)
        if parentheses_pairs:
            row = _add_parentheses(row, parentheses_pairs)
        problems.append(" ".join([str(item) for item in row]))
    return problems


def _wrap_negative_values(operand_row, skip_positions: set | None = None):
    if skip_positions is None:
        skip_positions = {0}
    result = []
    for index, value in enumerate(operand_row):
        is_negative_text = isinstance(value, str) and value.startswith("-")
        is_negative_number = isinstance(value, numbers.Number) and value < 0
        should_wrap = index not in skip_positions and (is_negative_text or is_negative_number)
        result.append(f"({value})" if should_wrap else value)
    return result


def _interleave_operands_and_operators(operand_row, operator_row):
    operand_count = len(operand_row)
    operator_count = len(operator_row)
    if operand_count < operator_count or operand_count - operator_count > 1:
        raise ValueError("operand and operator counts do not match")
    row = [item for pair in zip(operand_row, operator_row, strict=False) for item in pair]
    if operand_count == operator_count + 1:
        row.append(operand_row[-1])
    return row


def _add_parentheses(row, parentheses_pairs):
    for left, right in parentheses_pairs:
        row[left] = "(" + str(row[left])
        row[right] = str(row[right]) + ")"
    return row
