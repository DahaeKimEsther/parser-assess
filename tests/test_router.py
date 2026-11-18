from pathlib import Path

import pytest

from rag_lab.parser.errors import ParserConfigError
from rag_lab.parser.registry import register_parser
from rag_lab.parser.router import ParserRouter, load_routing


def write_toml(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "routing.toml"
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def fake_parsers():
    @register_parser("fake_md")
    class FakeMd: ...

    @register_parser("fake_txt")
    class FakeTxt: ...


BASIC = """
[routes]
md = "fake_md"
txt = "fake_txt"

[output]
writer = "markdown"
dir = "out_dir"
"""


def test_load_routing_reads_routes_and_output(tmp_path):
    cfg = load_routing(write_toml(tmp_path, BASIC))
    assert cfg.routes == {"md": "fake_md", "txt": "fake_txt"}
    assert cfg.fallback is None
    assert cfg.writer == "markdown"
    assert cfg.out_dir == Path("out_dir")


def test_route_keys_are_normalized(tmp_path, fake_parsers):
    text = '[routes]\n".MD" = "fake_md"\n\n[output]\nwriter = "markdown"\ndir = "o"\n'
    cfg = load_routing(write_toml(tmp_path, text))
    assert cfg.routes == {"md": "fake_md"}


def test_select_known_type(tmp_path, fake_parsers):
    router = ParserRouter(load_routing(write_toml(tmp_path, BASIC)))
    name, parser = router.select("md")
    assert name == "fake_md"
    assert type(parser).__name__ == "FakeMd"


def test_select_unknown_type_without_fallback_returns_none(tmp_path, fake_parsers):
    router = ParserRouter(load_routing(write_toml(tmp_path, BASIC)))
    assert router.select("pdf") is None
    assert router.select("") is None


def test_select_uses_fallback(tmp_path, fake_parsers):
    text = 'fallback = "fake_txt"\n' + BASIC
    router = ParserRouter(load_routing(write_toml(tmp_path, text)))
    name, _ = router.select("pdf")
    assert name == "fake_txt"


def test_unknown_parser_name_fails_when_building_router(tmp_path, fake_parsers):
    text = BASIC.replace('"fake_txt"', '"no_such_parser"')
    with pytest.raises(ParserConfigError, match="no_such_parser"):
        ParserRouter(load_routing(write_toml(tmp_path, text)))


def test_invalid_toml_raises_config_error(tmp_path):
    with pytest.raises(ParserConfigError):
        load_routing(write_toml(tmp_path, "[routes\nmd ="))


def test_missing_file_raises_config_error(tmp_path):
    with pytest.raises(ParserConfigError, match="routing.toml"):
        load_routing(tmp_path / "routing.toml")


def test_missing_routes_table_raises_config_error(tmp_path):
    with pytest.raises(ParserConfigError, match="routes"):
        load_routing(write_toml(tmp_path, '[output]\nwriter = "markdown"\ndir = "o"\n'))


def test_non_string_route_value_raises_config_error(tmp_path):
    text = '[routes]\nmd = 3\n\n[output]\nwriter = "markdown"\ndir = "o"\n'
    with pytest.raises(ParserConfigError, match="md"):
        load_routing(write_toml(tmp_path, text))
