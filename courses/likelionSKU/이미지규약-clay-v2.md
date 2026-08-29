# clay v2 이미지 프롬프트 규약 — likelionSKU

> **정본 고지**: 이 문서는 `likelionSKU/` 원본에서 이식했으며, 이후 정본은 이 파일이다.
> - 원본① `likelionSKU/덱_템플릿킷/images/공통이미지프롬프트.md`(96줄)
> - 원본② `likelionSKU/.claude/skills/likelion-deck/references/image-and-deploy.md`(38줄)
>
> 두 원본은 읽기 전용으로 두고 값을 바꾸지 않았다. 두 원본의 서술이 갈리는 지점은 임의로 합치지 않고 각 절에서 출처를 밝혀 병기했다. 이 문서는 `courses/likelionSKU/` 소속이라 이 저장소의 `references/이미지-디렉션-프롬프트.md`(`바이브코딩` 과목의 `paper-cut-v1` 계약)와는 **다른 스타일 계약**이다 — 두 계약의 값을 섞지 않는다.

## 1. 개요 — 하우스 스타일과 역할 분리

덱의 3D 일러스트는 **하나의 하우스 스타일 "clay v2"**로 통일한다. §2의 프롬프트는 **4블록 구조**이며, **블록 2(SUBJECT)만** 슬라이드마다 바꾸고 나머지 3블록은 **그대로** 둔다. (원본①)

**생성기 사양** (원본①): `gpt-image-1` · `size:"1024x1024"` · `background:"transparent"` → `b64_json` 저장.

**역할 분리** (원본②): Claude(이 스킬)는 이미지를 생성하지 않는다. 3D 에셋(표지 포함)은 `codex imagegen`이 만든다. 스킬의 역할은 다음 4단계뿐이다.

1. 일러스트가 필요한 슬라이드에 **슬롯만** 배치: `<img class="asset hero" src="img/slides/sNN_<concept>.png" alt="">`.
2. `make_prompt_sheet.py <덱>` 실행 → `이미지프롬프트.md`(codex 포맷) 생성.
3. 각 항목의 **SUBJECT**(그릴 대상)만 채운다 → **사용자가 codex imagegen 실행** → `img/slides/`에 저장.
4. 프리뷰로 이미지 반영 재확인.

> 원본②의 스크립트 경로(`make_prompt_sheet.py`, `.claude/skills/likelion-deck/scripts/...`)는 `likelionSKU/` 프로젝트 기준 그대로 옮겼다. 이 저장소의 `create-slides` 스킬에 동일 스크립트·경로가 있는지는 이 작업 범위에서 확인하지 않았다.

## 2. 4블록 프롬프트 계약

### 2.1 슬라이드마다 바꾸는 자리

```
[SUBJECT] — 이 슬라이드가 그릴 대상 또는 은유. 장면, 오브젝트, 캐릭터 행동, 조립되는 조각 등 자유롭게 선택.
[OPTIONAL DIRECTION] — 필요할 때만: 구도, 질감, 보조색, 은유 방식에 대한 짧은 방향.
```

### 2.2 복붙용 프롬프트 (블록 1·3·4는 고정, 블록 2만 교체)

원본①의 문구를 그대로 옮긴다.

