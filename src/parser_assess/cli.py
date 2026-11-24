"""명령줄 진입점: `parser-assess complexity <PDF 또는 폴더>`."""

import argparse
import sys
from pathlib import Path

from parser_assess.complexity import analyze_pdf
from parser_assess.errors import ParserConfigError


def _collect_pdfs(target: Path) -> list[tuple[str, Path]]:
    """(표시 이름, 경로) 목록. 폴더면 하위 폴더까지 .pdf(대소문자 무관)를 모으고, 파일이면 그 파일 하나를 쓴다."""
    if target.is_file():
        return [(target.name, target)]
    found = [p for p in target.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf"]
    return sorted(((p.relative_to(target).as_posix(), p) for p in found), key=lambda item: item[0])


def _cmd_complexity(args: argparse.Namespace) -> int:
    target = Path(args.target)
    if not target.exists():
        raise ParserConfigError(f"경로를 찾을 수 없습니다: {target}")
    pdfs = _collect_pdfs(target)
    if not pdfs:
        print(f"PDF 파일이 없습니다: {target}")
        return 0

    analyzed = []
    failed = []
    for name, path in pdfs:
        try:
            analyzed.append((name, analyze_pdf(path)))
        except ParserConfigError:
            raise  # LiteParse 미설치 같은 설정 문제는 파일마다 반복하지 않고 한 번만 알린다.
        except Exception as e:  # noqa: BLE001  파일 하나의 실패가 전체 분석을 멈추지 않게 한다.
            failed.append((name, str(e) or type(e).__name__))

    analyzed.sort(key=lambda item: item[1].score)  # 단순한 문서부터
    width = max(len(name) for name, _ in pdfs)
    print(f"{'file':<{width}}  {'pages':>5}  {'scan':>4}  {'cols':>4}  {'table':>5}  {'fig':>3}  {'score':>5}  level")
    for name, c in analyzed:
        print(
            f"{name:<{width}}  {c.pages:>5}  {c.scanned_pages:>4}  {c.multicolumn_pages:>4}  "
            f"{c.table_pages:>5}  {c.figure_pages:>3}  {c.score:>5.2f}  {c.level}"
        )
    for name, error in failed:
        print(f"{name:<{width}}  failed: {error}")
    print(f"\n분석 {len(analyzed)}건, 실패 {len(failed)}건. 점수식은 잠정값이다(complexity.py 참고).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="parser-assess", description="PDF 파서 평가")
    sub = parser.add_subparsers(dest="command", required=True)

    complexity = sub.add_parser("complexity", help="PDF의 구조 복잡도를 계산해 단순한 문서부터 보여 준다")
    complexity.add_argument("target", help="PDF 파일 또는 PDF가 들어 있는 폴더")
    complexity.set_defaults(func=_cmd_complexity)
    return parser


def main(argv: list[str] | None = None) -> int:
    # 콘솔 인코딩으로 표현할 수 없는 문자(파일명 등)가 있어도 출력이 죽지 않게 한다.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ParserConfigError as e:
        print(f"오류: {e}", file=sys.stderr)
        return 2
