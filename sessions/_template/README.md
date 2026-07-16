# _template — 새 주차 골격

이 폴더를 복사해 새 주차를 시작한다. 전체 규약은 [`../README.md`](../README.md).

## 시작 (루트에서)
```bash
cp -r sessions/_template "sessions/N주차"
cp "입력양식/콘텐츠초안템플릿.md" "sessions/N주차/초안.md"
```

## 제작 체크리스트
1. [ ] `초안.md`를 `입력양식/콘텐츠초안템플릿.md` 형식으로 채운다(교시별 4열 표 `#·슬라이드 제목·본문 문구·비유·멘트` + 아이콘 범례 서두).
2. [ ] 원본 리서치·자료를 `자료/`에 넣는다.
3. [ ] 스킬에 "N주차 덱 만들어줘" 요청 → 정보 모양 판단·레이아웃·조립(SKILL.md 워크플로). PART 매핑은 스킬이 확인받는다.
4. [ ] `python scripts/verify_deck.py sessions/N주차/강의덱.html --parts <파트수>` 통과(FAIL 0).
5. [ ] 로컬 서버(`python -m http.server`)로 오버플로·콘솔 육안 — `.hint-reveal`은 닫힘+강제로 연 상태 둘 다.
6. [ ] (선택) `python scripts/inline_deck.py sessions/N주차/강의덱.html`로 단일 파일 배포본.

## 팀 스킬 파이프라인으로 시작 (선택)

위 체크리스트의 자료 수집·초안 채우기를 팀 스킬 순서로 진행할 수도 있다. 각 단계는 사람이 직접 해도 산출물이 완전히 호환된다(같은 스키마 — 정본은 루트 `skills/README.md`).

1. `/리서치 N주차` — `자료/`를 채운다.
2. `/콘텐츠 N주차` — `초안.md`를 생성한다.
3. `/vibecoding-deck` — 덱·발표자 노트를 조립한다.
4. `/검토 N주차 전체` — 전 단계 산출물을 검수한다.
