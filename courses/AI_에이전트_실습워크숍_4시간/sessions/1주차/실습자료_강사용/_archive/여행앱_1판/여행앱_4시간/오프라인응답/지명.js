// 오프라인응답/지명.js — 도구(여행도구.html)가 읽는 파일입니다. 에이전트는 열지 않습니다. gen_app.py가 만듭니다.
(function (o) {
  var 시각 = "2026-10-20 03:56";
  if (!o.만든시각 || o.만든시각 > 시각) o.만든시각 = 시각;
  o.날짜 = {"시작": "2026-10-27", "끝": "2026-10-28"};
  o.지명 = {
   "강릉": {
    "요청": "https://nominatim.openstreetmap.org/search?q=강릉&format=json&limit=5&countrycodes=kr&accept-language=ko",
    "응답": [
     {
      "place_id": 270067930,
      "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
      "osm_type": "node",
      "osm_id": 8223919750,
      "lat": "37.7645200",
      "lon": "128.8993979",
      "class": "railway",
      "type": "station",
      "place_rank": 30,
      "importance": 0.43014693072468363,
      "addresstype": "railway",
      "name": "강릉",
      "display_name": "강릉, 176, 용지로, 교2동, 강릉시, 강원특별자치도, 25491, 대한민국",
      "boundingbox": [
       "37.7595200",
       "37.7695200",
       "128.8943979",
       "128.9043979"
      ]
     },
     {
      "place_id": 270218801,
      "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
      "osm_type": "node",
      "osm_id": 436239829,
      "lat": "37.7464349",
      "lon": "128.8395253",
      "class": "highway",
      "type": "motorway_junction",
      "place_rank": 30,
      "importance": 6.204852368958599e-05,
      "addresstype": "highway",
      "name": "강릉",
      "display_name": "강릉, 동해고속도로, 금산리, 강릉시, 강원특별자치도, 25448, 대한민국",
      "boundingbox": [
       "37.7463849",
       "37.7464849",
       "128.8394753",
       "128.8395753"
      ]
     },
     {
      "place_id": 270386929,
      "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
      "osm_type": "node",
      "osm_id": 436244483,
      "lat": "37.7538262",
      "lon": "128.8390523",
      "class": "highway",
      "type": "motorway_junction",
      "place_rank": 30,
      "importance": 6.204852368958599e-05,
      "addresstype": "highway",
      "name": "강릉",
      "display_name": "강릉, 동해고속도로, 위촌리, 강릉시, 강원특별자치도, 25447, 대한민국",
      "boundingbox": [
       "37.7537762",
       "37.7538762",
       "128.8390023",
       "128.8391023"
      ]
     }
    ]
   }
  };
  o.예시 = !!(o.예시창구 && o.예시창구.length);
})(window.오프라인응답 = window.오프라인응답 || {});
