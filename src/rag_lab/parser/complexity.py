"""PDF 문서의 구조 복잡도 계산.

LiteParse의 페이지별 분석(`is_complex`)을 문서 단위로 요약해서, 문서를 단순한 것부터 복잡한 것까지 줄 세울 수 있게 한다.
정답이 없는 사내 문서에도 그대로 쓸 수 있고, 평가(assess)와 나중의 라우터가 같은 계산을 쓴다.

주의: 아래 가중치와 임계값은 **잠정값**이다. 아직 ParseBench 점수와 맞춰 보지 않았으므로,
점수가 실제 파싱 난이도를 얼마나 잘 설명하는지 확인한 뒤 보정해야 한다.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from rag_lab.parser._liteparse import get_engine

# 잠정 가중치(합 1.0). 문서 전체 페이지 중 해당 특징이 있는 페이지의 비율에 곱한다.
WEIGHT_SCANNED = 0.40  # 텍스트 레이어가 없어 OCR이 필요하거나 글자가 깨진 페이지
WEIGHT_MULTICOLUMN = 0.25  # 2단 이상
WEIGHT_TABLE = 0.20  # 격자 표 또는 표처럼 정렬된 텍스트
WEIGHT_FIGURE = 0.15  # 그림/도형이 페이지에서 차지하는 비율이 큼

FIGURE_COVERAGE_THRESHOLD = 0.10  # 그림이 페이지 면적의 10% 이상이면 그림이 많은 페이지로 본다
LEVEL_SIMPLE_BELOW = 0.15
LEVEL_MODERATE_BELOW = 0.40

_LAYOUT_KEYS = ("column_count", "ruled_table_count", "text_table_run_count", "figure_coverage")


@dataclass(frozen=True)
class DocumentComplexity:
    """문서 단위 복잡도. score는 0(단순)~1(복잡), level은 simple, moderate, complex, unknown(페이지 없음)."""

    pages: int
    scanned_pages: int
    multicolumn_pages: int
    table_pages: int
    figure_pages: int
    score: float
    level: str


def summarize_pages(pages: Sequence[Mapping[str, Any]]) -> DocumentComplexity:
    """페이지별 분석(dict)을 문서 단위로 요약한다. 없는 키는 해당 특징이 없는 것으로 본다."""
    total = len(pages)
    if total == 0:
        return DocumentComplexity(0, 0, 0, 0, 0, 0.0, "unknown")

    scanned = multicolumn = table = figure = 0
    for page in pages:
        layout = page.get("layout") or {}
        if page.get("needs_ocr") or page.get("is_garbled"):
            scanned += 1
        if (layout.get("column_count") or 0) >= 2:
            multicolumn += 1
        if (layout.get("ruled_table_count") or 0) > 0 or (layout.get("text_table_run_count") or 0) > 0:
            table += 1
        if (layout.get("figure_coverage") or 0.0) >= FIGURE_COVERAGE_THRESHOLD:
            figure += 1

    score = min(
        1.0,
        WEIGHT_SCANNED * scanned / total
        + WEIGHT_MULTICOLUMN * multicolumn / total
        + WEIGHT_TABLE * table / total
        + WEIGHT_FIGURE * figure / total,
    )
    if score < LEVEL_SIMPLE_BELOW:
        level = "simple"
    elif score < LEVEL_MODERATE_BELOW:
        level = "moderate"
    else:
        level = "complex"
    return DocumentComplexity(total, scanned, multicolumn, table, figure, score, level)


def _page_from_stats(stats: Any) -> dict[str, Any]:
    """LiteParse의 PageComplexityStats 객체를 summarize_pages가 받는 dict로 바꾼다."""
    layout = getattr(stats, "layout", None)
    return {
        "needs_ocr": bool(getattr(stats, "needs_ocr", False)),
        "is_garbled": bool(getattr(stats, "is_garbled", False)),
        "layout": None if layout is None else {key: getattr(layout, key, 0) for key in _LAYOUT_KEYS},
    }


def analyze_pdf(path: Path, engine: Any = None) -> DocumentComplexity:
    """PDF 한 건을 분석해 문서 복잡도를 돌려준다. LiteParse가 없으면 설치 안내가 담긴 ParserConfigError를 던진다."""
    if engine is None:
        engine = get_engine()
    return summarize_pages([_page_from_stats(s) for s in engine.is_complex(str(path))])
