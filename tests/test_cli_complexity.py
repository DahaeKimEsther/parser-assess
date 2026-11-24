import pytest

from parser_assess import cli
from parser_assess.complexity import DocumentComplexity
from parser_assess.errors import ParserConfigError


def make(score, level="simple", pages=1, scanned=0, multicol=0, table=0, figure=0):
    return DocumentComplexity(pages, scanned, multicol, table, figure, score, level)


@pytest.fixture
def docs(tmp_path):
    root = tmp_path / "docs"
    (root / "sub").mkdir(parents=True)
    for name in ["hard.pdf", "easy.pdf", "sub/mid.PDF", "notes.txt"]:
        (root / name).write_bytes(b"x")
    return root


def fake_analyze(table):
    def _analyze(path, engine=None):
        result = table[path.name]
        if isinstance(result, Exception):
            raise result
        return result

    return _analyze


def test_sorted_ascending_by_score_and_only_pdfs(docs, monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "analyze_pdf",
        fake_analyze({"hard.pdf": make(0.9, "complex"), "easy.pdf": make(0.0), "mid.PDF": make(0.2, "moderate")}),
    )
    assert cli.main(["complexity", str(docs)]) == 0
    out = capsys.readouterr().out
    assert out.index("easy.pdf") < out.index("mid.PDF") < out.index("hard.pdf")
    assert "notes.txt" not in out
    assert "sub/mid.PDF" in out  # 폴더 기준 상대 경로(구분자 /)


def test_one_failure_does_not_stop_the_rest_and_goes_last(docs, monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "analyze_pdf",
        fake_analyze({"hard.pdf": RuntimeError("깨진 PDF"), "easy.pdf": make(0.0), "mid.PDF": make(0.5, "complex")}),
    )
    assert cli.main(["complexity", str(docs)]) == 0
    out = capsys.readouterr().out
    assert out.index("easy.pdf") < out.index("mid.PDF") < out.index("hard.pdf")
    assert "failed" in out and "깨진 PDF" in out


def test_single_file_path(docs, monkeypatch, capsys):
    monkeypatch.setattr(cli, "analyze_pdf", fake_analyze({"easy.pdf": make(0.0)}))
    assert cli.main(["complexity", str(docs / "easy.pdf")]) == 0
    assert "easy.pdf" in capsys.readouterr().out


def test_missing_path_returns_2(tmp_path, capsys):
    assert cli.main(["complexity", str(tmp_path / "nope")]) == 2
    assert "오류" in capsys.readouterr().err


def test_folder_without_pdf(tmp_path, capsys):
    (tmp_path / "a.txt").write_text("x")
    assert cli.main(["complexity", str(tmp_path)]) == 0
    assert "PDF" in capsys.readouterr().out


def test_missing_liteparse_stops_once_with_hint(docs, monkeypatch, capsys):
    calls = []

    def boom(path, engine=None):
        calls.append(path)
        raise ParserConfigError("uv sync --extra liteparse")

    monkeypatch.setattr(cli, "analyze_pdf", boom)
    assert cli.main(["complexity", str(docs)]) == 2
    assert "uv sync --extra liteparse" in capsys.readouterr().err
    assert len(calls) == 1  # 파일마다 같은 오류를 반복하지 않는다


def test_real_liteparse_end_to_end(make_pdf, capsys):
    pytest.importorskip("liteparse")
    lines = [f"Line {i}: plain text that is long enough to be treated as a normal page." for i in range(40)]
    pdf = make_pdf("real.pdf", lines)
    assert cli.main(["complexity", str(pdf)]) == 0
    out = capsys.readouterr().out
    assert "real.pdf" in out and "simple" in out
