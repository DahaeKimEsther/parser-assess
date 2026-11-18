"""문서 처리 흐름: 유형 판별 → 라우팅 → 파싱 → 출력, 그리고 시간 측정."""

from dataclasses import replace
from pathlib import Path

from rag_lab.parser.base import DocumentWriter
from rag_lab.parser.detect import detect_type
from rag_lab.parser.metrics import timed
from rag_lab.parser.models import ProcessingRecord
from rag_lab.parser.router import ParserRouter


def process(path: Path, doc_id: str, router: ParserRouter, writer: DocumentWriter, out_dir: Path) -> ProcessingRecord:
    """문서 하나를 처리해 기록을 돌려준다. 파싱이나 출력에서 예외가 나도 failed로 기록할 뿐 밖으로 던지지 않는다."""
    doc_type = detect_type(path)
    try:
        size = path.stat().st_size
    except OSError:
        size = 0

    selected = router.select(doc_type)
    if selected is None:
        return ProcessingRecord(doc_id, doc_type, None, 0.0, size, "skipped")

    parser_name, parser = selected
    status, error = "ok", None
    with timed() as t:
        try:
            doc = parser.parse(path, doc_id)
            doc = replace(doc, metadata={**doc.metadata, "parser": parser_name})
            writer.write(doc, out_dir)
        except Exception as e:  # 문서 하나의 실패가 배치 전체를 멈추지 않게 한다.
            status, error = "failed", f"{type(e).__name__}: {e}"
    return ProcessingRecord(doc_id, doc_type, parser_name, t.ms, size, status, error)


def list_documents(root: Path, exclude_dir: Path | None = None) -> list[Path]:
    """폴더 아래의 모든 파일을 정렬해서 돌려준다. 출력 폴더가 안에 있으면 그 아래는 제외한다."""
    excluded = exclude_dir.resolve() if exclude_dir else None
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if excluded is not None and path.resolve().is_relative_to(excluded):
            continue
        files.append(path)
    return sorted(files)


def process_directory(root: Path, router: ParserRouter, writer: DocumentWriter, out_dir: Path) -> list[ProcessingRecord]:
    records = []
    for path in list_documents(root, exclude_dir=out_dir):
        doc_id = path.relative_to(root).as_posix()
        records.append(process(path, doc_id, router, writer, out_dir))
    return records
