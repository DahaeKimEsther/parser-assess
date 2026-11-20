# TODO

작업을 시작하기 전에 읽는다. 작성과 갱신은 요청할 때만 한다. (공개 저장소이므로 개인 경로/이메일/사내 문서 내용은 적지 않는다.)

## 참고 세션

최신 세션이 위. 작성 규칙은 CLAUDE.md의 "TODO.md 작성 규칙" 참고.

- `1f0f0453-109f-418e-9aa8-39e73c3455f2`: 평가 계획을 ParseBench-2 기반으로 재작성(T1~T5), parse-bench 설치와 첫 실행. 결정 배경(공식 파이프라인 그대로 쓰는 이유 등)이 이 대화에 있다.
- `53bf1886-0917-4f3f-8871-043b79bcad83`: parser 모듈 설계, LiteParse/ParseBench 조사, 1단계(LiteParse 파서, 복잡도, `complexity` CLI) 구현. 설계 결정의 배경(OCR을 끈 이유, 평면 `assess/` 구조 등)이 이 대화에 있다.

## 현재 상태

- 1단계 완료: LiteParse PDF 파서(`parsers/liteparse.py`), PDF 구조 복잡도(`complexity.py`), `rag-lab-parser complexity <PDF|폴더>`
- 선택 의존성이라 `uv sync --extra liteparse`로 설치해야 한다. 미설치여도 나머지 테스트는 통과하고 실제 PDF 테스트만 건너뛴다.
- 지금까지 확인한 샘플은 직접 만든 합성 PDF뿐이다. **실제 문서로는 아직 검증하지 않았다.**
- 평가 계획을 바꿨다: 직접 만든 샘플 대신 ParseBench-2 문서를 우리 복잡도 점수로 쉬운 순서대로 정렬해, LiteParse의 공식 점수와 함께 본다. 공식 파이프라인과 채점기를 그대로 쓴다(자체 채점기 없음).
- T1(parse-bench 실행 방법과 결과 형식 확인) 진행 중: 도구 설치, 옵션 확인, v1 `--test` 실행(실행 환경 문제로 실패)까지 끝났고 v2 `--test` 실행이 남았다.
- 미커밋 `scripts/make_samples.py`와 git 제외 `data/samples/`가 남아 있다(계획 밖의 합성 샘플).

## 다음 목표

LiteParse가 **어떤 구조 요소까지 쓸 만한지**, 쉬운 문서부터 어려운 문서 순서로 확인한다.

- [ ] T1: v2를 `--test`로 실행해 결과 폴더 형식, 문서 id 키, 공식 파이프라인의 LiteParse 버전(우리는 2.19.0)을 기록한다. 명령은 `알아둘 사실`의 "parse-bench 실행" 참고
- [ ] T2: `src/rag_lab/assess/{__init__,cli}.py`와 `pyproject.toml`의 `rag-lab-assess` 진입점. 복잡도 점수 오름차순 정렬, 공식 점수 결합, 결과 폴더가 없거나 형식을 모르면 종료 코드 2, 점수 없는 문서 수 표시. 공식 설정을 대리값으로 쓴 지름길에는 주석 `gstack-shortcut(dec-ce6bd669-ab2f-432b-a605-e73c03d8461a)`를 붙인다
- [ ] T3: `tests/test_assess_cli.py`
- [ ] T4: CLAUDE.md의 파일 구조와 개발 명령어 갱신. 개발 명령어에 `uv tool install "parse-bench[liteparse]"` 한 줄을 반드시 넣는다(옵션 이름은 T1에서 확인된 것으로)
- [ ] T5(낮은 우선순위): 결과로 복잡도 점수식을 보정(`complexity.py` 상단의 가중치/임계값)
- [ ] 미커밋 `scripts/make_samples.py`와 `data/samples/`를 남길지 지울지 정한다

## 알아둘 사실

- OCR은 꺼져 있다(`ocr_enabled=False`). 스캔 PDF는 본문이 비고 출력 front matter에 `empty: true`가 붙는다.
- LiteParse는 글자가 아주 적은 페이지를 `sparse-text`로 보고 `needs_ocr=True`를 준다. 그래서 짧은 정상 페이지도 스캔으로 집계된다.
- 복잡도 점수식(스캔 0.40, 다단 0.25, 표 0.20, 그림 0.15)과 등급 임계값(0.15, 0.40)은 **잠정값**이다.
- LiteParse 예외: 없는 파일은 `FileNotFoundError`, 깨진 PDF는 `liteparse.types.ParseError`, PDF가 아닌 파일은 예외 없이 빈 결과가 나온다.
- 첫 LiteParse 호출은 초기화로 약 1.4초 걸리고 이후는 수십 ms다. `quiet=True`를 주지 않으면 단계별 시간 로그가 출력된다.
- 구조 결정: `assess/`는 `parser/`를 import만 하고 `parser/`는 `assess/`를 모른다. 두 번째 평가 대상이 생기면 `assess/parser/`로 나눈다. `complexity.py`는 라우터가 재사용할 것이므로 `parser/`에 둔다.

