# _template — 새 주차 골격

이 폴더를 복사해 새 주차를 시작한다. 전체 규약은 [`../README.md`](../README.md).

## 시작 (루트에서)
```bash
cp -r sessions/_template "sessions/N주차"
cp "입력양식/콘텐츠초안템플릿.md" "sessions/N주차/초안.md"
```

## 제작 체크리스트 (2단계: 편집본 조각 → 배포 단일본)
1. [ ] `초안.md`를 `입력양식/콘텐츠초안템플릿.md` 형식으로 채운다(교시별 4열 표 `#·슬라이드 제목·본문 문구·비유·멘트` + 아이콘 범례 서두).
   - `deck.contract.json` 골격이 함께 복사된다 — 조립 단계에서 `slides`·`intro`·`sequences`·`must_keep`(초안의 「절대 사수」 목록)을 채워야 verify_deck 보존 게이트를 통과한다(규약: [`../README.md`](../README.md) 「주차 구조 계약」).
2. [ ] 원본 리서치·자료를 `자료/`에 넣는다.
3. [ ] `자료/이미지-에셋.json`에 슬라이드별 네 상태 판정과 재사용·생성 상태를 기록한다. `prompt_only`면 `자료/이미지-프롬프트.md`도 채운다.
4. [ ] 스킬에 "N주차 덱 만들어줘" 요청 → 정보 모양 판단·레이아웃·조립(SKILL.md 워크플로). 편집본은 `강의덱.초안/`에 **파트별 조각**(`shell.html` 고정슬롯 + PART마다 `part-NN.html`)으로 둔다. PART 매핑은 스킬이 확인받는다.
5. [ ] 미리보기: `python scripts/assemble_deck.py sessions/N주차/강의덱.초안 --watch` → 브라우저로 `강의덱.html`을 열고 대화하며 조각을 수정(저장 시 통합본 자동 갱신).
   - 조립 보고(`조립_보고.md`)를 쓰면 **머리에 기준 덱 식별자**(«**N장** · sha256 \`앞8자\`»)를 적는다. 재조립하면 갱신하고, 시점 기록으로 남길 문서는 `[시점 스냅샷 YYYY-MM-DD]`를 선언한다 — `verify_report_freshness.py`가 낡음·미기재를 잡는다(규약: [`../README.md`](../README.md) 「주차 구조 계약」).
6. [ ] `python scripts/verify_deck.py sessions/N주차/강의덱.html --parts <파트수>` 통과(FAIL 0). 로컬 서버로 오버플로·콘솔 육안 — `.hint-reveal`은 닫힘+강제로 연 상태 둘 다.
7. [ ] 최종본: `python scripts/build_release.py sessions/N주차/강의덱.초안` → `강의덱_배포.html`(단일 자립본, 폰트 임베드). **자립성 강제 게이트를 통과해야 완성**. unresolved 설명·기억 슬롯이 있으면 먼저 실제 에셋을 준비한다.

## 팀 스킬 파이프라인으로 시작 (선택)

위 체크리스트의 자료 수집·초안 채우기를 팀 스킬 순서로 진행할 수도 있다. 각 단계는 사람이 직접 해도 산출물이 완전히 호환된다(같은 스키마 — 정본은 루트 `skills/README.md`).

1. `/리서치 N주차` — `자료/`를 채운다.
2. `/콘텐츠 N주차` — `초안.md`를 생성한다.
3. `/create-slides` — 덱·발표자 노트를 조립한다.
4. `/검토 N주차 전체` — 전 단계 산출물을 검수한다.
