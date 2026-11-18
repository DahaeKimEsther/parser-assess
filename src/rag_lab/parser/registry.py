"""이름으로 파서와 writer를 찾는 등록 장치.

구현체 클래스에 `@register_parser("이름")`을 붙이면 설정 파일에 이름만 적어 쓸 수 있다.
"""

from typing import Any, Callable

from rag_lab.parser.errors import ParserConfigError

_PARSERS: dict[str, type] = {}
_WRITERS: dict[str, type] = {}


def _register(table: dict[str, type], kind: str, name: str) -> Callable[[type], type]:
    def decorator(cls: type) -> type:
        if name in table:
            raise ValueError(f"이미 등록된 {kind} 이름입니다: {name}")
        table[name] = cls
        return cls

    return decorator


def _get(table: dict[str, type], kind: str, name: str, params: dict[str, Any]) -> Any:
    if name not in table:
        available = ", ".join(sorted(table)) or "(없음)"
        raise ParserConfigError(f"알 수 없는 {kind} '{name}'입니다. 사용 가능: {available}")
    return table[name](**params)


def register_parser(name: str) -> Callable[[type], type]:
    return _register(_PARSERS, "parser", name)


def register_writer(name: str) -> Callable[[type], type]:
    return _register(_WRITERS, "writer", name)


def get_parser(name: str, **params: Any) -> Any:
    return _get(_PARSERS, "parser", name, params)


def get_writer(name: str, **params: Any) -> Any:
    return _get(_WRITERS, "writer", name, params)


def available_parsers() -> list[str]:
    return sorted(_PARSERS)


def available_writers() -> list[str]:
    return sorted(_WRITERS)
