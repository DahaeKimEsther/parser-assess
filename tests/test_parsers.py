import pytest

from rag_lab.parser.registry import available_parsers, get_parser


def test_builtin_parsers_are_registered():
    assert {"markdown", "text"} <= set(available_parsers())


@pytest.mark.parametrize("name", ["markdown", "text"])
def test_parser_reads_utf8_and_normalizes_newlines(tmp_path, name):
    path = tmp_path / "a.md"
    path.write_bytes("﻿# 제목\r\n내용\r\n".encode("utf-8"))
    doc = get_parser(name).parse(path, "a.md")
    assert doc.text == "# 제목\n내용\n"
    assert doc.doc_id == "a.md"
    assert doc.doc_type == "md"
    assert doc.source_path == path


@pytest.mark.parametrize("name", ["markdown", "text"])
def test_parser_flags_empty_document(tmp_path, name):
    path = tmp_path / "empty.txt"
    path.write_text("  \n\n", encoding="utf-8")
    doc = get_parser(name).parse(path, "empty.txt")
    assert doc.metadata["empty"] is True


@pytest.mark.parametrize("name", ["markdown", "text"])
def test_parser_rejects_non_utf8(tmp_path, name):
    path = tmp_path / "bad.txt"
    path.write_bytes(b"\xff\xfe\x00bad")
    with pytest.raises(UnicodeDecodeError):
        get_parser(name).parse(path, "bad.txt")
