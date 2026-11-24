# CLAUDE.md

이 파일은 Claude Code(claude.ai/code)가 이 저장소의 코드를 작업할 때 참고할 지침을 제공합니다.

## 언어 및 커뮤니케이션 규칙

- **기본 응답 언어**: 한국어
- **코드 주석**: 한국어로 작성
- **커밋 메시지**: 한국어로 작성
- **문서화**: 한국어로 작성
- **변수명/함수명**: 영어 (코드 표준 준수)

## 프로젝트 개요

**parser-assess** - 파서가 벤치마크에서 어느 문서까지 쓸 만한지 판단하는 평가 도구 저장소. **public 저장소**이므로 공개되어도 되는 내용만 커밋합니다.

- **목표**: 파서(현재 LiteParse)를 벤치마크(ParseBench-2) 문서로 평가한다. 문서 복잡도 점수와 공식 채점 결과를 한 표로 합쳐, 어떤 구조 요소까지 쓸 만한지 확인한다. 문서 처리, 시간 측정, 청킹·임베딩·검색 확장은 하지 않는다.
- **기술 스택**: Python 3.12+, uv(`pyproject.toml` + `uv.lock`), 런타임 의존성 없음(표준 라이브러리만), 테스트는 pytest

## 작업 시작 전

- **`TODO.md`를 먼저 읽는다.** 현재 상태, 다음 작업 체크리스트, 알아둘 사실, 열린 질문이 들어 있다. 작성과 갱신은 **사용자가 요청할 때만** 한다. (`.claude/plans/`는 git 제외라 worktree에서 읽을 수 없으므로 인수인계는 `TODO.md`로 한다.)
- **계획이나 설계를 세우기 전에 `docs/decisions.md`를 읽는다.** 사용자가 확정한 결정과 접기로 한 항목이 들어 있다. 접은 항목은 다시 꺼내지 않고, 새 결정은 사용자가 확정한 뒤에만 적는다.
- **`.claude/plans/`는 임시 메모다.** 결정의 근거로 삼지 않는다. 따를 것은 `docs/decisions.md`, `Architecture.md`, `TODO.md`다.

### TODO.md 작성 규칙

- **언어/공개**: 한국어. 공개 저장소이므로 개인 경로, 이메일, 사내 문서 내용은 적지 않는다.
- **섹션 순서**: `참고 세션` → `현재 상태` → `다음 목표` → `알아둘 사실` → `열린 질문` → `이후 단계`. 새 섹션이 필요하면 `알아둘 사실` 앞에 추가한다.
- **체크리스트**: 할 일은 `- [ ]`, 끝낸 일은 `- [x]`로 바꾼다. 한 항목은 한 줄로, 무엇을 하는지가 드러나게 쓴다. 끝난 항목이 쌓이면 `현재 상태`에 요약하고 지운다.
- **알아둘 사실**: 코드나 git 기록에서 알 수 없는 것만 적는다. 실측해서 확인한 것과 잠정값/미검증을 구분해서 쓴다.
- **세션 id**: 사용자가 `TODO.md` 작성/갱신을 요청했을 때 **현재 세션 id를 `참고 세션`에 한 줄 추가**한다. 형식은 ``- `<세션 id>`: 한 줄 설명(무엇을 한 세션인지)``이며 최신 세션이 위에 온다. 세션 id는 대화 기록 파일(`~/.claude/projects/<프로젝트>/<세션 id>.jsonl`)의 파일 이름이고, 이어서 열 때는 `claude --resume <세션 id>`를 쓴다.
- **갱신 시점**: 사용자가 요청할 때만 작성/갱신한다. 작업을 끝냈다고 해서 요청 없이 `TODO.md`를 고치거나 커밋에 포함하지 않는다.

### worklog 작성 규칙

`TODO.md`가 "지금 상태와 다음 할 일"(인수인계)이라면, worklog는 "그날 무엇을 왜 했는지"를 날짜별로 남기는 기록이다.

