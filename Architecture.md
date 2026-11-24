# Architecture

rag-lab의 현재 구조를 설명한다. 크게 두 부분이다.

- **처리 파이프라인**: 문서를 `.md`로 바꾸고 처리 시간을 잰다. 만들어 뒀지만 아직 실제 문서에 쓰지 않는다.
- **assessment(평가)**: LiteParse가 어떤 PDF까지 쓸 만한지 재는 실험이다. 지금 작업 중이다.

## 폴더 구조

```
rag-lab/
├── config/
│   └── parser_routing.toml      유형(확장자) → 파서, 출력 방식/폴더 설정
├── src/rag_lab/
│   ├── parser/                  [처리 파이프라인]
│   │   ├── models.py            ParsedDocument, ProcessingRecord
│   │   ├── base.py              파서/writer 인터페이스
│   │   ├── registry.py          이름으로 파서/writer 찾기
│   │   ├── detect.py            확장자로 유형 판별
│   │   ├── router.py            설정(TOML) 읽기, 유형별 파서 선택
│   │   ├── pipeline.py          판별 → 파싱 → 출력 흐름
│   │   ├── metrics.py           시간 측정, 기록(JSONL), 요약
│   │   ├── errors.py            설정 오류
│   │   ├── cli.py               run / stats / complexity 명령
│   │   ├── parsers/             markdown, text, liteparse(PDF)
│   │   ├── writers/             markdown
│   │   ├── _liteparse.py        [assessment 겸용] LiteParse 불러오기, 공용 엔진
│   │   └── complexity.py        [assessment] PDF 복잡도 점수
│   └── assess/                  [assessment] 아직 없음(계획)
├── tests/
├── docs/worklog/                날짜별 작업 기록
├── TODO.md                      현재 상태와 다음 할 일
├── .cache/                      출력물, 처리 시간 기록 (git 제외)
└── data/                        평가용 데이터와 결과 (git 제외)
```

- `[assessment]` 표시는 처리 파이프라인이 아니라 평가를 위해 있는 파일이다.[^1]
- 청킹, 임베딩, 검색 같은 단계는 필요해질 때 `src/rag_lab/` 아래에 폴더를 추가한다.

---

# 1. 처리 파이프라인 (기본 파이프라인만 구축하고 미사용 중)

문서 폴더를 받아 파일마다 유형을 판별하고 알맞은 파서로 읽어 `.md`로 저장하며, 걸린 시간을 기록한다.

## 처리 흐름

```
문서 폴더
  └─ 파일마다 pipeline.py의 process를 거침 (아래 단계를 진행)
       1. detect_type      확장자로 유형 판별            (detect.py)
       2. router.select    유형 → 파서 선택              (router.py, 설정은 parser_routing.toml)
       3. parser.parse     파일 → ParsedDocument         (parsers/, 2.번에서 고른 parser 사용)
       4. writer.write     ParsedDocument → .md 파일     (writers/)
       5. 시간 측정        ProcessingRecord 생성         (metrics.py)
  └─ 기록을 JSONL에 덧붙임 → `stats`로 요약              (metrics.py)
```
- 3~4단계의 시간만 잰다.[^2]
- 파일 하나가 실패해도 `failed`로 기록하고 다음 파일로 넘어간다.
- 매핑이 없는 유형은 `skipped`로 기록한다.

## 핵심 개념

- **파서**: 파일 하나를 읽어 `ParsedDocument`를 돌려준다. 실패하면 예외를 던진다.
- **writer**: `ParsedDocument`를 출력 폴더에 저장한다. 문서 id(폴더 기준 상대 경로)가 곧 출력 경로다.
- **라우터**: `[routes]`(확장자 → 파서 이름)를 보고 파서를 고른다. 시작할 때 현재 존재하는 파서의 이름을 전부 확인하므로 오타는 처리 전에 드러난다.
- **등록 장치**: 이름과 클래스를 이어 준다. 그래서 설정 파일에는 이름만 적는다.

## 현재 지원 유형

| 유형 | 파서 | 비고 |
|---|---|---|
| `md` | `markdown` | 내용을 그대로 사용 |
| `txt` | `text` | 내용을 그대로 사용 |
| `pdf` | `liteparse` | 선택 설치. 설정 파일에는 아직 연결돼 있지 않다.[^3] |

## 출력과 저장 위치

`.cache/parsed/<문서 id>.md`로 저장하고, 맨 위에 front matter를 붙인다.

```
---
title: "문서 이름"
source: "하위폴더/문서.pdf"
doc_type: "pdf"
parser: "liteparse"
empty: true        # 본문이 비었을 때만
---
```

처리 기록은 `.cache/parser/metrics.jsonl`에 `run`할 때마다 덧붙는다.

## 확장 방법

새 파서나 writer는 기존 코드를 고치지 않고 추가한다.

1. `parsers/`(또는 `writers/`)에 파일을 만들고 클래스에 `@register_parser("이름")`을 붙인다.
2. 해당 패키지의 `__init__.py`에서 import한다.
3. `config/parser_routing.toml`에 이름을 적는다.

---

# 2. assessment (작업 중)

LiteParse가 **어떤 구조 요소(표, 다단, 스캔 등)까지 쓸 만한지**를, 쉬운 문서부터 어려운 문서 순서로 확인한다.

## 평가 흐름

```
ParseBench-2 문서 (공개 평가용 PDF 모음, 정답 포함)
  ├─ ① 우리 복잡도 점수로 쉬운 순서 정렬     complexity.py          [구현됨]
  ├─ ② LiteParse 공식 점수 계산              parse-bench 도구        [설치됨, 실행 확인 중]
  └─ ③ ①과 ②를 한 표로 합쳐 출력             assess/cli.py           [미구현]
```

- 채점은 공식 도구(`parse-bench`)가 한다. 자체 채점기는 만들지 않는다.
- 복잡도 점수식(스캔 0.40, 다단 0.25, 표 0.20, 그림 0.15)은 잠정값이며, 결과를 본 뒤 보정한다.

## 진행 상태

| 구성 요소 | 위치 | 상태 |
|---|---|---|
| PDF 복잡도 점수 | `parser/complexity.py` | 구현됨 |
| 복잡도 명령 | `rag-lab-parser complexity <PDF\|폴더>` | 구현됨 |
| LiteParse 공용 엔진 | `parser/_liteparse.py` | 구현됨 |
| 공식 평가 도구 | `parse-bench` (프로젝트 밖 전역 설치) | 설치됨, ParseBench-2 `--test` 실행이 남음 |
| 점수 결합 도구 | `assess/` (`rag-lab-assess`) | 미구현 |

## 의존성 방향

```
assess → parser (가져다 쓰기만 한다)
parser → assess (모른다)
```

---

[^1]: `complexity.py`는 나중에 라우터가 재사용할 계획이라 지금 `parser/`에 있다. 평가 쪽으로 옮길지는 정하지 않았다.
[^2]: 유형 판별과 파일 크기 확인은 시간에 넣지 않는다. 측정 대상은 "파서가 파일을 읽어 변환하고 저장하는 시간"이다.
[^3]: PDF를 `run`으로 처리하려면 `config/parser_routing.toml`의 `[routes]`에 `pdf = "liteparse"`를 추가해야 한다. 지금은 `complexity` 명령에서만 LiteParse를 쓴다.
