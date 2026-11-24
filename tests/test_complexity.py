import sys
from types import SimpleNamespace

import pytest

from parser_assess import _liteparse
from parser_assess.complexity import (
    FIGURE_COVERAGE_THRESHOLD,
    DocumentComplexity,
    analyze_pdf,
    summarize_pages,
)
from parser_assess.errors import ParserConfigError


def layout(column_count=1, ruled_table_count=0, text_table_run_count=0, figure_coverage=0.0):
    return {
        "column_count": column_count,
        "ruled_table_count": ruled_table_count,
        "text_table_run_count": text_table_run_count,
        "figure_coverage": figure_coverage,
    }


# 실제 LiteParse 호출에서 확인한 값들
SIMPLE = {"needs_ocr": False, "is_garbled": False, "layout": layout()}
SCANNED = {"needs_ocr": True, "is_garbled": False, "layout": layout()}
TWO_COL_TABLE = {
    "needs_ocr": False,
    "is_garbled": False,
    "layout": layout(column_count=2, ruled_table_count=1, text_table_run_count=1, figure_coverage=0.034),
}


@pytest.fixture(autouse=True)
def fresh_engine_cache():
    _liteparse.get_engine.cache_clear()
    yield
    _liteparse.get_engine.cache_clear()


def test_simple_page_scores_zero():
    c = summarize_pages([SIMPLE])
    assert (c.pages, c.scanned_pages, c.multicolumn_pages, c.table_pages, c.figure_pages) == (1, 0, 0, 0, 0)
    assert c.score == 0.0
    assert c.level == "simple"


def test_scanned_page_is_complex():
    c = summarize_pages([SCANNED])
    assert c.scanned_pages == 1
    assert c.score == pytest.approx(0.40)
    assert c.level == "complex"


def test_two_column_page_with_table():
    c = summarize_pages([TWO_COL_TABLE])
    assert (c.multicolumn_pages, c.table_pages, c.figure_pages, c.scanned_pages) == (1, 1, 0, 0)
    assert c.score == pytest.approx(0.25 + 0.20)
    assert c.level == "complex"


def test_mixed_document_uses_page_fractions():
    c = summarize_pages([SIMPLE, SIMPLE, SCANNED, TWO_COL_TABLE])
    assert c.pages == 4
    assert c.score == pytest.approx(0.40 * 0.25 + 0.25 * 0.25 + 0.20 * 0.25)
    assert c.level == "moderate"


def test_empty_document_is_unknown():
    c = summarize_pages([])
    assert (c.pages, c.score, c.level) == (0, 0.0, "unknown")


def test_missing_keys_are_tolerated():
    c = summarize_pages([{"needs_ocr": False}, {}, {"layout": None}])
    assert c.pages == 3
    assert c.score == 0.0 and c.level == "simple"


def test_garbled_counts_as_scanned_but_page_is_counted_once():
    both = {"needs_ocr": True, "is_garbled": True, "layout": layout()}
    garbled_only = {"needs_ocr": False, "is_garbled": True, "layout": layout()}
    assert summarize_pages([both]).scanned_pages == 1
    assert summarize_pages([garbled_only]).scanned_pages == 1


def test_text_table_run_alone_counts_as_table_page():
    page = {"needs_ocr": False, "layout": layout(text_table_run_count=2)}
    assert summarize_pages([page]).table_pages == 1


def test_figure_threshold_boundary():
    at = {"layout": layout(figure_coverage=FIGURE_COVERAGE_THRESHOLD)}
    below = {"layout": layout(figure_coverage=FIGURE_COVERAGE_THRESHOLD - 0.001)}
    assert summarize_pages([at]).figure_pages == 1
    assert summarize_pages([below]).figure_pages == 0


def test_score_never_exceeds_one():
    everything = {
        "needs_ocr": True,
        "layout": layout(column_count=3, ruled_table_count=2, figure_coverage=0.9),
    }
    c = summarize_pages([everything, everything])
    assert c.score <= 1.0
    assert c.score == pytest.approx(1.0)


def test_level_boundaries():
    # 8페이지 중 1페이지 다단 → 0.25/8 ≈ 0.03 (simple), 스캔 1/2 → 0.2 (moderate), 전부 스캔 → 0.4 (complex)
    two_col = {"layout": layout(column_count=2)}
    assert summarize_pages([two_col] + [SIMPLE] * 7).level == "simple"
    assert summarize_pages([SCANNED, SIMPLE]).level == "moderate"
    assert summarize_pages([SCANNED]).level == "complex"


def test_returns_frozen_dataclass():
    c = summarize_pages([SIMPLE])
    assert isinstance(c, DocumentComplexity)
    with pytest.raises(Exception):
        c.score = 1.0  # type: ignore[misc]


class FakeEngine:
    """LiteParse.is_complex()가 돌려주는 PageComplexityStats 모양을 흉내 낸다."""

    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def is_complex(self, path):
        self.calls.append(path)
        return self.pages


def stats(needs_ocr=False, is_garbled=False, lay=None):
    return SimpleNamespace(needs_ocr=needs_ocr, is_garbled=is_garbled, layout=lay)


def lay_obj(**kw):
    base = {"column_count": 1, "ruled_table_count": 0, "text_table_run_count": 0, "figure_coverage": 0.0}
    return SimpleNamespace(**{**base, **kw})


def test_analyze_pdf_reads_attributes_from_engine(tmp_path):
    engine = FakeEngine([stats(lay=lay_obj()), stats(needs_ocr=True, lay=lay_obj()), stats(lay=lay_obj(column_count=2))])
    c = analyze_pdf(tmp_path / "a.pdf", engine=engine)
    assert (c.pages, c.scanned_pages, c.multicolumn_pages) == (3, 1, 1)
    assert engine.calls == [str(tmp_path / "a.pdf")]


def test_analyze_pdf_handles_missing_layout(tmp_path):
    c = analyze_pdf(tmp_path / "a.pdf", engine=FakeEngine([stats(lay=None)]))
    assert c.pages == 1 and c.score == 0.0


def test_analyze_pdf_without_liteparse_gives_install_hint(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "liteparse", None)  # import liteparse → ImportError
    with pytest.raises(ParserConfigError, match="uv sync --extra liteparse"):
        analyze_pdf(tmp_path / "a.pdf")


def test_analyze_pdf_with_real_liteparse(make_pdf):
    pytest.importorskip("liteparse")
    # 글자가 너무 적은 페이지는 LiteParse가 sparse-text로 보고 OCR 필요(스캔)로 판정하므로 본문을 충분히 넣는다
    lines = [f"Line {i}: plain text that is long enough to be treated as a normal page." for i in range(40)]
    c = analyze_pdf(make_pdf("real.pdf", lines))
    assert c.pages == 1
    assert c.scanned_pages == 0
    assert c.level == "simple"


def test_analyze_pdf_sparse_text_page_counts_as_scanned(make_pdf):
    """글이 거의 없는 페이지는 스캔으로 집계된다(LiteParse의 sparse-text 판정). 알려진 한계를 고정해 둔다."""
    pytest.importorskip("liteparse")
    c = analyze_pdf(make_pdf("sparse.pdf", ["Hi"]))
    assert c.scanned_pages == 1
