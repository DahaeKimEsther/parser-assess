# CLAUDE.md

이 파일은 Claude Code(claude.ai/code)가 이 저장소의 코드를 작업할 때 참고할 지침을 제공합니다.

## 언어 및 커뮤니케이션 규칙

- **기본 응답 언어**: 한국어
- **코드 주석**: 한국어로 작성
- **커밋 메시지**: 한국어로 작성
- **문서화**: 한국어로 작성
- **변수명/함수명**: 영어 (코드 표준 준수)

## 프로젝트 개요

**rag-lab** - 사내 문서 검색 RAG(Retrieval-Augmented Generation)를 위한 문서 처리 모듈 저장소. **public 저장소**이므로 공개되어도 되는 내용만 커밋합니다.

- **목표**: 문서를 유형별로 알맞은 파서로 처리해 `.md` 파일로 내보내고, 처리 시간을 계속 측정해 줄여 간다. 청킹, 임베딩, 검색 같은 단계는 필요해질 때 `src/rag_lab/` 아래에 폴더를 추가하며 확장한다.
- **기술 스택**: Python 3.12+, uv(`pyproject.toml` + `uv.lock`), 런타임 의존성 없음(표준 라이브러리만), 테스트는 pytest

## 작업 시작 전

- **`TODO.md`를 먼저 읽는다.** 현재 상태, 다음 작업 체크리스트, 알아둘 사실, 열린 질문이 들어 있다. 작성과 갱신은 **사용자가 요청할 때만** 한다. (`.claude/plans/`는 git 제외라 worktree에서 읽을 수 없으므로 인수인계는 `TODO.md`로 한다.)

### TODO.md 작성 규칙

- **언어/공개**: 한국어. 공개 저장소이므로 개인 경로, 이메일, 사내 문서 내용은 적지 않는다.
- **섹션 순서**: `참고 세션` → `현재 상태` → `다음 목표` → `알아둘 사실` → `열린 질문` → `이후 단계`. 새 섹션이 필요하면 `알아둘 사실` 앞에 추가한다.
- **체크리스트**: 할 일은 `- [ ]`, 끝낸 일은 `- [x]`로 바꾼다. 한 항목은 한 줄로, 무엇을 하는지가 드러나게 쓴다. 끝난 항목이 쌓이면 `현재 상태`에 요약하고 지운다.
- **알아둘 사실**: 코드나 git 기록에서 알 수 없는 것만 적는다. 실측해서 확인한 것과 잠정값/미검증을 구분해서 쓴다.
- **세션 id**: 사용자가 `TODO.md` 작성/갱신을 요청했을 때 **현재 세션 id를 `참고 세션`에 한 줄 추가**한다. 형식은 ``- `<세션 id>`: 한 줄 설명(무엇을 한 세션인지)``이며 최신 세션이 위에 온다. 세션 id는 대화 기록 파일(`~/.claude/projects/<프로젝트>/<세션 id>.jsonl`)의 파일 이름이고, 이어서 열 때는 `claude --resume <세션 id>`를 쓴다.
- **갱신 시점**: 사용자가 요청할 때만 작성/갱신한다. 작업을 끝냈다고 해서 요청 없이 `TODO.md`를 고치거나 커밋에 포함하지 않는다.

## 개발 명령어

uv만 설치되어 있으면 된다. (이 환경에서는 conda의 `uv` 환경을 활성화: `conda activate uv`)

```powershell
uv sync                                  # .venv 생성과 의존성 설치 (pyproject.toml, uv.lock 기준)
uv run pytest                            # 테스트
uv run rag-lab-parser run <문서 폴더>      # 문서 처리 + 처리 시간 기록 (출력: .cache/parsed/)
uv run rag-lab-parser stats              # 쌓인 처리 시간을 유형/파서별로 요약
uv sync --extra liteparse                # (선택) PDF 파서 LiteParse 설치
uv run rag-lab-parser complexity <PDF|폴더>  # PDF 구조 복잡도를 단순한 순서로 출력 (LiteParse 필요)
```

**선택 의존성**: 기본 `dependencies`는 비워 두고, 무거운 파서 라이브러리는 `[project.optional-dependencies]`로 분리한다. 파서 모듈은 라이브러리를 import 시점이 아니라 `__init__`에서 불러와, 미설치 시 설치 안내가 담긴 `ParserConfigError`로 실패하게 한다(`parser/_liteparse.py` 참고).

