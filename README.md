# rag-lab

사내 문서 검색 RAG를 위한 문서 처리 모듈입니다. 문서를 유형별로 알맞은 파서로 처리해 `.md` 파일로 내보내고, 처리 시간을 기록해 계속 줄여 가는 것이 목표입니다.

## 준비

[uv](https://docs.astral.sh/uv/)만 설치되어 있으면 됩니다. 파이썬과 라이브러리는 `pyproject.toml`과 `uv.lock`에 맞춰 uv가 설치합니다.

1. uv가 설치된 환경을 활성화합니다. (예: conda의 `uv` 환경)

   ```powershell
   conda activate uv
   ```

2. 프로젝트 폴더에서 `uv sync`를 실행합니다. `.venv`가 만들어지고 라이브러리가 설치됩니다. `.venv`는 git에 포함하지 않으므로 필요할 때 다시 만들면 됩니다.

   ```powershell
   uv sync
   ```

## 실행

문서 폴더를 처리하고 결과를 `.cache/parsed/`에 `.md`로 저장합니다. 처리 시간은 `.cache/parser/metrics.jsonl`에 쌓입니다.

```powershell
uv run rag-lab-parser run <문서 폴더>
```

쌓인 처리 시간을 유형/파서별로 요약해서 봅니다.

```powershell
uv run rag-lab-parser stats
```

## 테스트

```powershell
uv run pytest
```

## 구성

문서 유형별로 어떤 파서를 쓸지는 `config/parser_routing.toml`에서 정합니다. 새 파서나 출력 방식은 `src/rag_lab/parser/parsers/`, `src/rag_lab/parser/writers/`에 파일을 추가하고 `@register_parser`, `@register_writer`로 등록한 뒤 설정에 이름을 적으면 됩니다.
