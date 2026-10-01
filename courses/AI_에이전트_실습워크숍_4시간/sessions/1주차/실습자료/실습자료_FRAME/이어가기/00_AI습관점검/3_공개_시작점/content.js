/* AI 활용 습관 점검 — 문항과 결과 글 (이어가기 · 공개 시작점)
   2_제작_시작점의 문항.txt · 결과글.txt 내용을 옮긴 파일이다. 화면의 글은 전부 이 파일에서 읽는다.
   - questions: axis는 "start"(시작) 또는 "finish"(마무리), text는 「~한다」로 끝나는 한 문장
   - types: T1 시작 높음·마무리 높음 / T2 시작 낮음·마무리 높음 / T3 시작 높음·마무리 낮음 / T4 둘 다 낮음
            본인이 예상하는 유형을 포함한 두 유형은 summary(요약) · step(이번 주 해 볼 한 가지)이 필수이고,
            나머지 두 유형과 prompt(요청문 카드)는 비워도 된다. 비워 둔 유형이 나오면 화면이 안내 문구를 보여 준다 */
window.CHECK_CONTENT = {
  title: "AI 활용 습관 점검",
  axes: {
    start: { name: "시작", desc: "AI를 켜기 전에 내 생각을 먼저 두는가", high: "내 생각 먼저", low: "AI 먼저" },
    finish: { name: "마무리", desc: "받은 답을 쓰기 전에 확인하는가", high: "확인하고 씀", low: "그대로 씀" }
  },
  questions: [
    { axis: "start", text: "AI에게 묻기 전에 내 생각이나 초안을 한 줄이라도 적어 둔다." },
    { axis: "start", text: "결론을 묻기 전에 선택지와 장단점을 먼저 요청한다." },
    { axis: "finish", text: "AI 답에서 근거 하나를 원문이나 출처로 직접 확인한다." },
    { axis: "finish", text: "틀렸을 때 문제가 큰 일일수록 더 꼼꼼히 확인한다." }
  ],
  types: {
    T1: {
      summary: "AI에게 묻기 전에 생각을 적고, 받은 답을 확인한 뒤 쓰는 편입니다.",
      step: "확인에 걸린 시간을 한 번 재서 AI 없이 할 때와 비교합니다.",
      prompt: ""
    },
    T2: {
      summary: "",
      step: "",
      prompt: ""
    },
    T3: {
      summary: "",
      step: "",
      prompt: ""
    },
    T4: {
      summary: "AI 답을 먼저 받고, 대부분 그대로 쓰는 편입니다.",
      step: "AI 답을 내 말로 세 줄 요약해 본 뒤에 씁니다.",
      prompt: ""
    }
  }
};
