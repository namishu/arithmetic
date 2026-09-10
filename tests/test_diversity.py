from __future__ import annotations

from tests.support import run_project_python


def test_removes_exact_and_commutative_duplicates() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic.diversity import DiversityConfig, select_diverse_pages; "
        "pages = select_diverse_pages(['2 + 6 =', '6 + 2 =', '0 + 5 =', '3 + 4 ='], "
        "page_size=3, page_count=1, config=DiversityConfig()); "
        "assert '2 + 6 =' in pages[0]; "
        "assert '6 + 2 =' not in pages[0]; "
        "assert len(pages[0]) == 3",
    )


def test_limits_similar_leading_operands() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic.diversity import DiversityConfig, select_diverse_pages; "
        "cfg = DiversityConfig(max_same_leading_operand_per_page=1, max_special_operand_per_page=10); "
        "pages = select_diverse_pages(['0 + 5 =', '0 + 7 =', '2 + 6 =', '2 + 8 ='], "
        "page_size=3, page_count=1, config=cfg); "
        "assert pages[0][0] == '0 + 5 ='; "
        "assert pages[0][1] == '2 + 6 ='; "
        "assert pages[0][2] in {'0 + 7 =', '2 + 8 ='}",
    )


def test_allows_repeated_topics_across_pages() -> None:
    run_project_python(
        "arithmetic",
        "from namishu_arithmetic.diversity import DiversityConfig, select_diverse_pages; "
        "pages = select_diverse_pages(['1 + 1 =', '2 + 2 ='] * 2, "
        "page_size=2, page_count=2, config=DiversityConfig()); "
        "assert pages == [['1 + 1 =', '2 + 2 ='], ['1 + 1 =', '2 + 2 =']]",
    )
