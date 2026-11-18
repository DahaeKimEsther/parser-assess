"""마크다운 파서: 이미 마크다운이므로 내용을 그대로 쓴다."""

from pathlib import Path

from rag_lab.parser.models import ParsedDocument
from rag_lab.parser.parsers._common import read_text_document
from rag_lab.parser.registry import register_parser


@register_parser("markdown")
class MarkdownParser:
    def parse(self, path: Path, doc_id: str) -> ParsedDocument:
        return read_text_document(path, doc_id)
