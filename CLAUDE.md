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
