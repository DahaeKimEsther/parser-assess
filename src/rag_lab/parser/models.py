"""파서와 writer가 주고받는 데이터 모양."""

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ParsedDocument:
    """파서가 만든 결과. doc_id는 문서 폴더 기준 상대 경로(구분자는 `/`)다."""

    doc_id: str
    source_path: Path
    doc_type: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProcessingRecord:
    """문서 하나를 처리한 기록. status는 ok, skipped, failed 중 하나다."""

    doc_id: str
    doc_type: str
    parser: str | None
    ms: float
    size_bytes: int
    status: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
