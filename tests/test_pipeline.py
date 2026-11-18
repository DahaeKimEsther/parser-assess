import json
from pathlib import Path

import pytest
import yaml

from rag_lab.parser.cli import main
from rag_lab.parser.registry import register_parser

CONFIG = """
[routes]
md = "markdown"
txt = "text"

[output]
writer = "markdown"
dir = "{out}"
"""


@pytest.fixture
def workspace(tmp_path):
    docs = tmp_path / "docs"
    (docs / "sub").mkdir(parents=True)
    (docs / "a.md").write_text("# 제목\n내용\n", encoding="utf-8")
    (docs / "sub" / "b.txt").write_text("본문\n", encoding="utf-8")
    (docs / "report.pdf").write_bytes(b"%PDF-1.4")
    (docs / "empty.md").write_text("", encoding="utf-8")
    (docs / "UPPER.MD").write_text("대문자 확장자\n", encoding="utf-8")
    (docs / "NOEXT").write_text("확장자 없음\n", encoding="utf-8")
    return tmp_path


def write_config(root: Path, text: str | None = None) -> Path:
    cfg = root / "routing.toml"
    cfg.write_text(text or CONFIG.format(out=(root / "out").as_posix()), encoding="utf-8")
    return cfg


def run(root: Path, cfg: Path, *extra: str) -> int:
    return main(["run", str(root / "docs"), "--config", str(cfg), "--metrics", str(root / "metrics.jsonl"), *extra])


def records(root: Path) -> dict[str, dict]:
    lines = (root / "metrics.jsonl").read_text(encoding="utf-8").splitlines()
    return {r["doc_id"]: r for r in map(json.loads, lines)}


def test_end_to_end(workspace, capsys):
    cfg = write_config(workspace)
    assert run(workspace, cfg) == 0

    recs = records(workspace)
    assert {k: v["status"] for k, v in recs.items()} == {
        "a.md": "ok",
        "sub/b.txt": "ok",
        "empty.md": "ok",
        "UPPER.MD": "ok",
        "report.pdf": "skipped",
        "NOEXT": "skipped",
    }
    assert recs["a.md"]["parser"] == "markdown"
    assert recs["sub/b.txt"]["parser"] == "text"
    assert recs["report.pdf"]["parser"] is None

    out = workspace / "out"
    assert (out / "a.md").exists()
    assert (out / "sub" / "b.txt.md").exists()
    assert (out / "UPPER.MD").exists()
    assert not (out / "report.pdf.md").exists()
    assert not (out / "NOEXT.md").exists()

    content = (out / "a.md").read_text(encoding="utf-8")
    fm = yaml.safe_load(content[4:].split("\n---\n", 1)[0])
    assert fm == {"title": "a", "source": "a.md", "doc_type": "md", "parser": "markdown"}

    shown = capsys.readouterr().out
    assert "ok 4" in shown and "skipped 2" in shown


def test_changing_routing_config_changes_parser_without_code_change(workspace):
    cfg = write_config(workspace, CONFIG.format(out=(workspace / "out").as_posix()).replace('md = "markdown"', 'md = "text"'))
    assert run(workspace, cfg) == 0
    assert records(workspace)["a.md"]["parser"] == "text"


def test_fallback_handles_unmapped_types(workspace):
    text = 'fallback = "text"\n' + CONFIG.format(out=(workspace / "out").as_posix())
    assert run(workspace, write_config(workspace, text)) == 0
    recs = records(workspace)
    assert recs["NOEXT"]["status"] == "ok" and recs["NOEXT"]["parser"] == "text"


def test_failed_document_does_not_stop_batch(workspace):
    (workspace / "docs" / "bad.md").write_bytes(b"\xff\xfe\x00bad")
    assert run(workspace, write_config(workspace)) == 0
    recs = records(workspace)
    assert recs["bad.md"]["status"] == "failed"
    assert "UnicodeDecodeError" in recs["bad.md"]["error"]
    assert recs["a.md"]["status"] == "ok"
    assert not (workspace / "out" / "bad.md").exists()


def test_parser_exception_is_isolated(workspace):
    @register_parser("boom")
    class Boom:
        def parse(self, path, doc_id):
            raise RuntimeError("터짐")

    text = CONFIG.format(out=(workspace / "out").as_posix()).replace('txt = "text"', 'txt = "boom"')
    assert run(workspace, write_config(workspace, text)) == 0
    recs = records(workspace)
    assert recs["sub/b.txt"]["status"] == "failed" and "터짐" in recs["sub/b.txt"]["error"]
    assert recs["a.md"]["status"] == "ok"


def test_unknown_parser_in_config_fails_before_processing(workspace, capsys):
    text = CONFIG.format(out=(workspace / "out").as_posix()).replace('"text"', '"nope"')
    assert run(workspace, write_config(workspace, text)) == 2
    assert "nope" in capsys.readouterr().err
    assert not (workspace / "metrics.jsonl").exists()
    assert not (workspace / "out").exists()


def test_unknown_writer_in_config_fails_before_processing(workspace, capsys):
    text = CONFIG.format(out=(workspace / "out").as_posix()).replace('writer = "markdown"', 'writer = "okf"')
    assert run(workspace, write_config(workspace, text)) == 2
    assert "okf" in capsys.readouterr().err
    assert not (workspace / "metrics.jsonl").exists()


def test_missing_docs_dir_and_missing_config(workspace, capsys):
    cfg = write_config(workspace)
    assert main(["run", str(workspace / "nope"), "--config", str(cfg)]) == 2
    assert main(["run", str(workspace / "docs"), "--config", str(workspace / "none.toml")]) == 2
    assert "오류" in capsys.readouterr().err


def test_output_dir_inside_docs_is_not_reprocessed(workspace):
    out_inside = (workspace / "docs" / "_out").as_posix()
    cfg = write_config(workspace, CONFIG.format(out=out_inside))
    assert run(workspace, cfg) == 0
    first = len((workspace / "metrics.jsonl").read_text(encoding="utf-8").splitlines())
    assert run(workspace, cfg) == 0
    total = len((workspace / "metrics.jsonl").read_text(encoding="utf-8").splitlines())
    assert total == first * 2


def test_metrics_accumulate_across_runs(workspace):
    cfg = write_config(workspace)
    run(workspace, cfg)
    run(workspace, cfg)
    assert len((workspace / "metrics.jsonl").read_text(encoding="utf-8").splitlines()) == 12


def test_stats_command(workspace, capsys):
    assert main(["stats", "--metrics", str(workspace / "metrics.jsonl")]) == 0
    assert "기록된 처리 결과가 없습니다." in capsys.readouterr().out

    run(workspace, write_config(workspace))
    capsys.readouterr()
    assert main(["stats", "--metrics", str(workspace / "metrics.jsonl")]) == 0
    shown = capsys.readouterr().out
    assert "markdown" in shown and "text" in shown and "p95ms" in shown
