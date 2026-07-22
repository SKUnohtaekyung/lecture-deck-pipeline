// 오늘의 활동 기록 도구 - script.js
// 활동을 입력받아 화면의 목록에 추가한다. 저장 기능은 없다(새로고침하면 사라짐).

const input = document.getElementById("activity-input");
const button = document.getElementById("record-button");
const list = document.getElementById("record-list");
const message = document.getElementById("message");

function addRecord() {
  const text = input.value.trim();

  // 빈 입력 안내 (앵커 프로젝트에만 넣는 간단한 안내)
  if (text === "") {
    message.textContent = "활동 내용을 입력한 뒤 기록하기를 눌러 주세요.";
    return;
  }

  message.textContent = "";

  const item = document.createElement("li");
  item.textContent = text;
  list.appendChild(item);

  input.value = "";
  input.focus();
}

button.addEventListener("click", addRecord);

// 엔터 키로도 기록할 수 있게 한다.
input.addEventListener("keydown", function (event) {
  if (event.key === "Enter") {
    addRecord();
  }
});
