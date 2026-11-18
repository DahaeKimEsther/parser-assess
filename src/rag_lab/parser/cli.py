"""명령줄 진입점: `rag-lab-parser run <문서 폴더>`, `rag-lab-parser stats`."""

import argparse
import sys
from collections import Counter
from pathlib import Path

import rag_lab.parser  # noqa: F401  기본 파서/writer 등록
from rag_lab.parser.errors import ParserConfigError
from rag_lab.parser.metrics import append_records, format_summary, load_records, summarize
from rag_lab.parser.pipeline import process_directory
from rag_lab.parser.registry import get_writer
from rag_lab.parser.router import ParserRouter, load_routing

DEFAULT_CONFIG = "config/parser_routing.toml"
DEFAULT_METRICS = ".cache/parser/metrics.jsonl"
MAX_FAILED_SHOWN = 10


def _cmd_run(args: argparse.Namespace) -> int:
    config = load_routing(Path(args.config))
    router = ParserRouter(config)  # 파서 이름 오류는 여기서 처리 전에 드러난다.
    writer = get_writer(config.writer)  # writer 이름 오류도 마찬가지다.
    root = Path(args.docs_dir)
    if not root.is_dir():
        raise ParserConfigError(f"문서 폴더를 찾을 수 없습니다: {root}")

    records = process_directory(root, router, writer, config.out_dir)
    append_records(Path(args.metrics), records)

    counts = Counter(r.status for r in records)
    print(f"처리 완료: ok {counts['ok']} / skipped {counts['skipped']} / failed {counts['failed']}")
    print(f"출력 폴더: {config.out_dir}   처리 시간 기록: {args.metrics}")
    failed = [r for r in records if r.status == "failed"]
    for r in failed[:MAX_FAILED_SHOWN]:
        print(f"  실패: {r.doc_id} ({r.error})")
    if len(failed) > MAX_FAILED_SHOWN:
        print(f"  ... 외 {len(failed) - MAX_FAILED_SHOWN}건")
    print()
    print(format_summary(summarize(r.to_dict() for r in records)))
    return 0


def _cmd_stats(args: argparse.Namespace) -> int:
    print(format_summary(summarize(load_records(Path(args.metrics)))))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rag-lab-parser", description="문서 유형별 처리와 처리 시간 측정")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="문서 폴더를 처리하고 처리 시간을 기록한다")
    run.add_argument("docs_dir", help="처리할 문서 폴더")
    run.add_argument("--config", default=DEFAULT_CONFIG, help=f"라우팅 설정 파일 (기본: {DEFAULT_CONFIG})")
    run.add_argument("--metrics", default=DEFAULT_METRICS, help=f"처리 시간 기록 파일 (기본: {DEFAULT_METRICS})")
    run.set_defaults(func=_cmd_run)

    stats = sub.add_parser("stats", help="쌓인 처리 시간을 유형/파서별로 요약한다")
    stats.add_argument("--metrics", default=DEFAULT_METRICS, help=f"처리 시간 기록 파일 (기본: {DEFAULT_METRICS})")
    stats.set_defaults(func=_cmd_stats)
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
