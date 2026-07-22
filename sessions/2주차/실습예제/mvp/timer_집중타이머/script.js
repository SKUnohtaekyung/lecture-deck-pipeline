// 집중 타이머 - script.js
// 분을 입력받아 초 단위로 카운트다운하고, 0이 되면 종료 안내를 보여 준다.

const minutesInput = document.getElementById("minutes");
const startButton = document.getElementById("start-button");
const timeDisplay = document.getElementById("time-display");
const notice = document.getElementById("notice");

let remainingSeconds = 0;
let timerId = null;

function updateDisplay() {
  const minutes = Math.floor(remainingSeconds / 60);
  const seconds = remainingSeconds % 60;

  // 한 자리 숫자 앞에 0을 붙여 두 자리로 보여 준다.
  const mm = minutes < 10 ? "0" + minutes : "" + minutes;
  const ss = seconds < 10 ? "0" + seconds : "" + seconds;
  timeDisplay.textContent = mm + ":" + ss;
}

function startTimer() {
  // 이미 타이머가 돌고 있으면 멈추고 새로 시작한다.
  if (timerId !== null) {
    clearInterval(timerId);
  }

  const minutes = Number(minutesInput.value);
  remainingSeconds = minutes * 60;
  notice.textContent = "";
  updateDisplay();

  timerId = setInterval(function () {
    remainingSeconds = remainingSeconds - 1;
    updateDisplay();

    if (remainingSeconds <= 0) {
      clearInterval(timerId);
      timerId = null;
      notice.textContent = "집중 시간이 끝났어요. 잠시 쉬어 볼까요?";
    }
  }, 1000);
}

startButton.addEventListener("click", startTimer);
