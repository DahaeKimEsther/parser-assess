"""텍스트 계열 파서가 함께 쓰는 읽기 함수."""

from pathlib import Path

from rag_lab.parser.detect import detect_type
from rag_lab.parser.models import ParsedDocument


def read_text_document(path: Path, doc_id: str) -> ParsedDocument:
    """UTF-8 파일을 읽는다. BOM은 떼고 줄바꿈은 `\\n`으로 통일하며, UTF-8이 아니면 UnicodeDecodeError를 던진다."""
    raw = path.read_bytes().decode("utf-8-sig")
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    metadata = {} if text.strip() else {"empty": True}
    return ParsedDocument(doc_id, path, detect_type(path), text, metadata)
