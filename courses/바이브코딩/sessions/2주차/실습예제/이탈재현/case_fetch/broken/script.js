// 범위 이탈: 시작 데이터를 로컬 data.json 파일에서 fetch() 로 읽어 온다.
// file:// 에서 로컬 파일 fetch 는 차단되어(Failed to fetch) 시작 기록이 절대 나타나지 않는다.
var activities = [];

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

// 여기서 실패한다: file:// 에서는 이 fetch 가 거부된다.
fetch("./data.json")
  .then(function (res) {
    return res.json();
  })
  .then(function (data) {
    activities = data.activities;
    render();
  })
  .catch(function (err) {
    console.error("데이터를 불러오지 못했습니다.", err);
  });

render();