```text
── BLOCK 1 · STYLE + MATERIAL & PALETTE (공통 방향) ──
A clean, friendly 3D educational illustration for a Korean lecture deck.
House style: soft-3D / clay v2, rounded, tactile, approachable, and easy to read at slide scale.
The image should explain the slide idea, not just decorate it.

MATERIAL: let the model choose the best surface mix for the metaphor.
UI panels, documents, tools, and technical objects may use smooth matte plastic, soft gloss, or frosted-glass accents.
Characters, gestures, and hand-built metaphors may lean into soft clay / hand-molded matte texture, with subtly uneven edges or gently pressed forms when that adds warmth.
Mixed surfaces are welcome when they help separate roles.

PALETTE: use white/grey/blue as the visual anchor, with a small but visible secondary accent chosen by the model.
The secondary accent should come from the subject, mood, or object separation; it should be visible at slide scale and should not collapse into another blue/cyan shade.
About 5-10% of the subject area is a useful target for character scenes, hand-built metaphors, or multi-object scenes.
Keep the overall impression calm, clean, and aligned with the white/grey/blue deck identity.

STYLE FREEDOM: vary the visual metaphor between slides.
The subject may become a character scene, a sculpted object metaphor, assembled pieces, a before/after transformation, or a compact workflow.
Prefer the clearest metaphor over repeating the same document-arrow-screen formula.

LIGHTING: soft studio light, gentle ambient occlusion, and internal object shading.
CAMERA: near eye-level three-quarter view with a slight downward tilt, unless the subject works better from another simple angle.

── BLOCK 2 · SUBJECT + COMPOSITION (슬라이드마다 교체) ──
SUBJECT: [SUBJECT — 예: "두 개의 둥근 문(門)이 나란히 서 있고, 한쪽 문으로만 동전이 굴러 들어간다;
보조로 작은 캐릭터 실루엣 둘"].
[OPTIONAL DIRECTION — 필요할 때만: "make the character more clay-like", "use a small non-orange accent if helpful", "avoid the arrow-screen formula"].
COMPOSITION: subject sits on the RIGHT side of a 1:1 frame, floating; leave the LEFT ~35-40% visually lighter for text.
Characters are faceless / near-faceless and stylized.

── BLOCK 3 · RENDER (고정) ──
Rendered FLOATING FREELY on a FULLY TRANSPARENT background (PNG with alpha).
Keep it as a standalone cutout asset: no visible backdrop, floor plane, base disk, pedestal, or framing card unless the subject itself requires a self-contained prop.
Use internal object shading for depth. A subtle self-contained shadow may be included only if it improves grounding.
Generous empty margins. 1:1 square.

── BLOCK 4 · REQUIRED CONSTRAINTS (고정) ──
No readable text, letters, numbers, Korean characters, logos, or watermark.
Use abstract UI marks instead of real writing.
Keep characters faceless or near-faceless.
Avoid styles that break the 3D house style, such as photoreal faces, flat vector art, or anime rendering.
```

### 2.3 블록별 요지

- **블록 1 STYLE+MATERIAL&PALETTE(고정)** — soft-3D clay, 둥글고 촉감 있고 슬라이드 배율에서 읽기 쉬움. 소재는 UI·문서·도구는 매트 플라스틱/소프트 글로스/프로스티드 글라스, 캐릭터·손으로 빚은 은유는 소프트 클레이 질감으로 자유 혼합. 팔레트는 흰/회/파랑을 시각 앵커로 삼고, 모델이 고르는 보조 액센트 1색을 더한다(다른 파랑/청록 계열로 수렴하면 안 됨) — 캐릭터 장면·손빚음 은유·다중 오브젝트 장면에서는 피사체 면적의 **약 5~10%**가 기준. 조명은 소프트 스튜디오광 + 은은한 앰비언트 오클루전, 카메라는 근안구높이 3/4뷰 + 약간의 하향 틸트(피사체에 안 맞으면 다른 단순 각도 허용).
- **블록 2 SUBJECT+COMPOSITION(슬라이드마다 교체 — 교체 대상은 여기뿐)** — subject는 1:1 프레임의 **오른쪽**에 떠 있고, **왼쪽 ~35–40%**는 텍스트를 위해 시각적으로 가볍게 비운다. 캐릭터는 무이목구비(faceless)~near-faceless로 스타일화한다. (원본②의 운영 요약은 구성요소 수를 "메타포 main 1 + 보조 2~4"로 더 구체화한다 — 원본①의 복붙용 프롬프트 자체에는 이 개수 지침이 없다.)
- **블록 3 RENDER(고정)** — **완전 투명 배경(alpha PNG)** 위에 자유롭게 떠 있는 컷아웃 에셋. 받침대·바닥면·베이스 디스크·프레이밍 카드 등 배경 요소 금지(피사체 자체가 자기완결적 소품을 요구할 때만 예외). 깊이감은 내부 오브젝트 셰이딩으로 표현하고, 그라운딩에 도움될 때만 옅은 자기그림자 1개를 허용. 여백 넉넉히, **1:1 정사각**.
- **블록 4 REQUIRED CONSTRAINTS/NEGATIVE(고정)** — 읽을 수 있는 글자·숫자·한글·로고·워터마크 금지(실제 문자 대신 추상적 UI 마크 사용). 캐릭터는 무이목구비~near-faceless 유지. 포토리얼 얼굴·플랫 벡터아트·애니메이션 렌더링 등 3D 하우스 스타일을 깨는 화풍 금지.

