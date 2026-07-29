// 오늘 점심 메뉴 추천 - script.js
// JS 안에 담아 둔 고정 메뉴 목록에서, 고른 종류에 맞는 메뉴를 추천한다.

// 추천에 사용할 고정 데이터 (외부 파일 없이 여기에 직접 적어 둔다)
const menus = [
  { name: "김치찌개", type: "한식" },
  { name: "비빔밥", type: "한식" },
  { name: "된장찌개", type: "한식" },
  { name: "짜장면", type: "중식" },
  { name: "짬뽕", type: "중식" },
  { name: "탕수육", type: "중식" },
  { name: "초밥", type: "일식" },
  { name: "우동", type: "일식" },
  { name: "돈카츠", type: "일식" },
  { name: "파스타", type: "양식" },
  { name: "스테이크", type: "양식" },
  { name: "리조또", type: "양식" },
  { name: "떡볶이", type: "분식" },
  { name: "김밥", type: "분식" },
  { name: "라면", type: "분식" }
];

const typeSelect = document.getElementById("type-select");
const recommendButton = document.getElementById("recommend-button");
const pickText = document.getElementById("pick");
const menuList = document.getElementById("menu-list");

function recommend() {
  const type = typeSelect.value;

  // 종류를 고르지 않았으면 추천하지 않고 무엇을 해야 하는지 알려 준다.
  if (type === "") {
    menuList.innerHTML = "";
    pickText.textContent = "메뉴 종류를 먼저 선택해 주세요.";
    return;
  }

  // 고른 종류에 맞는 메뉴만 모은다.
  const matched = [];
  for (let i = 0; i < menus.length; i++) {
    if (menus[i].type === type) {
      matched.push(menus[i].name);
    }
  }

  // 목록을 비우고 다시 채운다.
  menuList.innerHTML = "";
  for (let i = 0; i < matched.length; i++) {
    const item = document.createElement("li");
    item.textContent = matched[i];
    menuList.appendChild(item);
  }

  // 모인 메뉴 중 하나를 무작위로 골라 오늘의 추천으로 보여 준다.
  const randomIndex = Math.floor(Math.random() * matched.length);
  pickText.textContent = "오늘의 추천: " + matched[randomIndex];
}

recommendButton.addEventListener("click", recommend);