**새 파서/출력 방식 추가**: `src/rag_lab/parser/parsers/`(또는 `writers/`)에 파일을 만들고 클래스에 `@register_parser("이름")`(또는 `@register_writer`)을 붙인 뒤, 해당 패키지의 `__init__.py`에서 import하고 `config/parser_routing.toml`에 이름을 적는다. 라우터/측정 코드는 수정하지 않는다.

## 파일 구조

```
rag-lab/
├── CLAUDE.md
├── README.md
├── pyproject.toml / uv.lock / .python-version
├── config/
│   └── parser_routing.toml      # 유형(확장자) → 파서, 출력 방식/폴더
├── src/rag_lab/parser/
│   ├── models.py                # ParsedDocument, ProcessingRecord
│   ├── base.py                  # 파서/writer 인터페이스
│   ├── registry.py              # @register_parser, @register_writer
│   ├── detect.py                # 문서 유형 판별(확장자)
│   ├── router.py                # 라우팅 설정(TOML) 로드, 유형별 파서 선택
│   ├── pipeline.py              # 유형 판별 → 파싱 → 출력, 시간 측정
│   ├── metrics.py               # 시간 측정, 기록(JSONL), 요약
│   ├── complexity.py            # PDF 구조 복잡도 점수 (가중치는 잠정값)
│   ├── _liteparse.py            # LiteParse 선택 의존성 로딩, 공용 엔진
│   ├── cli.py                   # rag-lab-parser run / stats / complexity
│   ├── parsers/                 # markdown, text, liteparse(PDF)
│   └── writers/                 # markdown (OKF 등은 필요할 때 추가)
├── tests/
├── .cache/                      # 출력물과 처리 시간 기록 (git 제외)
└── .claude/
    ├── settings.json            # 프로젝트 설정 (공유)
    └── settings.local.json      # 개인 설정 (git 제외)
```

## 작업 시 주의사항

- **비밀 값 금지**: API 키, 토큰, 개인 경로는 커밋하지 않음. `.env`에 두고 `.env.example`만 커밋
- **대용량 산출물 제외**: 데이터셋, 벡터 DB, 모델 파일은 `.gitignore`에 추가
- **오래 걸리는 스크립트**: 장시간 실행되거나 LLM API를 호출하는 스크립트는 직접 실행하지 않고 실행 명령만 안내
- **확인 후 진행**: 큰 변경이나 되돌리기 어려운 작업(삭제, force push 등)은 먼저 확인
- **커밋**: 요청할 때만 수행
- **worktree 작업**: 파일을 수정하는 작업은 시작 전에 `EnterWorktree` 도구로 worktree를 만들고 그 안에서 진행한다. 작업이 끝나면 `main`에 병합한 뒤 worktree와 브랜치를 삭제한다. 읽기 전용 질문과 첫 커밋 전 초기 세팅은 예외
- **스킬 사용**: `.claude/skills/`에는 이 저장소 전용 스킬만 커밋한다. superpowers 같은 범용 스킬은 저장소에 포함하지 않으며, 필요하면 각자 전역(`~/.claude/skills/`)이나 로컬에 설치한다

## gstack 전역 설치 (선택, 저장소에는 포함하지 않음)

[garrytan/gstack](https://github.com/garrytan/gstack)은 용량이 크고(약 97MB, 5천여 파일) 범용 도구이므로 **이 저장소가 아니라 각자 전역(`~/.claude/skills/gstack`)에 설치**합니다. 저장소 안(`.claude/skills/`)에는 설치하지 않으며, 쓰지 않아도 이 저장소 작업에는 지장이 없습니다.

- **설치 요건**: Bun 1.4.2 이상, Node.js, Git. Windows에서는 Git Bash로 실행
- **설치 방법** (저장소 밖에서 실행)
  1. `git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack`
  2. `cd ~/.claude/skills/gstack && ./setup --host claude`
- **주의**
  - 전역에 설치하므로 `.gitignore`나 `.git/info/exclude` 설정은 필요 없다
  - setup은 전역 설정 `~/.claude/settings.json`에 훅을 등록하므로 질문 내용을 읽고 선택한다
  - Windows에서는 심볼릭 링크 대신 파일 복사로 설치되므로 gstack을 갱신하면 `./setup`을 다시 실행한다
  - `/cso`는 Visual Studio 2022 Build Tools(C++)가 없으면 사용할 수 없다
