// 걸음 수 거리 환산기 - script.js
// 걸음 수를 입력받아 대략적인 거리(m, km)로 바꾼다.

const stepsInput = document.getElementById("steps");
const convertButton = document.getElementById("convert-button");
const resultText = document.getElementById("result-text");

// 걸음 한 번의 평균 보폭(미터)
const STEP_LENGTH = 0.7;

function convert() {
  const steps = Number(stepsInput.value);

  const meters = steps * STEP_LENGTH;
  const kilometers = meters / 1000;

  resultText.textContent =
    steps + "걸음은 약 " + meters.toFixed(0) + "m (" + kilometers.toFixed(2) + "km) 입니다.";
}

convertButton.addEventListener("click", convert);
