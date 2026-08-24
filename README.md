# create-slides

![version](https://img.shields.io/badge/version-0.3.0--wip-blue)
![Claude Code](https://img.shields.io/badge/Claude%20Code-supported-5A45FF)
![Codex](https://img.shields.io/badge/Codex-supported-10A37F)
![status](https://img.shields.io/badge/status-active%20development-brightgreen)

> Claude Code와 Codex가 채워진 콘텐츠 초안(교시별 표·본문·강사 멘트)을 읽고, 정보의 모양에 맞는 레이아웃과 시각 요소를 골라 **1280×720 HTML 발표 웹덱**을 만들도록 돕는 프레젠테이션 스킬입니다. 대상은 코딩 경험이 없는 입문자 중심의 혼합군 강의·교육 발표입니다.

---

## 목차

- [저장소 구조](#저장소-구조)
- [제작 파이프라인](#제작-파이프라인)
- [핵심 기능](#핵심-기능)
- [사용하기](#사용하기)
- [빠른 시작](#빠른-시작)
- [검증 · 도구](#검증--도구)
- [디자인 원칙](#디자인-원칙)
- [레이아웃 아틀라스](#레이아웃-아틀라스)
- [더 알아보기](#더-알아보기)

---

## 저장소 구조

이 저장소는 하나의 배포 대상 스킬(create-slides)과, 그 스킬을 만들고 운영하는 데 쓰는 개발 자산을 함께 담고 있습니다. 배포 대상과 개발 전용 자산은 명확히 분리되어 있습니다.

| 층 | 위치 | 배포 | 설명 |
|---|---|:---:|---|
| ① 포터블 스킬 | `SKILL.md` · `kit/` · `references/` · `scripts/` · `입력양식/` · `outputs/` | ✅ | 덱 조립 규칙의 정본. 다른 프로젝트에 그대로 복사해 쓸 수 있습니다. |
| ② 개발 자료 | `_dev/설계기록/` | ⛔ | 빌드·설계 결정 기록, 미채택 탐색안 아카이브. |
| ③ 플랫폼 어댑터 | `.claude/skills/` · `.agents/skills/` | — | Claude Code·Codex가 스킬을 찾는 얇은 진입점. 규칙을 복제하지 않고 정본을 로드만 합니다. |
| ④ 주차별 작업물 | `sessions/` | ⛔ | 강의 주차별 초안·덱·리서치 자료 산출물. |
| ⑤ 팀 워크플로 스킬 | `skills/` | ⛔ | 강의 제작 팀 역할을 스킬화한 리서치·콘텐츠·검토·하네스 정본. |

```text
lecture-deck-pipeline/
├── SKILL.md                    스킬 진입점 · 덱 조립 워크플로(포터블 스킬 정본)
├── AGENTS.md                   Codex 공통 작업 매뉴얼(정본, 저장소 구조·불변 규칙)
├── CLAUDE.md                   Claude Code 진입점(@AGENTS.md 로드 + 플랫폼 차이만)
├── README.md                   이 문서
│
├── kit/                        포터블 스킬 자원
│   ├── starter/                 덱 · 발표자노트 스타터 템플릿
│   ├── styles/                  디자인 토큰 · 컴포넌트 CSS(deck.css, patterns.css)
│   ├── layouts/                 레이아웃 카탈로그 50종 + by-shape.md 역인덱스
│   ├── charts/                  차트·다이어그램 요소 23종 + by-shape.md 역인덱스
│   ├── guide/                   정보모양 taxonomy · 디자인시스템 · 토큰 치트시트
│   ├── images/                  이미지 에셋 중앙 레지스트리
│   └── fonts/, screenshots/     폰트 서브셋 원본 · 주석 스크린샷 가이드
│
├── references/                 조립 리듬 · 이미지 디렉션 · 배포 규칙
├── 입력양식/                    콘텐츠 초안 템플릿(공식 입력 형식)
├── outputs/                     레이아웃 아틀라스 산출물
├── scripts/                     검증 · 조립 · 배포 도구 11종
├── evals/                       회귀 평가 시나리오(JSON) + 이미지 계약 검증기
├── tests/                       파이프라인·게이트 회귀 테스트(unittest 10모듈 219개 + fixtures 3종)
│
├── skills/                      팀 워크플로 스킬 정본: 리서치 · 콘텐츠 · 검토 · 하네스
├── sessions/                    주차별 산출물(N주차/N주차_초안.md(레거시 초안.md 폴백 인식) · 강의덱.html · 자료/)
├── _dev/설계기록/                빌드 · 설계 결정 기록(배포 제외)
│
├── .claude/skills/              Claude Code 어댑터(`/create-slides` 등 5종 + ui-ux-pro-max)
├── .agents/skills/              Codex 어댑터(`$create-slides` 등 5종 + ui-ux-pro-max)
│
├── 1주차_강의덱.html             1주차 실전 산출 예시(루트 CSS 상대경로 특례로 예외 유지)
└── 데모_제작규칙.html            마크업 예시 데모
```

---

## 제작 파이프라인

강의 한 주차는 5개 역할이 순서대로 이어받아 만듭니다. 아래 4단계는 스킬로 옮겨져 있고, 스토리라인만 사람이 직접 작성합니다.

```mermaid
flowchart LR
    A["📋 커리큘럼 문서\ncourses/<과목>/sessions/N주차_강의안설계.md"] --> B["🔍 /리서치\n콘텐츠 리서치 · 실습 검증"]
    B -->|"자료/*.md"| C["✍️ /콘텐츠\n슬라이드 문장 집필"]
    C -->|"N주차_초안.md"| D["🎨 /create-slides\nHTML 웹덱 조립"]
    D -->|"강의덱.html"| E["✅ /검토\n읽기 전용 감사"]
```

| 스킬 | 담당 | 산출물 | 호출 |
|---|---|---|---|
| `/리서치` | 콘텐츠 리서치 · 실습 검증 | `courses/<과목>/sessions/N주차/자료/` 3~5파일 | 명시 호출 전용 |
| `/콘텐츠` | 슬라이드 문장 · 비유 · 멘트 집필 | `courses/<과목>/sessions/N주차/N주차_초안.md` | 명시 호출 전용 |
| `/create-slides` | HTML 웹덱 · 발표자노트 조립 | `강의덱.html` + `_발표자노트.html` | **자동 발동** |
| `/검토` | 전 단계 횡단 읽기 전용 감사 | `검토보고_YYYY-MM-DD.md` | 명시 호출 전용 |

`/create-slides`만 자연어 요청으로 자동 호출되고, 나머지 3개 팀 스킬은 이름을 직접 지목했을 때만 발동합니다. 계약·스키마 정본은 [`skills/README.md`](skills/README.md)를 참고하세요.

**`/하네스`**는 위 파이프라인의 한 단계가 아니라, 다파일·대규모 작업일 때 어떤 단계에서든 적용하는 **작업 수행 방식**(메인 게이트 + 워커 편집 분담)입니다. 정본은 [`skills/하네스/SKILL.md`](skills/하네스/SKILL.md).

---

## 핵심 기능

- 초안의 슬라이드 순서·제목·본문을 그대로 존중합니다(재작성하지 않음). 수용량을 넘겨도 승인 없이 슬라이드를 나누지 않습니다.
- `시각화 의도`를 사람이 지정하지 않아도, 12개 정보 모양을 스킬이 직접 판단한 뒤 레이아웃 50종과 차트·다이어그램 요소 23종을 조합합니다.
- 강사 멘트를 아이콘으로 라우팅합니다 — `💬` 농담·`👀` 시연 큐는 화면에 감추고, `🗣` 안전망 예시는 접힌 힌트로 넣습니다. 멘트가 있으면 강사용 **발표자 노트 HTML**도 함께 만듭니다.
- 큰 글자와 높은 대비를 기본으로 하며, 입문자 중심 혼합군 대상의 강의·교육 발표에 맞춥니다.
- 표지의 3단 큐브, 메인 블루 색 체계, 민트 강조 규칙, 파트 진행 표시와 페이지 번호를 유지합니다.
- 방향키 발표, 전체화면, 홈·페이지 이동·슬라이드 목록·PDF 출력을 제공하는 Liquid Glass 발표 내비게이션을 포함합니다.
- 외부 이미지보다 코드 기반 차트·다이어그램을 우선하고, 필요한 화면 조작은 주석 스크린샷으로 안내합니다.

---

## 사용하기

### Claude Code

이 개발 저장소에서는 `.claude/skills/create-slides/SKILL.md` 어댑터가 루트 공통 정본을 로드하므로 바로 사용할 수 있습니다. 다른 프로젝트에 배포할 때는 루트 포터블 Skill 파일을 아래 위치에 복사합니다.

```text
<프로젝트>/.claude/skills/create-slides/
```

새 Claude Code 세션에서 `/create-slides`로 호출하거나, "이 초안으로 강의덱 만들어줘", "PPT를 HTML 웹덱으로 만들어줘"처럼 요청하면 스킬이 적용됩니다.

### Codex

이 개발 저장소에서는 `.agents/skills/create-slides/SKILL.md` 어댑터가 루트 공통 정본을 로드하므로 바로 사용할 수 있습니다. 다른 프로젝트에 포터블 스킬로 설치할 때는 배포 대상 파일을 아래 위치에 둡니다.

```text
<프로젝트>/.agents/skills/create-slides/
```

새 Codex 작업에서 `$create-slides`를 명시하거나 "이 초안으로 강의덱 만들어줘"처럼 요청합니다. 이 개발 저장소의 `.agents/`는 프로젝트 설정 레이어이므로 포터블 스킬 안에 중첩해 복사하지 않습니다.

자세한 워크플로와 불변 요소는 [`SKILL.md`](SKILL.md)를, 작성 형식은 [콘텐츠 초안 템플릿](입력양식/콘텐츠초안템플릿.md)을 참고하세요.

---

## 빠른 시작

1. [`입력양식/콘텐츠초안템플릿.md`](입력양식/콘텐츠초안템플릿.md) 형식으로 슬라이드 내용을 채웁니다(교시별 표 + 강사 멘트 아이콘).
2. Claude Code 또는 Codex에서 초안과 함께 덱 제작을 요청합니다. 스킬이 교시→PART 묶음을 확인한 뒤 조립합니다.
3. 생성된 HTML 덱(+ 멘트가 있으면 발표자 노트 HTML)을 아래 명령으로 검증합니다.

```powershell
python scripts/verify_deck.py <덱 파일>.html --parts <파트 수>
python scripts/verify_skill_setup.py
```

### 개발환경 설정(이 저장소에 기여할 때)

폰트 서브셋 임베드에 `fontTools`·`Pillow`가 필요합니다. 의존 정본은 [`requirements-dev.txt`](requirements-dev.txt)이며, Windows 로컬에서는 보통 `.venv\Scripts\python.exe`로 설치·실행합니다.

```powershell
python -m unittest tests.test_deck_pipeline tests.test_image_pipeline tests.test_quality_gates tests.test_deck_contract tests.test_declared_vs_enforced tests.test_rule_pointers tests.test_typography_rules tests.test_analyze_agent_usage tests.test_audit_context_budget tests.test_hook_guards tests.test_course_paths tests.test_theme_contract
```

10개 모듈 219개 테스트가 전부 돕니다(2026-08-18 실측 `Ran 219 tests … OK`). `tests/`에 `__init__.py`가 없어 `unittest discover`는 동작하지 않으므로 모듈을 명시합니다.

---

## 검증 · 도구

`scripts/`의 11개 도구가 정적 검증·조립·배포를 담당합니다.

| 스크립트 | 역할 |
|---|---|
| `verify_deck.py` | 덱 정적 검증 — 파트수·구도 다양성·같은 구도 연속·색 토큰·아이콘 마커 누출 |
| `verify_skill_setup.py` | Claude/Codex 스킬 어댑터 정합 검증(정본·어댑터 frontmatter 일치, 규칙 복제 금지) |
| `verify_session_docs.py` | 주차 산출물 스키마 검증(리서치 8항목 등) |
| `verify_research_chunks.py` | 개념KB 청크 최소 깊이 검증 |
| `verify_image_assets.py` | 이미지 에셋 계약 검증(PNG·RGBA·투명 여백) |
| `verify_distributable.py` | 배포본 자립성 검증(외부 의존 0) |
| `assemble_deck.py` | 조각(shell + part-NN)을 강의덱.html로 조립 |
| `build_release.py` | 조립 → 검증 → 인라인 → 배포본 검증 전체 파이프라인 실행 |
| `inline_deck.py` | 외부 CSS·JS·이미지를 단일 HTML로 인라인 |
| `font_embed.py` | Pretendard 글리프 서브셋 추출 후 base64 임베드 |
| `prepare_image_asset.py` | 크로마키 이미지 에셋 전처리(알파 복구) |

검증 원칙: 브라우저는 `deck.css`를 캐시하므로 변경 확인 때 `href`에 `?v=`를 붙이고, `file://`가 아닌 로컬 HTTP 서버(`python -m http.server`)로 확인합니다. 스크린샷보다 `scrollHeight`·computed style 등 JS 측정을 우선합니다.

---

## 디자인 원칙

- 구조와 주 강조에는 `--blue`를 사용합니다.
- 민트는 행동·안전·강조에 사용하며, 글자색·밑줄·글자폭 배경·도형 중 문맥에 맞춰 선택합니다.
- 상단 헤더 선은 메인 블루를 사용합니다.
- 그라데이션과 `navy` 렌더 사용을 금지합니다.
- 하단 기본 바는 고투명 유리, 상세 메뉴는 옅은 쿨그레이 반투명 유리로 구성합니다.

---

## 레이아웃 아틀라스

[`outputs/create-slides-layout-atlas.html`](outputs/create-slides-layout-atlas.html)에서 레이아웃 50종과 현재 아틀라스에 수록된 시각 요소를 실제 발표 화면처럼 넘겨볼 수 있습니다. 전체 23종 element의 정본은 `kit/charts/`입니다.

---

## 더 알아보기

| 문서 | 다루는 내용 |
|---|---|
| [`AGENTS.md`](AGENTS.md) | 저장소 구조 전체 · 불변 규칙 · 작업 방식(정본) |
| [`SKILL.md`](SKILL.md) | 덱 조립 워크플로 · 판단 기준(정본) |
| [`skills/README.md`](skills/README.md) | 팀 워크플로 스킬 계약표 · 파이프라인 지도 · 명시 호출 규약 |
| [`skills/하네스/SKILL.md`](skills/하네스/SKILL.md) | 다파일·대규모 작업 오케스트레이션 프로토콜 |
| [`sessions/README.md`](sessions/README.md) | 주차별 산출물 폴더 규약 |
| [`.agents/agent-memory/create-slides/MEMORY.md`](.agents/agent-memory/create-slides/MEMORY.md) | 누적 규칙 · 색 시스템 정본 · 현재 상태(`## 미해결`) |
