import sys
from types import SimpleNamespace

import pytest

from rag_lab.parser import _liteparse, registry
from rag_lab.parser.errors import ParserConfigError
from rag_lab.parser.registry import get_parser


@pytest.fixture(autouse=True)
def fresh_engine_cache():
    _liteparse.get_engine.cache_clear()
    yield
    _liteparse.get_engine.cache_clear()


class FakeLiteParse:
    """liteparse.LiteParse를 흉내 낸다. 만들 때 받은 옵션과 parse 호출을 기록한다."""

    instances = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.calls = []
        FakeLiteParse.instances.append(self)

    def parse(self, path):
        self.calls.append(path)
        return SimpleNamespace(text="# 제목\n\n본문", total_pages=3)


@pytest.fixture
def fake_liteparse(monkeypatch):
    FakeLiteParse.instances = []
    monkeypatch.setitem(sys.modules, "liteparse", SimpleNamespace(LiteParse=FakeLiteParse))
    return FakeLiteParse


def test_parser_is_registered_without_importing_liteparse():
    # 등록은 liteparse 설치 여부와 무관해야 한다(모듈 import 시점에는 liteparse를 불러오지 않는다)
    assert "liteparse" in registry._PARSERS


def test_missing_liteparse_gives_install_hint(monkeypatch):
    monkeypatch.setitem(sys.modules, "liteparse", None)
    with pytest.raises(ParserConfigError, match="uv sync --extra liteparse"):
        get_parser("liteparse")


def test_parse_returns_markdown_text_and_page_count(fake_liteparse, tmp_path):
    pdf = tmp_path / "docs" / "a.pdf"
    pdf.parent.mkdir()
    pdf.write_bytes(b"%PDF")
    doc = get_parser("liteparse").parse(pdf, "docs/a.pdf")
    assert doc.doc_id == "docs/a.pdf"
    assert doc.doc_type == "pdf"
    assert doc.source_path == pdf
    assert doc.text == "# 제목\n\n본문"
    assert doc.metadata["total_pages"] == 3
    assert "empty" not in doc.metadata
    assert fake_liteparse.instances[0].calls == [str(pdf)]


def test_engine_is_created_with_ocr_off_and_markdown(fake_liteparse, tmp_path):
    get_parser("liteparse").parse(tmp_path / "a.pdf", "a.pdf")
    kwargs = fake_liteparse.instances[0].kwargs
    assert kwargs["ocr_enabled"] is False
    assert kwargs["output_format"] == "markdown"


def test_engine_is_shared_between_parser_instances(fake_liteparse, tmp_path):
    get_parser("liteparse").parse(tmp_path / "a.pdf", "a.pdf")
    get_parser("liteparse").parse(tmp_path / "b.pdf", "b.pdf")
    assert len(fake_liteparse.instances) == 1


def test_empty_text_is_flagged(monkeypatch, tmp_path):
    class Empty(FakeLiteParse):
        def parse(self, path):
            return SimpleNamespace(text="```text\n\n```", total_pages=1)  # 스캔 PDF를 OCR 없이 읽으면 이런 빈 블록이 나온다

    monkeypatch.setitem(sys.modules, "liteparse", SimpleNamespace(LiteParse=Empty))
    doc = get_parser("liteparse").parse(tmp_path / "a.pdf", "a.pdf")
    assert doc.metadata["empty"] is True


def test_whitespace_only_text_is_flagged(monkeypatch, tmp_path):
    class Blank(FakeLiteParse):
        def parse(self, path):
            return SimpleNamespace(text="  \n ", total_pages=1)

    monkeypatch.setitem(sys.modules, "liteparse", SimpleNamespace(LiteParse=Blank))
    assert get_parser("liteparse").parse(tmp_path / "a.pdf", "a.pdf").metadata["empty"] is True


def test_real_liteparse_extracts_text_layer(make_pdf):
    pytest.importorskip("liteparse")
    lines = [f"Line {i}: plain text that is long enough to be treated as a normal page." for i in range(40)]
    pdf = make_pdf("real.pdf", lines)
    doc = get_parser("liteparse").parse(pdf, "real.pdf")
    assert "Line 0" in doc.text and "Line 39" in doc.text
    assert doc.metadata["total_pages"] == 1


def test_real_liteparse_raises_on_broken_pdf(tmp_path):
    pytest.importorskip("liteparse")
    broken = tmp_path / "broken.pdf"
    broken.write_bytes(b"%PDF-1.4\n garbage")
    with pytest.raises(Exception):
        get_parser("liteparse").parse(broken, "broken.pdf")
