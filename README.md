# parser-assess

파서가 벤치마크에서 어느 문서까지 쓸 만한지 판단하는 평가 도구입니다. 지금은 LiteParse(PDF 파서)를 평가합니다.

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

3. PDF 파서(LiteParse)는 필요할 때만 설치하는 선택 의존성입니다. 기본 `uv sync`에는 포함되지 않습니다.

   ```powershell
   uv sync --extra liteparse
   ```

## 실행

PDF(또는 PDF 폴더)가 얼마나 복잡한지 단순한 문서부터 순서대로 보여 줍니다. 스캔, 다단, 표, 그림이 있는 페이지 수를 세어 0~1 점수로 만든 것이며, 점수식은 아직 잠정값입니다.

```powershell
uv run parser-assess complexity <PDF 또는 폴더>
```

- **한계**: OCR은 꺼져 있어서 스캔 PDF는 본문이 비어 나옵니다. 글자가 아주 적은 페이지도 스캔으로 집계될 수 있습니다.

## 테스트

```powershell
uv run pytest
```

LiteParse가 설치되어 있지 않으면 실제 PDF를 쓰는 테스트는 건너뜁니다.
