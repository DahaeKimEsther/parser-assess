# CLAUDE.md

이 파일은 Claude Code(claude.ai/code)가 이 저장소의 코드를 작업할 때 참고할 지침을 제공합니다.

## 언어 및 커뮤니케이션 규칙

- **기본 응답 언어**: 한국어
- **코드 주석**: 한국어로 작성
- **커밋 메시지**: 한국어로 작성
- **문서화**: 한국어로 작성
- **변수명/함수명**: 영어 (코드 표준 준수)

## 프로젝트 개요

**rag-lab** - RAG(Retrieval-Augmented Generation) 실험용 저장소. **public 저장소**이므로 공개되어도 되는 내용만 커밋합니다.

- **목표**: (한두 줄로 작성)
- **기술 스택**: (확정되면 작성)

## 개발 명령어

(환경 설정, 실행, 테스트 명령어를 확정되면 작성)

## 파일 구조

```
rag-lab/
├── CLAUDE.md            # 이 파일
└── .claude/
    ├── settings.json        # 프로젝트 설정 (공유)
    └── settings.local.json  # 개인 설정 (git 제외)
```

## 작업 시 주의사항

- **비밀 값 금지**: API 키, 토큰, 개인 경로는 커밋하지 않음. `.env`에 두고 `.env.example`만 커밋
- **대용량 산출물 제외**: 데이터셋, 벡터 DB, 모델 파일은 `.gitignore`에 추가
- **오래 걸리는 스크립트**: 장시간 실행되거나 LLM API를 호출하는 스크립트는 직접 실행하지 않고 실행 명령만 안내
- **확인 후 진행**: 큰 변경이나 되돌리기 어려운 작업(삭제, force push 등)은 먼저 확인
- **커밋**: 요청할 때만 수행
- **worktree 작업**: 파일을 수정하는 작업은 시작 전에 `using-git-worktrees` 스킬로 worktree를 만들고 그 안에서 진행한다. 읽기 전용 질문과 첫 커밋 전 초기 세팅은 예외
- **스킬 사용**: 작업 시작 전 `.claude/skills/using-superpowers` 스킬을 확인하고, 해당하는 스킬이 있으면 먼저 호출한다 (superpowers 스킬은 `.claude/skills/`에 직접 포함, 출처: obra/superpowers, MIT)

## gstack 로컬 설치 (선택, 저장소에는 포함하지 않음)

[garrytan/gstack](https://github.com/garrytan/gstack)은 용량이 크고(약 97MB, 5천여 파일) setup이 `.claude/skills/` 아래에 스킬 폴더 60여 개를 만들기 때문에 **저장소에 커밋하지 않고 각자 로컬에만 설치**합니다. 쓰지 않아도 이 저장소 작업에는 지장이 없습니다.

- **설치 요건**: Bun 1.4.2 이상, Node.js, Git. Windows에서는 Git Bash로 실행
- **설치 방법**
  1. gstack을 받아 `.claude/skills/gstack/`에 둔다 (`.git`은 제외)
  2. `.claude/skills/gstack`에서 `./setup --host claude` 실행
- **git에서 제외 (필수)**: setup이 `.claude/skills/` 아래에 만든 스킬 폴더(`autoplan/`, `qa/`, `review/` 등)가 커밋되지 않도록 각자 로컬 전용 파일 `.git/info/exclude`에 직접 추가한다. 이 저장소의 `.gitignore`에는 넣지 않는다. 커밋된 superpowers 스킬은 제외하면 안 된다
- **주의**
  - setup은 전역 설정 `~/.claude/settings.json`에 훅을 등록하므로 질문 내용을 읽고 선택한다
  - Windows에서는 심볼릭 링크 대신 파일 복사로 설치되므로 gstack을 갱신하면 `./setup`을 다시 실행한다
  - `/cso`는 Visual Studio 2022 Build Tools(C++)가 없으면 사용할 수 없다