- **위치/이름**: `docs/worklog/YYYY-MM-DD.md`. 하루에 세션이 여러 개여도 한 파일에 모은다.
- **작성 시점**: 사용자가 요청할 때만 작성한다. 요청 없이 만들거나 커밋에 포함하지 않는다.
- **초안 만들기**: 전역 스킬 `daily-claude-code-recap`으로 그날의 세션을 훑어 초안을 만든 뒤, **parser-assess 관련 내용만** 추려서 적는다. 이 스킬은 모든 프로젝트의 세션 로그를 읽으므로 다른 프로젝트 내용이 섞이지 않게 걸러낸다.
- **구성**: `한 줄 요약` → `한 일`(변경·결과, 수치가 있으면 함께) → `결정과 이유` → `막힌 점 / 다음 할 일`. 한 일은 커밋 메시지와 겹치므로 짧게 쓰고, 결정과 이유를 가장 충실히 쓴다.
- **언어/공개**: 한국어. 공개 저장소이므로 개인 경로, 이메일, API 키, 사내 문서 내용은 적지 않는다. 스킬·환경 설정 같은 개인 작업 환경 이야기는 parser-assess 내용이 아니면 적지 않는다.
- **세션 id**: 해당 날짜의 세션 id를 파일 맨 아래 `참고 세션`에 `TODO.md`와 같은 형식으로 적을 수 있다.

## 개발 명령어

uv만 설치되어 있으면 된다. (이 환경에서는 conda의 `uv` 환경을 활성화: `conda activate uv`)

```powershell
uv sync                                  # .venv 생성과 의존성 설치 (pyproject.toml, uv.lock 기준)
uv run pytest                            # 테스트
uv sync --extra liteparse                # (선택) PDF 파서 LiteParse 설치
uv run parser-assess complexity <PDF|폴더>  # PDF 구조 복잡도를 단순한 순서로 출력 (LiteParse 필요)
uv tool install "parse-bench[liteparse]"   # 공식 평가 도구 parse-bench 설치 (프로젝트 밖 전역)
```

**선택 의존성**: 기본 `dependencies`는 비워 두고, 무거운 파서 라이브러리는 `[project.optional-dependencies]`로 분리한다. 라이브러리는 import 시점이 아니라 사용할 때 불러와, 미설치 시 설치 안내가 담긴 `ParserConfigError`로 실패하게 한다(`parser_assess/_liteparse.py` 참고).

## 파일 구조

```
parser-assess/
├── CLAUDE.md
├── README.md
├── pyproject.toml / uv.lock / .python-version
├── src/parser_assess/
│   ├── errors.py                # ParserConfigError
│   ├── _liteparse.py            # LiteParse 선택 의존성 로딩, 공용 엔진
│   ├── complexity.py            # PDF 구조 복잡도 점수 (가중치는 잠정값)
│   └── cli.py                   # parser-assess complexity
├── tests/
├── data/                        # 평가용 데이터와 결과 (git 제외)
└── .claude/
    ├── settings.json            # 프로젝트 설정 (공유)
    └── settings.local.json      # 개인 설정 (git 제외)
```

## 작업 시 주의사항

- **비밀 값 금지**: API 키, 토큰, 개인 경로는 커밋하지 않음. `.env`에 두고 `.env.example`만 커밋
- **대용량 산출물 제외**: 데이터셋, 벡터 DB, 모델 파일은 `.gitignore`에 추가
- **오래 걸리는 스크립트**: 장시간 실행되거나 LLM API를 호출하는 스크립트는 직접 실행하지 않고 실행 명령만 안내
- **확인 후 진행**: 큰 변경이나 되돌리기 어려운 작업(삭제, force push 등)은 먼저 확인
- **커밋**: 요청할 때만 수행. 메시지 형식은 `.claude/rules/commit.md`를 따른다
- **worktree 작업**: 파일을 수정하는 작업은 시작 전에 `EnterWorktree` 도구로 worktree를 만들고 그 안에서 진행한다. 작업이 끝나면 `main`에 병합한 뒤 worktree와 브랜치를 삭제한다. 읽기 전용 질문과 첫 커밋 전 초기 세팅은 예외
- **스킬 사용**: `.claude/skills/`에는 이 저장소 전용 스킬만 커밋한다. superpowers 같은 범용 스킬은 저장소에 포함하지 않으며, 필요하면 각자 전역(`~/.claude/skills/`)이나 로컬에 설치한다
