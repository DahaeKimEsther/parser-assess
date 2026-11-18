"""마크다운 writer: 파싱 결과를 front matter가 붙은 `.md` 파일로 저장한다."""

import json
from pathlib import Path, PurePosixPath

from rag_lab.parser.models import ParsedDocument
from rag_lab.parser.registry import register_writer


def _quote(value: str) -> str:
    # JSON 문자열은 YAML의 큰따옴표 문자열로도 유효해서, 따옴표/콜론/역슬래시가 있어도 안전하다.
    return json.dumps(value, ensure_ascii=False)


def render_markdown(doc: ParsedDocument) -> str:
    # doc_id는 항상 `/` 구분자이므로 OS와 상관없이 PurePosixPath로 제목을 뽑는다.
    lines = [
        f"title: {_quote(PurePosixPath(doc.doc_id).stem)}",
        f"source: {_quote(doc.doc_id)}",
        f"doc_type: {_quote(doc.doc_type)}",
    ]
    parser = doc.metadata.get("parser")
    if parser:
        lines.append(f"parser: {_quote(parser)}")
    if doc.metadata.get("empty"):
        lines.append("empty: true")

    content = "---\n" + "\n".join(lines) + "\n---\n"
    body = doc.text.rstrip("\n")
    if body:
        content += "\n" + body + "\n"
    return content


@register_writer("markdown")
class MarkdownWriter:
    def write(self, doc: ParsedDocument, out_dir: Path) -> Path:
        relative = doc.doc_id if doc.doc_id.lower().endswith(".md") else doc.doc_id + ".md"
        base = out_dir.resolve()
        target = (out_dir / relative).resolve()
        if target == base or not target.is_relative_to(base):
            raise ValueError(f"출력 폴더 밖으로 나가는 문서 경로입니다: {doc.doc_id}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_markdown(doc), encoding="utf-8", newline="\n")
        return target
