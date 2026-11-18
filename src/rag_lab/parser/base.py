"""파서와 writer가 지켜야 하는 약속(인터페이스)."""

from pathlib import Path
from typing import Protocol

from rag_lab.parser.models import ParsedDocument


class DocumentParser(Protocol):
    """파일 하나를 읽어 텍스트로 바꾼다. 실패하면 예외를 던진다."""

    def parse(self, path: Path, doc_id: str) -> ParsedDocument: ...


class DocumentWriter(Protocol):
    """파싱 결과를 출력 폴더에 저장하고, 저장한 파일 경로를 돌려준다."""

    def write(self, doc: ParsedDocument, out_dir: Path) -> Path: ...
