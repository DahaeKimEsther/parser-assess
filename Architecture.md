# Architecture

parser-assess는 **파서가 벤치마크에서 어느 문서까지 쓸 만한지** 판단하는 평가 도구다. 지금은 LiteParse를 평가한다.

## 폴더 구조

```
parser-assess/
├── src/parser_assess/
│   ├── errors.py            설정 오류(ParserConfigError)
│   ├── _liteparse.py        LiteParse 불러오기, 공용 엔진
│   ├── complexity.py        PDF 복잡도 점수
│   └── cli.py               complexity 명령 (점수 결합 명령이 들어올 자리)
├── tests/
│   ├── conftest.py          make_pdf fixture
│   ├── test_complexity.py
│   └── test_cli_complexity.py
├── docs/worklog/            날짜별 작업 기록
├── TODO.md                  현재 상태와 다음 할 일
└── data/                    평가용 데이터와 결과 (git 제외)
```

## 평가 흐름

```
ParseBench-2 문서 (공개 평가용 PDF 모음, 정답 포함)
  ├─ ① 우리 복잡도 점수로 쉬운 순서 정렬     complexity.py          [구현됨]
  ├─ ② LiteParse 공식 점수 계산              parse-bench 도구        [설치됨, 실행 확인 중]
  └─ ③ ①과 ②를 한 표로 합쳐 출력             cli.py                  [미구현]
```

- 채점은 공식 도구(`parse-bench`)가 한다. 자체 채점기는 만들지 않는다.
- 복잡도 점수식(스캔 0.40, 다단 0.25, 표 0.20, 그림 0.15)은 잠정값이며, 결과를 본 뒤 보정한다.

## 진행 상태

| 구성 요소 | 위치 | 상태 |
|---|---|---|
| PDF 복잡도 점수 | `complexity.py` | 구현됨 |
| 복잡도 명령 | `parser-assess complexity <PDF\|폴더>` | 구현됨 |
| LiteParse 공용 엔진 | `_liteparse.py` | 구현됨 |
| 공식 평가 도구 | `parse-bench` (프로젝트 밖 전역 설치) | 설치됨, ParseBench-2 `--test` 실행이 남음 |
| 점수 결합 명령 | `cli.py` | 미구현 |

## 이전 구조

문서를 `.md`로 바꾸고 처리 시간을 재던 처리 파이프라인(라우터, 레지스트리, writer 등)은 제거했다.[^1]

---

[^1]: 이전 구현은 git 이력(`618f748` 이전 커밋)에서 되살릴 수 있다. 제거 이유는 `docs/decisions.md`를 본다.
