// 오프라인응답/날씨.js — 도구(여행도구.html)가 읽는 파일입니다. 에이전트는 열지 않습니다. gen_app.py가 만듭니다.
(function (o) {
  var 시각 = "2026-10-20 03:56";
  if (!o.만든시각 || o.만든시각 > 시각) o.만든시각 = 시각;
  o.날짜 = {"시작": "2026-10-27", "끝": "2026-10-28"};
  o.날씨 = {
   "요청": "https://api.open-meteo.com/v1/forecast?latitude=37.76452&longitude=128.8994&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code&timezone=Asia/Seoul&start_date=2026-10-27&end_date=2026-10-28",
   "응답": {
    "latitude": 37.75,
    "longitude": 128.875,
    "generationtime_ms": 0.3294944763183594,
    "utc_offset_seconds": 32400,
    "timezone": "Asia/Seoul",
    "timezone_abbreviation": "GMT+9",
    "elevation": 12.0,
    "daily_units": {
     "time": "iso8601",
     "temperature_2m_max": "°C",
     "temperature_2m_min": "°C",
     "precipitation_probability_max": "%",
     "weather_code": "wmo code"
    },
    "daily": {
     "time": [
      "2026-10-27",
      "2026-10-28"
     ],
     "temperature_2m_max": [
      16.1,
      16.9
     ],
     "temperature_2m_min": [
      9.6,
      6.7
     ],
     "precipitation_probability_max": [
      54,
      6
     ],
     "weather_code": [
      55,
      3
     ]
    }
   }
  };
  o.예시 = !!(o.예시창구 && o.예시창구.length);
})(window.오프라인응답 = window.오프라인응답 || {});
