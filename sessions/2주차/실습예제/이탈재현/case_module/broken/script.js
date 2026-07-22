// 범위 이탈: import 로 다른 파일의 값을 가져온다.
// file:// 에서 module 스크립트와 import 는 CORS 정책으로 차단되어 이 파일 전체가 실행되지 않는다.
import { initialActivities } from "./data.js";

var activities = initialActivities.slice();

var input = document.getElementById("activityInput");
var button = document.getElementById("addButton");
var list = document.getElementById("logList");
var emptyMsg = document.getElementById("emptyMsg");

function render() {
  list.innerHTML = "";
  if (activities.length === 0) {
    emptyMsg.style.display = "block";
    return;
  }
  emptyMsg.style.display = "none";
  for (var i = 0; i < activities.length; i++) {
    var li = document.createElement("li");
    li.textContent = activities[i];
    list.appendChild(li);
  }
}

function addActivity() {
  var text = input.value.trim();
  if (text === "") {
    return;
  }
  activities.push(text);
  input.value = "";
  render();
}

button.addEventListener("click", addActivity);
render();
