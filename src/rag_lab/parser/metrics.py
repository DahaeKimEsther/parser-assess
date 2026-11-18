"""처리 시간 측정, 기록 저장(JSONL), 유형/파서별 요약."""

import json
import math
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator

from rag_lab.parser.models import ProcessingRecord


_REQUIRED_KEYS = frozenset({"doc_type", "status", "ms"})


class _Timer:
    ms: float = 0.0


@contextmanager
def timed(clock: Callable[[], float] = time.perf_counter) -> Iterator[_Timer]:
    """with 블록의 실행 시간을 밀리초로 재서 `t.ms`에 넣는다. 블록에서 예외가 나도 시간은 기록된다."""
    timer = _Timer()
    start = clock()
    try:
        yield timer
    finally:
        timer.ms = (clock() - start) * 1000


def append_records(path: Path, records: Iterable[ProcessingRecord]) -> None:
    """기록을 JSONL 파일 끝에 덧붙인다. 같은 호출의 기록은 같은 recorded_at(UTC)을 갖는다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    recorded_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(path, "a", encoding="utf-8") as f:
        for record in records:
            row = {**record.to_dict(), "recorded_at": recorded_at}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_records(path: Path) -> list[dict[str, Any]]:
    """JSONL 기록을 읽는다. 파일이 없으면 빈 목록, 깨진 줄은 건너뛴다."""
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict) and _REQUIRED_KEYS <= row.keys():
                rows.append(row)
    return rows


def percentile(values: list[float], p: float) -> float:
    """가장 가까운 순위(nearest-rank) 방식의 백분위수."""
    ordered = sorted(values)
    rank = max(1, math.ceil(p / 100 * len(ordered)))
    return ordered[rank - 1]


@dataclass(frozen=True)
class GroupStats:
    """(유형, 파서) 묶음의 요약. 시간 통계는 성공(ok)한 문서만 대상이고, 성공이 없으면 None이다."""

    doc_type: str
    parser: str | None
    count: int
    ok: int
    skipped: int
    failed: int
    mean_ms: float | None
    p50_ms: float | None
    p95_ms: float | None
    docs_per_sec: float | None


def summarize(rows: Iterable[dict[str, Any]]) -> list[GroupStats]:
    groups: dict[tuple[str, str | None], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["doc_type"], row.get("parser"))].append(row)

    stats: list[GroupStats] = []
    for (doc_type, parser), items in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1] or "")):
        times = [float(r["ms"]) for r in items if r["status"] == "ok"]
        total_ms = sum(times)
        stats.append(
            GroupStats(
                doc_type=doc_type,
                parser=parser,
                count=len(items),
                ok=len(times),
                skipped=sum(1 for r in items if r["status"] == "skipped"),
                failed=sum(1 for r in items if r["status"] == "failed"),
                mean_ms=total_ms / len(times) if times else None,
                p50_ms=percentile(times, 50) if times else None,
                p95_ms=percentile(times, 95) if times else None,
                docs_per_sec=len(times) / (total_ms / 1000) if times and total_ms > 0 else None,
            )
        )
    return stats


def _fmt(value: float | None) -> str:
    return "-" if value is None else f"{value:.1f}"


def format_summary(stats: list[GroupStats]) -> str:
    if not stats:
        return "기록된 처리 결과가 없습니다."
    header = ["유형", "파서", "건수", "ok", "skipped", "failed", "평균ms", "p50ms", "p95ms", "문서/초"]
    table = [header]
    for s in stats:
        table.append(
            [
                s.doc_type or "(없음)",
                s.parser or "-",
                str(s.count),
                str(s.ok),
                str(s.skipped),
                str(s.failed),
                _fmt(s.mean_ms),
                _fmt(s.p50_ms),
                _fmt(s.p95_ms),
                _fmt(s.docs_per_sec),
            ]
        )
    widths = [max(len(row[i]) for row in table) for i in range(len(header))]
    return "\n".join("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)) for row in table)