- **parse-bench 실행**(실측): `uv tool install "parse-bench[liteparse]"`로 프로젝트 밖 전역 도구로 설치한다(`pyproject.toml` 불변, 버전 2.1.3). 이 도구는 LiteParse를 라이브러리가 아니라 `lit` 실행 파일로 호출하는데 PATH에 없으므로 `$env:LITEPARSE_BIN = "$(uv tool dir)\parse-bench\Scripts\lit.exe"`로 지정한다(창을 닫으면 사라짐). `data\parsebench`에서 실행하면 데이터와 결과가 `data/`(git 제외) 안에 생긴다. 예: `parse-bench run liteparse_markdown --dataset parsebench-2 --test --open_report=False --force=True`
- parse-bench 옵션(실측): `--test`는 작은 테스트 세트(카테고리당 3개)를 받는다. `--test`를 빼면 전체(v2는 9,215개 파일, 예상 3시간 이상)를 받으니 주의한다. `--open_report` 기본값이 True라 브라우저가 열린다. `--group`은 카테고리 필터다. `--dataset` 기본값은 v1(`parsebench`)이다.
- parse-bench 결과 형식(v1 실행 기준): `output/liteparse_markdown/`에 `_summary.json`, `_errors.json`, `_metadata.json`이 생기고 문서 id는 `카테고리/파일이름`이다. 공식 `liteparse_markdown` 설정은 `output_format=markdown`, `ocr_enabled=false`로 우리와 같다.
- ParseBench-2(서브에이전트 조사, 일부 요약에 의존): LlamaIndex가 올린 v1의 후속이며 v1과 점수를 비교할 수 없다. 4,317페이지, 13개 하위 세트, 약 1.57GB, Apache-2.0이다. PDF마다 정답(`.test.json`)과 기준 마크다운이 들어 있다. 문서별 난이도 필드는 없다(그래서 우리 복잡도 점수로 정렬한다).
- `--dataset parsebench-2`는 설치된 parse-bench(2.1.3)가 받는 값이다(실측): HuggingFace `llamaindex/ParseBench-2`로 풀려 `data_parsebench-2` 폴더에 받기 시작했다. `--test` 없이 실행하면 9,215개 파일 전체를 받는다. `--test`가 v2에서 작은 부분만 받는지는 아직 확인하지 못했다.
- 정리할 남은 파일(`data/parsebench/` 아래, 모두 git 제외): v1 `--test` 데이터 `data/test`(몇 MB)와 실패한 실행 결과 `output/liteparse_markdown`. v2 `--test`가 같은 `data/test`를 쓸 가능성이 있으니(미검증) v2 실행 전에 지우지 말고 내용을 먼저 확인한다. 받다 만 `data_parsebench-2`는 지웠다. 폴더가 남아 있으면 다시 받지 않고 불완전한 데이터로 실행할 수 있다(미검증).
- 다운로드 경고: HF 토큰이 없으면 속도가 느리다는 경고가 나온다. 필수는 아니다. 토큰은 저장소나 대화에 적지 않는다.
- `parse-bench run --help`는 페이저에서 멈춘다. `parse-bench run --help *> data\help.txt`처럼 파일로 받아 읽는다(`|` 파이프는 비어 있었다).
- 합성 샘플 탐침 결과(`scripts/make_samples.py`로 만든 깨끗한 PDF 7건, LiteParse 2.19.0): 헤딩은 `#`/`##`, 목록은 `- `, 격자/무격자 표는 둘 다 마크다운 표로 나왔다. 2단은 읽는 순서는 맞지만 한 문단으로 합쳐졌고, 한국어(TTF/CID 폰트 모두)는 글자는 정확하나 문장 줄바꿈이 공백으로 합쳐졌다. 짧은 목록/표/한국어 페이지는 모두 scan으로 집계돼 complex가 나왔다(sparse-text 오탐). 합성 문서라 실제 품질의 근거는 아니다.
- 터미널에 긴 명령을 붙여 넣으면 줄이 끊겨 깨진다. 짧은 줄로 나누거나 `$a = '인자',...` 후 `parse-bench @a`처럼 변수로 넘긴다.

## 열린 질문

- 공식 파이프라인은 `lit`을 json 형식으로 호출해 변환하는 것으로 보인다. 우리 라이브러리의 markdown 출력과 같은가(다르면 우리 `LiteParseParser`를 parse-bench 파이프라인으로 등록하는 B안 검토)
- v2에 한국어 문서가 있는가(독일어, 일본어, 중국어 파일 이름은 보이나 한국어는 확인하지 못했다)
- `--test`가 v2에서도 작은 부분만 받는가(v2 전체는 9,215개 파일이라 3시간 이상 걸린다)
- 한 페이지짜리 문서에서 sparse-text 오탐이 복잡도 정렬을 왜곡하는가
- 사내 문서가 PDF 위주인가, hwp/Word도 섞여 있는가(LiteParse는 hwp 미지원)
- 검색에 표/헤딩 구조가 얼마나 중요한가, 즉 "쓸 만함"의 기준을 무엇으로 볼 것인가
- 저장소 이름

## 이후 단계

- [ ] 복잡도 기준을 라우터에 연결(유형 + 복잡도로 파서 선택)
- [ ] OCR 파서 추가(한국어 traineddata 동작 확인 필요)
- [ ] OKF writer 추가(필요해질 때)
