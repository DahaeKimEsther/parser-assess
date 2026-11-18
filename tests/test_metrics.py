import json

from rag_lab.parser.metrics import (
    append_records,
    format_summary,
    load_records,
    percentile,
    summarize,
    timed,
)
from rag_lab.parser.models import ProcessingRecord


def rec(doc_id="a.md", doc_type="md", parser="markdown", ms=10.0, status="ok", error=None):
    return ProcessingRecord(doc_id, doc_type, parser, ms, 100, status, error)


def test_timed_measures_elapsed_ms_with_injected_clock():
    ticks = iter([1.0, 1.25])
    with timed(clock=lambda: next(ticks)) as t:
        pass
    assert t.ms == 250.0


def test_append_and_load_roundtrip(tmp_path):
    path = tmp_path / "sub" / "metrics.jsonl"
    append_records(path, [rec("한글 문서.md"), rec("b.txt", "txt", "text")])
    append_records(path, [rec("c.md")])
    rows = load_records(path)
    assert [r["doc_id"] for r in rows] == ["한글 문서.md", "b.txt", "c.md"]
    assert all("recorded_at" in r for r in rows)
    assert "한글 문서" in path.read_text(encoding="utf-8")


def test_load_records_skips_corrupt_lines_and_missing_file(tmp_path):
    path = tmp_path / "metrics.jsonl"
    assert load_records(path) == []
    path.write_text(
        json.dumps({"doc_id": "a", "doc_type": "md", "parser": "p", "ms": 1.0, "status": "ok"})
        + "\n{깨진 줄\n\n",
        encoding="utf-8",
    )
    assert len(load_records(path)) == 1


def test_percentile_nearest_rank():
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert percentile(values, 50) == 30.0
    assert percentile(values, 95) == 50.0
    assert percentile([7.0], 95) == 7.0


def rows(*records):
    return [r.to_dict() for r in records]


def test_summarize_values():
    data = rows(*[rec(ms=m) for m in (10.0, 20.0, 30.0, 40.0, 50.0)])
    (s,) = summarize(data)
    assert (s.doc_type, s.parser) == ("md", "markdown")
    assert (s.count, s.ok, s.skipped, s.failed) == (5, 5, 0, 0)
    assert s.mean_ms == 30.0
    assert s.p50_ms == 30.0
    assert s.p95_ms == 50.0
    assert round(s.docs_per_sec, 2) == 33.33


def test_summarize_groups_by_type_and_parser():
    data = rows(rec(), rec(doc_type="txt", parser="text"), rec(doc_type="txt", parser="text"))
    stats = {(s.doc_type, s.parser): s.count for s in summarize(data)}
    assert stats == {("md", "markdown"): 1, ("txt", "text"): 2}


def test_summarize_excludes_failed_and_skipped_from_timing():
    data = rows(
        rec(ms=10.0),
        rec(ms=9999.0, status="failed", error="x"),
        rec(doc_type="pdf", parser=None, ms=0.0, status="skipped"),
    )
    by_key = {(s.doc_type, s.parser): s for s in summarize(data)}
    md = by_key[("md", "markdown")]
    assert (md.count, md.ok, md.failed) == (2, 1, 1)
    assert md.mean_ms == 10.0
    pdf = by_key[("pdf", None)]
    assert (pdf.skipped, pdf.ok) == (1, 0)
    assert pdf.mean_ms is None and pdf.p50_ms is None and pdf.docs_per_sec is None


def test_summarize_empty():
    assert summarize([]) == []


def test_format_summary_lists_each_group():
    text = format_summary(summarize(rows(rec(), rec(doc_type="pdf", parser=None, status="skipped"))))
    assert "md" in text and "markdown" in text and "pdf" in text
    assert format_summary([]) == "기록된 처리 결과가 없습니다."
