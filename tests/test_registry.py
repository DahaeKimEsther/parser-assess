import pytest

from rag_lab.parser.errors import ParserConfigError
from rag_lab.parser.registry import (
    available_parsers,
    available_writers,
    get_parser,
    get_writer,
    register_parser,
    register_writer,
)


def test_register_and_get_parser_with_params():
    @register_parser("dummy_a")
    class A:
        def __init__(self, size: int = 1):
            self.size = size

    assert get_parser("dummy_a", size=5).size == 5
    assert "dummy_a" in available_parsers()


def test_parser_and_writer_registries_are_separate():
    @register_parser("same_name")
    class P: ...

    @register_writer("same_name")
    class W: ...

    assert isinstance(get_parser("same_name"), P)
    assert isinstance(get_writer("same_name"), W)
    assert "same_name" in available_writers()


def test_unknown_parser_lists_available_names():
    @register_parser("known_one")
    class A: ...

    with pytest.raises(ParserConfigError) as e:
        get_parser("nope")
    assert "nope" in str(e.value)
    assert "known_one" in str(e.value)


def test_unknown_writer_lists_available_names():
    @register_writer("known_w")
    class W: ...

    with pytest.raises(ParserConfigError, match="known_w"):
        get_writer("nope")


def test_duplicate_registration_rejected():
    @register_parser("dup")
    class A: ...

    with pytest.raises(ValueError):
        register_parser("dup")(A)
