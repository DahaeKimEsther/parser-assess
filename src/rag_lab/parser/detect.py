"""문서 유형 판별."""

from pathlib import Path


def detect_type(path: Path) -> str:
    """확장자(점 없이, 소문자)를 유형으로 쓴다. 확장자가 없으면 빈 문자열이다."""
    return path.suffix.lstrip(".").lower()
