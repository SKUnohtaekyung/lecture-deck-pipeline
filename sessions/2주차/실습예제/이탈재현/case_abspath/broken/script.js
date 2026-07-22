var activities = ["아침 스트레칭", "책 20쪽 읽기"];

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
