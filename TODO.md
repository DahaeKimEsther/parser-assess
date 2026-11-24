# TODO

작업을 시작하기 전에 읽는다. 작성과 갱신은 요청할 때만 한다. (공개 저장소이므로 개인 경로/이메일/사내 문서 내용은 적지 않는다.)

## 참고 세션

최신 세션이 위. 작성 규칙은 CLAUDE.md의 "TODO.md 작성 규칙" 참고.

- `8d75de71-031f-439e-a007-40e27a194e84`: TODO.md 작성 규칙을 짧게 유지하는 방향으로 고치고 TODO.md를 줄임.
- `5aee983f-c3bc-4c1e-b9f4-ee34d08906c9`: 저장소를 파서 평가 전용 `parser-assess`로 좁힘. 결정 배경은 `docs/decisions.md` 참고.

## 현재 상태

- 남은 기능은 PDF 복잡도(`complexity.py`), LiteParse 엔진(`_liteparse.py`), `parser-assess complexity <PDF|폴더>`다. `uv sync --extra liteparse` 설치 후 24 passed(실측).
- **실제 문서로는 검증하지 않았다.** 확인한 PDF는 최소 PDF와 합성 PDF뿐이다.
- 평가 방식: ParseBench-2 문서를 우리 복잡도 점수로 쉬운 순서대로 정렬해 LiteParse 공식 점수와 함께 본다. 공식 파이프라인과 채점기를 그대로 쓴다(자체 채점기 없음).
- T1 진행 중: v1 `--test`는 실행 환경 문제로 실패했고, v2 `--test` 실행이 남았다.

## 다음 목표

LiteParse가 **어떤 구조 요소까지 쓸 만한지**, 쉬운 문서부터 어려운 문서 순서로 확인한다.

- [ ] **T0(최우선)**: ParseBench-2 데이터를 직접 살펴본다
- [ ] T1: v2를 `--test`로 실행해 결과 폴더 형식, 문서 id 키, 공식 파이프라인의 LiteParse 버전(우리는 2.19.0), `--test`가 v2에서도 작은 부분만 받는지를 기록한다
- [ ] T2: `src/parser_assess/cli.py`에 점수 결합 하위 명령 추가. 복잡도 점수 오름차순 정렬, 공식 점수 결합, 결과 폴더가 없거나 형식을 모르면 종료 코드 2, 점수 없는 문서 수 표시
- [ ] T3: `tests/test_assess_cli.py`
- [ ] T5(낮은 우선순위): 결과로 복잡도 점수식 보정(`complexity.py` 상단의 가중치/임계값)
- [ ] 실제 PDF로 `parser-assess complexity`를 돌려 이름 변경 전(`618f748` 이전 커밋)과 같은 표가 나오는지 비교

## 알아둘 사실

- OCR은 꺼져 있다(`ocr_enabled=False`). 스캔 PDF는 본문이 비고 출력에 `empty: true`가 붙는다.
- LiteParse는 글자가 아주 적은 페이지를 `sparse-text`로 보고 `needs_ocr=True`를 준다. 그래서 짧은 정상 페이지(목록, 표, 한국어)도 스캔으로 집계되어 complex가 나온다(합성 샘플에서 관찰).
- 복잡도 점수식(스캔 0.40, 다단 0.25, 표 0.20, 그림 0.15)과 등급 임계값(0.15, 0.40)은 **잠정값**이다.
- 계획 파일이 `.claude/.claude/plans/`에 생긴 적이 있다. 세션 중 작업 폴더가 `.claude`로 바뀌면 상대 경로인 `plansDirectory`(`.claude/plans`)가 그 폴더 기준으로 풀린 것으로 보인다(미검증). 작업 중 `.claude` 안으로 `cd`하지 말고 절대 경로를 쓴다.
- LiteParse 예외: 없는 파일은 `FileNotFoundError`, 깨진 PDF는 `liteparse.types.ParseError`, PDF가 아닌 파일은 예외 없이 빈 결과가 나온다.
- **parse-bench 실행**(실측): `uv tool install "parse-bench[liteparse]"`로 전역 설치한다(버전 2.1.3). `lit` 실행 파일이 PATH에 없으므로 `$env:LITEPARSE_BIN = "$(uv tool dir)\parse-bench\Scripts\lit.exe"`로 지정한다(창을 닫으면 사라짐). `data\parsebench`에서 실행하면 데이터와 결과가 `data/`(git 제외) 안에 생긴다. 예: `parse-bench run liteparse_markdown --dataset parsebench-2 --test --open_report=False --force=True`
- parse-bench 옵션 주의(실측): `--test`는 카테고리당 3개만 받는다. 빼면 v2 전체(9,215개 파일, 3시간 이상)를 받는다. `--open_report` 기본값이 True라 브라우저가 열린다. `--dataset` 기본값은 v1(`parsebench`)이다.
- parse-bench 결과 형식(v1 기준): `output/liteparse_markdown/`에 `_summary.json`, `_errors.json`, `_metadata.json`이 생기고 문서 id는 `카테고리/파일이름`이다. 공식 `liteparse_markdown` 설정은 `output_format=markdown`, `ocr_enabled=false`로 우리와 같다.
- ParseBench-2(서브에이전트 조사, 일부 요약에 의존): v1의 후속이며 v1과 점수를 비교할 수 없다. 4,317페이지, 약 1.57GB, Apache-2.0이다. PDF마다 정답(`.test.json`)과 기준 마크다운이 있고, 문서별 난이도 필드는 없다(그래서 우리 복잡도 점수로 정렬한다).

## 열린 질문

- 공식 파이프라인은 `lit`을 json 형식으로 호출해 변환하는 것으로 보인다. 우리 라이브러리의 markdown 출력과 같은가(다르면 우리 `LiteParseParser`를 parse-bench 파이프라인으로 등록하는 B안 검토)
- v2에 한국어 문서가 있는가(독일어, 일본어, 중국어 파일 이름은 보이나 한국어는 확인하지 못했다)
- 한 페이지짜리 문서에서 sparse-text 오탐이 복잡도 정렬을 왜곡하는가
- 사내 문서가 PDF 위주인가, hwp/Word도 섞여 있는가(LiteParse는 hwp 미지원)
- 검색에 표/헤딩 구조가 얼마나 중요한가, 즉 "쓸 만함"의 기준을 무엇으로 볼 것인가

## 이후 단계

- [ ] 평가 대상 파서 추가(LiteParse 외). 한국어 OCR 동작 확인이 필요하다
- 라우터 연결, OKF writer, 청킹·임베딩·검색은 하지 않기로 했다(`docs/decisions.md` 참고).
