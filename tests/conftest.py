"""공통 테스트 설정."""

import pytest

from rag_lab.parser import registry


@pytest.fixture(autouse=True)
def isolated_registry():
    """테스트마다 레지스트리를 원래 상태로 되돌려 가짜 구현체 등록이 서로 새지 않게 한다."""
    parsers = dict(registry._PARSERS)
    writers = dict(registry._WRITERS)
    yield
    registry._PARSERS.clear()
    registry._PARSERS.update(parsers)
    registry._WRITERS.clear()
    registry._WRITERS.update(writers)
