// 가상 예산 연습 도구 - script.js
// 예산을 정하고 지출을 더해 합계와 잔액을 계산한다. 저장 기능은 없다.

const budgetInput = document.getElementById("budget");
const nameInput = document.getElementById("expense-name");
const amountInput = document.getElementById("expense-amount");
const addButton = document.getElementById("add-button");
const list = document.getElementById("expense-list");
const totalText = document.getElementById("total");
const balanceText = document.getElementById("balance");
const message = document.getElementById("message");

// 지금까지 더한 지출 금액을 모아 둔다.
const expenses = [];

function addExpense() {
  const amount = Number(amountInput.value);

  // 빈 입력 안내 (calc 프로젝트에만 넣는 간단한 안내)
  if (amountInput.value.trim() === "" || isNaN(amount) || amount <= 0) {
    message.textContent = "지출 금액을 0보다 큰 숫자로 입력해 주세요.";
    return;
  }

  const name = nameInput.value.trim() === "" ? "지출" : nameInput.value.trim();
  expenses.push(amount);

  const item = document.createElement("li");
  item.textContent = name + ": " + amount.toLocaleString() + " 원";
  list.appendChild(item);

  update();

  nameInput.value = "";
  amountInput.value = "";
  amountInput.focus();
}

function update() {
  let total = 0;
  for (let i = 0; i < expenses.length; i++) {
    total = total + expenses[i];
  }

  const budget = Number(budgetInput.value) || 0;
  const balance = budget - total;

  totalText.textContent = total.toLocaleString();
  balanceText.textContent = balance.toLocaleString();

  // 잔액이 음수이면 초과 안내를 보여 주고, 아니면 안내를 지운다.
  if (balance < 0) {
    message.textContent = "예산을 초과했어요.";
  } else {
    message.textContent = "";
  }
}

addButton.addEventListener("click", addExpense);

// 예산을 바꾸면 잔액도 다시 계산한다.
budgetInput.addEventListener("input", update);
