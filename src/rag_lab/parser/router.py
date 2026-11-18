"""문서 유형에 맞는 파서를 고르는 라우터와 그 설정(TOML) 로더."""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rag_lab.parser.base import DocumentParser
from rag_lab.parser.errors import ParserConfigError
from rag_lab.parser.registry import get_parser

DEFAULT_WRITER = "markdown"
DEFAULT_OUT_DIR = ".cache/parsed"


@dataclass(frozen=True)
class RoutingConfig:
    routes: dict[str, str]
    fallback: str | None
    writer: str
    out_dir: Path


def _normalize_type(key: str) -> str:
    return key.lstrip(".").lower()


def load_routing(path: Path) -> RoutingConfig:
    """라우팅 설정 파일을 읽는다. 구조가 잘못되면 어떤 항목이 문제인지 담아 ParserConfigError를 던진다."""
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        raise ParserConfigError(f"라우팅 설정 파일을 찾을 수 없습니다: {path}") from None
    except tomllib.TOMLDecodeError as e:
        raise ParserConfigError(f"라우팅 설정 파일({path})을 읽을 수 없습니다: {e}") from None

    raw_routes = data.get("routes")
    if not isinstance(raw_routes, dict):
        raise ParserConfigError(f"설정 파일({path})에 [routes] 표가 필요합니다.")
    routes: dict[str, str] = {}
    for key, value in raw_routes.items():
        if not isinstance(value, str):
            raise ParserConfigError(f"[routes] '{key}'의 값은 파서 이름(문자열)이어야 합니다.")
        routes[_normalize_type(key)] = value

    fallback = data.get("fallback")
    if fallback is not None and not isinstance(fallback, str):
        raise ParserConfigError("fallback은 파서 이름(문자열)이어야 합니다.")

    output: Any = data.get("output", {})
    if not isinstance(output, dict):
        raise ParserConfigError("[output]은 표여야 합니다.")
    writer = output.get("writer", DEFAULT_WRITER)
    out_dir = output.get("dir", DEFAULT_OUT_DIR)
    if not isinstance(writer, str) or not isinstance(out_dir, str):
        raise ParserConfigError("[output]의 writer와 dir은 문자열이어야 합니다.")

    return RoutingConfig(routes=routes, fallback=fallback, writer=writer, out_dir=Path(out_dir))


class ParserRouter:
    """유형 → 파서. 설정에 적힌 파서 이름은 만들 때 모두 확인해서, 처리 도중이 아니라 시작 전에 오류를 낸다."""

    def __init__(self, config: RoutingConfig) -> None:
        self.config = config
        self._parsers: dict[str, DocumentParser] = {}
        names = set(config.routes.values())
        if config.fallback:
            names.add(config.fallback)
        for name in sorted(names):
            self._parsers[name] = get_parser(name)

    def select(self, doc_type: str) -> tuple[str, DocumentParser] | None:
        """유형에 맞는 (파서 이름, 파서)를 돌려준다. 매핑도 폴백도 없으면 None이다."""
        name = self.config.routes.get(doc_type) or self.config.fallback
        if name is None:
            return None
        return name, self._parsers[name]
