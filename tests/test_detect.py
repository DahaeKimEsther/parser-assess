from pathlib import Path

import pytest

from rag_lab.parser.detect import detect_type


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("a.md", "md"),
        ("A.MD", "md"),
        ("dir/sub/report.PDF", "pdf"),
        ("archive.tar.gz", "gz"),
        ("README", ""),
        (".gitignore", ""),
    ],
)
def test_detect_type(name, expected):
    assert detect_type(Path(name)) == expected
