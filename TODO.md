# TODO

작업을 시작하기 전에 읽고, 끝낸 항목은 체크하며 갱신한다. (공개 저장소이므로 개인 경로/이메일/사내 문서 내용은 적지 않는다.)

## 참고 세션

- 1단계(LiteParse 파서, 복잡도, `complexity` CLI)를 만든 Claude Code 세션 id: `53bf1886-0917-4f3f-8871-043b79bcad83`
- 설계 결정의 배경(OCR을 끈 이유, 평면 `assess/` 구조, ParseBench 조사 내용 등)은 이 세션 대화에 있다. 대화 기록은 로컬의 Claude Code 프로젝트 세션 폴더에서 이 id의 `.jsonl` 파일로 찾을 수 있고, 이어서 열려면 `claude --resume 53bf1886-0917-4f3f-8871-043b79bcad83`을 쓴다.

## 현재 상태

- 1단계 완료: LiteParse PDF 파서(`parsers/liteparse.py`), PDF 구조 복잡도(`complexity.py`), `rag-lab-parser complexity <PDF|폴더>`
- 선택 의존성이라 `uv sync --extra liteparse`로 설치해야 한다. 미설치여도 나머지 테스트는 통과하고 실제 PDF 테스트만 건너뛴다.
- 지금까지 확인한 샘플은 직접 만든 PDF 4건(단순 영어/한국어, 2단+표, 스캔)뿐이다. **실제 사내 문서로는 아직 검증하지 않았다.**

## 다음 목표

LiteParse가 **어떤 구조 요소까지 쓸 만한지** 테스트하는 파이프라인을 만든다.

- [ ] 구조 요소별 샘플 PDF 확충: 표(격자/무격자), 다단, 헤딩 계층, 목록, 그림/차트, 스캔, 한국어, 긴 문서
- [ ] 샘플 생성 스크립트를 `scripts/`로 보존(reportlab/pillow는 `uv run --no-project --with reportlab --with pillow`로 일회성 사용). 샘플 PDF 자체는 `data/`에 둔다(git 제외)
- [ ] `src/rag_lab/assess/` 설계와 구현(평면 구조: cases, scoring, report, cli)
- [ ] 요소별 추출 품질 측정 후 "쓸 수 있는 범위"의 경계 도출
- [ ] 복잡도 점수식을 측정 결과로 보정(`complexity.py` 상단의 가중치/임계값)
- [ ] (선택) ParseBench-2 연동: 데이터셋 `llamaindex/ParseBench-2`, 도구 `parse-bench`의 `liteparse_markdown` 파이프라인. 한국어 문서는 없는 것으로 확인했고 v2 리더보드에 LiteParse는 없다

## 알아둘 사실

- OCR은 꺼져 있다(`ocr_enabled=False`). 스캔 PDF는 본문이 비고 출력 front matter에 `empty: true`가 붙는다.
- LiteParse는 글자가 아주 적은 페이지를 `sparse-text`로 보고 `needs_ocr=True`를 준다. 그래서 짧은 정상 페이지도 스캔으로 집계된다.
- 복잡도 점수식(스캔 0.40, 다단 0.25, 표 0.20, 그림 0.15)과 등급 임계값(0.15, 0.40)은 **잠정값**이다.
- LiteParse 예외: 없는 파일은 `FileNotFoundError`, 깨진 PDF는 `liteparse.types.ParseError`, PDF가 아닌 파일은 예외 없이 빈 결과가 나온다.
- 첫 LiteParse 호출은 초기화로 약 1.4초 걸리고 이후는 수십 ms다. `quiet=True`를 주지 않으면 단계별 시간 로그가 출력된다.
- 구조 결정: `assess/`는 `parser/`를 import만 하고 `parser/`는 `assess/`를 모른다. 두 번째 평가 대상이 생기면 `assess/parser/`로 나눈다. `complexity.py`는 라우터가 재사용할 것이므로 `parser/`에 둔다.

## 열린 질문

- 사내 문서가 PDF 위주인가, hwp/Word도 섞여 있는가(LiteParse는 hwp 미지원)
- 검색에 표/헤딩 구조가 얼마나 중요한가, 즉 "쓸 만함"의 기준을 무엇으로 볼 것인가
- 저장소 이름

## 이후 단계

- [ ] 복잡도 기준을 라우터에 연결(유형 + 복잡도로 파서 선택)
- [ ] OCR 파서 추가(한국어 traineddata 동작 확인 필요)
- [ ] OKF writer 추가(필요해질 때)
