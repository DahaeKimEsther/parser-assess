"""PDF 파서(LiteParse): 텍스트 레이어가 있는 PDF를 마크다운으로 바꾼다.

규칙 기반이라 가볍고 빠르지만, 스캔 문서(OCR 필요)와 복잡한 표/차트는 약하다.
OCR은 끈 상태로 고정한다. 문서가 어느 정도 복잡한지는 `rag-lab-parser complexity`로 먼저 확인할 수 있다.
"""

from pathlib import Path

from rag_lab.parser._liteparse import get_engine, import_liteparse
from rag_lab.parser.models import ParsedDocument
from rag_lab.parser.registry import register_parser

# OCR 없이 스캔 PDF를 읽으면 본문 대신 이런 빈 코드 블록만 나온다. 이를 제거한 뒤 비어 있는지 본다.
_EMPTY_BLOCK = "```text\n\n```"


@register_parser("liteparse")
class LiteParseParser:
    def __init__(self) -> None:
        # 라우터가 처리 시작 전에 파서를 만들기 때문에, 설치되지 않았으면 여기서 안내와 함께 실패한다.
        import_liteparse()

    def parse(self, path: Path, doc_id: str) -> ParsedDocument:
        result = get_engine().parse(str(path))
        text = result.text
        metadata: dict = {"total_pages": result.total_pages}
        if not text.replace(_EMPTY_BLOCK, "").strip():
            metadata["empty"] = True  # 텍스트 레이어가 없는 스캔 PDF일 가능성이 크다(OCR 필요)
        return ParsedDocument(doc_id=doc_id, source_path=path, doc_type="pdf", text=text, metadata=metadata)
