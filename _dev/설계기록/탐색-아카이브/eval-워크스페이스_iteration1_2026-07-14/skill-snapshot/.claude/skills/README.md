# .claude/skills — 프로젝트 스킬 관리소

이 폴더는 **이 프로젝트에서 쓰는 커스텀 스킬을 추가·보관·관리**하는 곳이다.
Claude Code는 여기 있는 `<스킬이름>/SKILL.md`를 **자동으로 발견**한다 — 별도 설정(settings.json) 불필요.

> ⚠️ `.claude/`는 **개발용 설정(레이어 ③)**이라 포터블 스킬 배포물에 포함되지 않는다.
> 여기 둔 스킬은 "이 프로젝트를 열었을 때만" 켜지는 로컬 스킬이다.

---

## 1. 스킬은 어디서 발견되나 (우선순위)

| 위치 | 범위 | 비고 |
|---|---|---|
| `~/.claude/skills/<이름>/SKILL.md` | 개인(모든 프로젝트) | 내 계정 전역 |
| **`.claude/skills/<이름>/SKILL.md`** ← 여기 | **이 프로젝트** | 팀·레포와 공유 가능 |
| 플러그인/마켓플레이스 | 설치한 플러그인 | `design:*`, `engineering:*` 등 |

같은 이름이면 대개 더 좁은 범위(프로젝트)가 우선한다. 이름 충돌을 피하려면 고유한 kebab-case 이름을 쓴다.

---

## 2. 이 폴더 구조

```
.claude/skills/
├── README.md                    ← 이 파일(관리 가이드)
├── _template/                   ← 새 스킬 만들 때 복사하는 골격(밑줄 시작 = 스킬 아님)
│   ├── SKILL.md.template        ← 복사 후 SKILL.md 로 이름 바꿔 편집
│   └── references/
│       └── example-reference.md ← 보조 문서 예시(필요할 때만 읽힘)
└── <내-스킬>/                    ← 실제 스킬들이 여기 하나씩
    ├── SKILL.md                 ← 필수: 프론트매터(name·description) + 워크플로
    ├── references/              ← 선택: 길게 참조할 문서(온디맨드 로드)
    ├── scripts/                 ← 선택: 스킬이 부르는 스크립트
    └── assets/                  ← 선택: 템플릿·이미지 등
```

`_template`은 폴더명이 밑줄(`_`)로 시작하고 안에 `SKILL.md`가 아니라 `SKILL.md.template`이 있어
**스킬로 로드되지 않는다**(발견기는 정확히 `SKILL.md`만 찾음). 안심하고 복사 원본으로 둔다.

---

## 3. 새 스킬 추가하기 (3단계)

```bash
# 1) 템플릿 복사 → 원하는 kebab-case 이름으로
cp -r .claude/skills/_template .claude/skills/my-skill

# 2) 템플릿 파일을 진짜 SKILL.md 로 승격
mv .claude/skills/my-skill/SKILL.md.template .claude/skills/my-skill/SKILL.md

# 3) SKILL.md 의 name 을 폴더명과 똑같이, description 을 "무엇을·언제"로 채운다
```

편집 후 **새 세션에서** `/my-skill` 로 호출되거나, description이 맞으면 자동 트리거된다.
(현재 세션에는 즉시 반영 안 될 수 있음 → 새 대화로 확인.)

---

## 4. SKILL.md 프론트매터 규격

```markdown
---
name: my-skill                    # 필수. 폴더명과 동일. 소문자·숫자·하이픈만.
description: >-                    # 필수. 이게 자동 트리거의 핵심.
  이 스킬이 무엇을 하는지 + "언제 써야 하는지"를 구체적으로.
  트리거가 될 사용자 표현·상황을 넣을수록 정확히 발동한다.
# allowed-tools: Read, Grep, Glob  # 선택. 스킬이 쓸 수 있는 툴 제한.
---

# 제목

여기부터 실제 워크플로/지침. 필요하면 references/*.md 를 "필요할 때 읽어라"로 링크.
```

**description 잘 쓰는 법**: "~덱 만들어줘", "이 자료로 조립" 같은 **실제 발화**와
**대상·산출물**을 담는다. 모호하면 안 켜지고, 너무 넓으면 엉뚱하게 켜진다.
(좋은 예시는 이 레포 루트의 `SKILL.md` 프론트매터 참고.)

---

## 5. 관리 (이름변경·끄기·삭제)

| 하고 싶은 것 | 방법 |
|---|---|
| **끄기(임시 비활성)** | `SKILL.md` → `SKILL.md.off` 로 rename (발견 안 됨). 되돌리면 다시 켜짐 |
| **이름 변경** | 폴더명 + 프론트매터 `name` **둘 다** 같은 값으로 |
| **삭제** | 스킬 폴더 통째로 제거 |
| **일시 숨김** | 폴더를 `_보관/` 밑으로 이동(밑줄 시작이라 무시됨) |

---

## 6. 이 레포의 vibecoding-deck 와의 관계

이 프로젝트 **루트 자체가 `vibecoding-deck` 스킬 패키지**다(루트의 `SKILL.md`·`kit/`·`scripts/` …).
평소엔 여기 `.claude/skills/` 에 넣지 않는다 — 중복이 되기 때문. 다만 **"설치된 스킬처럼 켜서 테스트"** 하고 싶을 때만 링크한다:

```bash
# 복사(간단, 무거움)
cp -r . .claude/skills/vibecoding-deck   # 루트 전체를 복사(주의: 용량)

# 또는 심볼릭 링크(가벼움 · Windows는 관리자/개발자 모드 필요)
#   PowerShell:  New-Item -ItemType Junction -Path .claude\skills\vibecoding-deck -Target .
```

테스트가 끝나면 링크/사본을 지운다. (배포는 여전히 루트 → 대상 프로젝트의 `.claude/skills/vibecoding-deck/` 로 복사하는 것.)

---

## 7. 새 스킬 추가 체크리스트

- [ ] 폴더명 = 프론트매터 `name` (kebab-case, 고유)
- [ ] `description` 에 **무엇 + 언제(트리거 발화)** 명시
- [ ] 긴 참조는 `references/` 로 분리(SKILL.md 는 짧게)
- [ ] 스크립트/에셋은 `scripts/`·`assets/`
- [ ] **새 세션**에서 `/이름` 호출 또는 자동 트리거 확인
