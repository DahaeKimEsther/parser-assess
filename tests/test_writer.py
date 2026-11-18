from pathlib import Path

import pytest
import yaml

from rag_lab.parser.models import ParsedDocument
from rag_lab.parser.registry import available_writers, get_writer
from rag_lab.parser.writers.markdown import render_markdown


def split_front_matter(content: str):
    assert content.startswith("---\n")
    head, body = content[4:].split("\n---\n", 1)
    return yaml.safe_load(head), body


def make_doc(doc_id="a.md", text="# 제목\n내용", **metadata):
    return ParsedDocument(doc_id, Path(doc_id), Path(doc_id).suffix.lstrip("."), text, metadata)


def test_markdown_writer_is_registered():
    assert "markdown" in available_writers()


def test_front_matter_fields_and_body():
    fm, body = split_front_matter(render_markdown(make_doc("sub/보고서.md", parser="markdown")))
    assert fm == {"title": "보고서", "source": "sub/보고서.md", "doc_type": "md", "parser": "markdown"}
    assert body.strip() == "# 제목\n내용"


def test_front_matter_survives_special_characters():
    doc = make_doc('따옴표 " 와 콜론: 그리고 \\ 역슬래시.md', parser="markdown")
    fm, _ = split_front_matter(render_markdown(doc))
    assert fm["source"] == '따옴표 " 와 콜론: 그리고 \\ 역슬래시.md'
    assert fm["title"] == '따옴표 " 와 콜론: 그리고 \\ 역슬래시'


def test_empty_document_has_marker_and_no_body():
    fm, body = split_front_matter(render_markdown(make_doc("e.md", text="", empty=True)))
    assert fm["empty"] is True
    assert body == ""


def test_write_keeps_md_name_and_appends_for_other_types(tmp_path):
    writer = get_writer("markdown")
    assert writer.write(make_doc("a.md"), tmp_path) == tmp_path / "a.md"
    assert writer.write(make_doc("sub/b.txt"), tmp_path) == tmp_path / "sub" / "b.txt.md"
    assert (tmp_path / "sub" / "b.txt.md").read_text(encoding="utf-8").startswith("---\n")


def test_write_overwrites_existing_file(tmp_path):
    writer = get_writer("markdown")
    writer.write(make_doc("a.md", text="처음"), tmp_path)
    writer.write(make_doc("a.md", text="나중"), tmp_path)
    assert "나중" in (tmp_path / "a.md").read_text(encoding="utf-8")
    assert "처음" not in (tmp_path / "a.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("doc_id", ["../escape.md", "a/../../escape.md", "/abs/escape.md"])
def test_write_rejects_paths_outside_output_dir(tmp_path, doc_id):
    out = tmp_path / "out"
    with pytest.raises(ValueError):
        get_writer("markdown").write(make_doc(doc_id), out)
    assert not (tmp_path / "escape.md").exists()
