"""LiteParse(선택 의존성) 불러오기와 공용 엔진.

`liteparse`는 `uv sync --extra liteparse`로 설치해야 하는 선택 의존성이라서, 모듈을 import하는 시점이 아니라
실제로 쓰는 시점에 불러온다. 그래야 LiteParse가 없는 환경에서도 나머지 기능이 그대로 동작한다.
"""

from functools import lru_cache
from typing import Any

from parser_assess.errors import ParserConfigError

INSTALL_HINT = "LiteParse가 설치되어 있지 않습니다. `uv sync --extra liteparse`로 설치하세요."


def import_liteparse() -> Any:
    try:
        import liteparse
    except ImportError:
        raise ParserConfigError(INSTALL_HINT) from None
    return liteparse


def make_engine() -> Any:
    """OCR을 끈 LiteParse를 만든다.

    OCR을 켜면 첫 실행 때 언어 데이터(traineddata)를 내려받을 수 있고 한국어 동작도 확인되지 않아서 끈다.
    `quiet`는 단계별 시간 로그가 표준 출력에 계속 찍히는 것을 막는다.
    """
    liteparse = import_liteparse()
    return liteparse.LiteParse(output_format="markdown", ocr_enabled=False, quiet=True)


@lru_cache(maxsize=1)
def get_engine() -> Any:
    """프로세스 안에서 재사용하는 엔진. 첫 호출만 초기화 때문에 오래 걸린다(실측 약 1.4초)."""
    return make_engine()
