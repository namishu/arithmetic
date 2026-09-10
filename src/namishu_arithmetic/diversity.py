from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_COMMUTATIVE_OPERATORS = {"+", "×"}
_OPERATORS = {"+", "-", "×", "÷", "="}
_SPECIAL_OPERANDS = {"-1", "0", "1"}


@dataclass(frozen=True)
class ProblemFeatures:
    text_key: str
    operator_pattern: tuple[str, ...]
    operands: tuple[str, ...]
    leading_operand: str | None
    commutative_key: tuple[str, tuple[str, ...]] | None
    special_operands: tuple[str, ...]


@dataclass(frozen=True)
class DiversityConfig:
    candidate_multiplier: int = 8
    max_same_leading_operand_per_page: int = 2
    max_special_operand_per_page: int = 3

    @classmethod
    def from_config(cls, cfg: dict[str, Any] | None) -> DiversityConfig:
        if cfg is None:
            return cls()
        return cls(
            candidate_multiplier=int(cfg.get("candidate_multiplier", cls.candidate_multiplier)),
            max_same_leading_operand_per_page=int(
                cfg.get("max_same_leading_operand_per_page", cls.max_same_leading_operand_per_page)
            ),
            max_special_operand_per_page=int(cfg.get("max_special_operand_per_page", cls.max_special_operand_per_page)),
        )


def select_diverse_pages(
    candidates: list[str],
    *,
    page_size: int,
    page_count: int,
    config: DiversityConfig,
) -> list[list[str]]:
    if page_size <= 0:
        raise ValueError("page_size must be > 0")
    if page_count <= 0:
        raise ValueError("page_count must be > 0")

    remaining = list(candidates)
    pages = []
    for _ in range(page_count):
        page = _select_page(remaining, page_size, config)
        pages.append(page)

    return pages


def extract_features(problem: str) -> ProblemFeatures:
    tokens = [_normalize_token(token) for token in problem.split()]
    operators = tuple(token for token in tokens if token in _OPERATORS and token != "=")
    operands = tuple(token for token in tokens if token not in _OPERATORS and token != "__")
    leading_operand = operands[0] if operands else None
    special_operands = tuple(operand for operand in operands if operand in _SPECIAL_OPERANDS)

    commutative_key = None
    if len(operators) == 1 and operators[0] in _COMMUTATIVE_OPERATORS and len(operands) >= 2:
        commutative_key = (operators[0], tuple(sorted(operands[:2])))

    text_key = "".join(tokens)
    return ProblemFeatures(
        text_key=text_key,
        operator_pattern=operators,
        operands=operands,
        leading_operand=leading_operand,
        commutative_key=commutative_key,
        special_operands=special_operands,
    )


def _select_page(candidates: list[str], page_size: int, config: DiversityConfig) -> list[str]:
    page: list[str] = []
    page_features: list[ProblemFeatures] = []

    while len(page) < page_size and candidates:
        best_index = min(
            range(len(candidates)),
            key=lambda index: (
                _diversity_penalty(extract_features(candidates[index]), page_features, config),
                index,
            ),
        )
        selected = candidates.pop(best_index)
        page.append(selected)
        page_features.append(extract_features(selected))

    return page


def _diversity_penalty(
    candidate: ProblemFeatures,
    selected: list[ProblemFeatures],
    config: DiversityConfig,
) -> int:
    if not selected:
        return 0

    penalty = 0
    same_text_count = sum(item.text_key == candidate.text_key for item in selected)
    same_commutative_count = (
        sum(item.commutative_key == candidate.commutative_key for item in selected)
        if candidate.commutative_key is not None
        else 0
    )
    if same_text_count or same_commutative_count:
        penalty += 10_000 * max(same_text_count, same_commutative_count)

    same_leading_count = sum(
        item.leading_operand == candidate.leading_operand and item.operator_pattern == candidate.operator_pattern
        for item in selected
        if candidate.leading_operand is not None
    )
    if same_leading_count >= config.max_same_leading_operand_per_page:
        penalty += 1_000 * (same_leading_count - config.max_same_leading_operand_per_page + 1)
    else:
        penalty += 25 * same_leading_count

    special_count = sum(len(item.special_operands) for item in selected) + len(candidate.special_operands)
    if special_count > config.max_special_operand_per_page:
        penalty += 200 * (special_count - config.max_special_operand_per_page)

    operand_overlap = sum(len(set(item.operands) & set(candidate.operands)) for item in selected)
    penalty += 5 * operand_overlap

    same_pattern_count = sum(item.operator_pattern == candidate.operator_pattern for item in selected)
    penalty += same_pattern_count

    return penalty


def _normalize_token(token: str) -> str:
    return token.strip().strip("()")