> **원본② 보강 — NEGATIVE 추가 항목**: 위 블록 4는 원본①의 복붙용 프롬프트 원문이다. 원본②의 운영 요약("clay v2 4블록 계약")은 NEGATIVE에 **"특히 차트·코인·게이지에 숫자·틱·통화 금지, 실사얼굴·레인보우·네온·플랫벡터·애니 금지"**를 덧붙인다. 원본①에는 없는 항목(레인보우·네온 금지, 차트/코인/게이지의 숫자·틱·통화 특칙)이라 이 문서에서 처음 합치지 않고, 두 원본에 각각 있는 문구를 모두 보존한다.
>
> **원본② 보강 — STYLE/PALETTE 운영 요약**: 원본②는 조명·그림자를 **"upper-left 라이트, 드롭섀도 1개"**로 더 구체화한다(원본①은 "near eye-level 3/4 뷰"와 "그라운딩에 도움될 때만 자기그림자 1개 허용"으로 서술 — 방향은 같되 원본②가 더 구체적인 표현을 쓴다). 그리고 원본②는 팔레트를 **"순백+ice-blue(#8EC3FF)+cobalt(#0066CC)+navy(#233B66) 깊이"**로 hex까지 명시한다. **이 hex 3종은 원본①의 복붙용 프롬프트(§2.2) 안에는 등장하지 않는다** — 원본①은 "흰/회/파랑 앵커 + 모델이 고르는 보조 액센트"로만 서술해 색을 열어둔다. 이 hex 3종이 쓰이는 맥락은 §3(두 코발트)에서 다룬다.

## 3. "두 코발트" — 화면 UI 색과 이미지 프롬프트 색은 다르다

원문 인용(원본②, 그대로):

> "두 코발트" 주의: 화면 UI 코발트는 `#3060C3`, **이미지 프롬프트의** 코발트는 `#0066CC`(위 계약대로). 혼동 금지.

이 규약에서 "코발트"는 **두 층에서 서로 다른 값**을 쓴다 — 우연한 불일치가 아니라 원문이 명시적으로 표시한 **의도된 이원화**다.

| 층 | 코발트 값 | 근거·용도 |
|---|---|---|
| 화면 UI(덱 CSS) | `#3060C3` | 테마 토큰 `--blue`. HTML/CSS의 강조색은 이 값만 쓴다. |
| 이미지 프롬프트(clay v2 생성) | `#0066CC` | 원본②의 STYLE/PALETTE 요약 "순백+ice-blue(`#8EC3FF`)+cobalt(`#0066CC`)+navy(`#233B66`) 깊이"에 등장. ice `#8EC3FF`·navy `#233B66`과 한 세트로, 이미지 생성 쪽에서만 쓰는 3D 깊이 팔레트다. |

**왜 갈라 두는가** — 두 원본이 명시하는 근거는 "위 계약대로"(원본②의 STYLE/PALETTE 요약을 가리킴)와 "혼동 금지" 두 마디뿐이다. 두 원본 모두 그 이상의 인과적 설명(예: 생성 모델이 다른 hex에서 더 잘 반응한다는 식의 이유)을 적지 않았고, 이 문서도 없는 이유를 지어내지 않는다. 실무 규칙은 다음 한 가지로 충분하다.

> **UI CSS에는 `#3060C3`만, 이미지 생성 프롬프트에는 `#0066CC`(+ice `#8EC3FF`+navy `#233B66`)만 쓴다 — 서로의 값이 상대 층으로 새어 들어가지 않게 한다.**

## 4. 네이밍 규칙

```
s<NN>_<concept-kebab>[-<style-version>][-transparent].png
```
- `s<NN>` — 2자리 슬라이드 번호(`s07`, `s14`). **불변 접두.**
- `<concept-kebab>` — 소문자 케밥 컨셉(`actor-split`, `assumption-test`, `revenue-menu`).
- `-<style-version>` — (선택) 반복 태그: `-clay-v2`(소프트3D), `-bg-v2`(16:9 배경형).
- `-transparent` — (선택) 배경 제거 정제본. 덱에 실제 배선되는 건 보통 이 파일.
- 확장자 항상 `.png`(alpha).

예: `s14_actor-split-clay-v2-transparent.png`

(원본②는 같은 규칙을 "`s<두자리번호>_<개념-kebab>[-clay-v2][-transparent].png`. 불변부는 `s##_` + `.png`"로 더 짧게 요약한다 — 값은 같고 표현만 다르다.)

## 5. 배치 규칙 (덱 CSS와 짝)

- 투명 PNG는 **오른쪽에 크게**, subject의 빈 바운딩박스는 캔버스 밖으로 흘려도 됨(`right` 음수 허용).
- 대응 클래스: `.asset.hero`(우하 대형), `.actor-visual`/`.flow-visual`(배경형 z-index:1, 본문 z-index:2), `.reverse-visual`/`.risk-visual`(칼럼 안).
- **왼쪽 ~40%는 항상 비워** 본문이 들어갈 자리를 확보한다.

(원본① 「배치 규칙」 절과 원본② 역할 1단계의 하위 규칙이 같은 내용을 병기한다 — 두 원본이 일치하는 지점이라 하나로 합쳐 적었다.)

## 6. 특수 슬롯 두 개 (도입 이미지 · concept-recap 배경)

원본②에만 있는 내용이다(원본①은 표준 1:1 투명 흐름만 다룬다).

- **도입(2p) 이미지** `img/slides/s02_intro.png` — 스캐폴드가 넣는 중립 플레이스홀더. 표지처럼 **주제별로 새로 생성**한다(§7 워크플로로 자동 프롬프트되는 떠 있는 1:1 에셋 — 위 clay v2 계약 그대로).
- **마무리 배경** `concept-recap`의 `concept-bg`(`*-bg.png`) — **수동**. 떠 있는 1:1 에셋이 아니라 화면을 꽉 채우는 **풀블리드 가로(≈16:9)**다. RENDER 계약이 다르다: 투명·1:1 대신 **불투명·가장자리까지 꽉 참**, 피사체는 오른쪽에 몰고 **왼쪽 ~45%는 저대비/여백**(요약 패널 텍스트가 그 위에 얹힌다). `make_prompt_sheet.py`가 `*-bg.png`를 **제외**하므로 직접 만든다. 없어도 밝은 배경으로 무방하다.

## 7. 워크플로우 (원본①)

1. **컨셉 한 줄** 정하기 — "이 슬라이드가 그림으로 전달할 것 1가지".
2. 블록 2의 `[SUBJECT]`만 채워 프롬프트 완성.
3. `gpt-image-1`로 생성(투명 PNG). 글자·숫자 아티팩트가 보이면 `No readable text or numbers.`처럼 필요한 제약만 짧게 보강해 최대 2회 재생성.
4. 필요 시 배경 잔여물 제거 → `-transparent` 파일로 저장.
5. `img/slides/`에 네이밍 규칙대로 저장하고 슬라이드 `<img>` 경로 연결.

## 8. 배포 — 단일 파일 (선택) (원본②)

개발용은 `img/` 참조(가벼움). 학생 배포·오프라인은 이미지를 base64 인라인한 단일 HTML:

```
python .claude/skills/likelion-deck/scripts/inline_images.py 세션/<주제>/<덱>.html
# 용량 크면:
python .claude/skills/likelion-deck/scripts/inline_images.py 세션/<주제>/<덱>.html --downscale 900
```
- 원본(dev)은 불변, `<덱>_배포.html` 새로 생성.
- 목표 **3~8MB**(메일/USB). 8MB 초과 시 `--downscale 900`(Pillow 필요) 권장.
- Netlify: 세션 폴더의 `_redirects`(루트 → `_배포.html` 200 리라이트)로 드래그앤드랍.

> 스크립트 경로는 원본② 그대로다 — §1의 안내대로, 이 저장소의 `create-slides` 스킬에 동일 스크립트가 있는지는 확인하지 않았다.

---

**남은 확인 사항** — 원본①의 마지막 줄은 "공통 스타일 원본: 프로젝트 루트 `image_generation_prompts.md`"를 가리키지만, 2026-08-29 기준 이 저장소의 `likelionSKU/`에서 `image_generation_prompts.md`를 찾지 못했다. 참조가 가리키는 파일이 없는 상태를 그대로 옮기며, 내용을 지어내지 않는다.
