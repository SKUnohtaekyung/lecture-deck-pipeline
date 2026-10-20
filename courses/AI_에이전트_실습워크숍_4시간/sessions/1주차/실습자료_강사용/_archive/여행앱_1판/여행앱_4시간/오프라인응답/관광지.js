// 오프라인응답/관광지.js — 도구(여행도구.html)가 읽는 파일입니다. 에이전트는 열지 않습니다. gen_app.py가 만듭니다.
// 형식 견본입니다. 이름은 모두 「(예시)」로 시작하는 지어낸 것이며 실제 행사가 아닙니다.
(function (o) {
  var 시각 = "2026-10-20 03:56";
  if (!o.만든시각 || o.만든시각 > 시각) o.만든시각 = 시각;
  o.날짜 = {"시작": "2026-10-27", "끝": "2026-10-28"};
  o.관광지 = {
   "요청": "https://apis.data.go.kr/B551011/KorService2/locationBasedList2?serviceKey=●●●●&MobileOS=ETC&MobileApp=FRAMEtrip&_type=json&mapX=128.8993979&mapY=37.76452&radius=20000&contentTypeId=12&arrange=E&numOfRows=50&pageNo=1 (형식 견본)",
   "응답": {
    "response": {
     "header": {
      "resultCode": "0000",
      "resultMsg": "OK"
     },
     "body": {
      "items": {
       "item": [
        {
         "addr1": "(예시 주소) 강릉시 남대천 둔치",
         "addr2": "",
         "contentid": "9900106",
         "contenttypeid": "12",
         "dist": "192.335170",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "128.9015000",
         "mapy": "37.7650000",
         "tel": "",
         "title": "(예시) 남대천 둔치 길"
        },
        {
         "addr1": "(예시 주소) 강릉시 시내",
         "addr2": "",
         "contentid": "9900105",
         "contenttypeid": "12",
         "dist": "1326.006158",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "128.8955000",
         "mapy": "37.7530000",
         "tel": "",
         "title": "(예시) 월화 거리 야경"
        },
        {
         "addr1": "(예시 주소) 강릉시 죽헌 일대",
         "addr2": "",
         "contentid": "9900103",
         "contenttypeid": "12",
         "dist": "2377.216586",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "128.8795000",
         "mapy": "37.7790000",
         "tel": "",
         "title": "(예시) 오죽헌 옛집 마당"
        },
        {
         "addr1": "(예시 주소) 강릉시 초당 일대",
         "addr2": "",
         "contentid": "9900104",
         "contenttypeid": "12",
         "dist": "3951.328142",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "128.9190000",
         "mapy": "37.7965000",
         "tel": "",
         "title": "(예시) 초당 솔숲 길"
        },
        {
         "addr1": "(예시 주소) 강릉시 해안",
         "addr2": "",
         "contentid": "9900107",
         "contenttypeid": "12",
         "dist": "4160.819588",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "128.9440000",
         "mapy": "37.7520000",
         "tel": "",
         "title": "(예시) 바다 전망 등대"
        },
        {
         "addr1": "(예시 주소) 강릉시 안목 일대",
         "addr2": "",
         "contentid": "9900102",
         "contenttypeid": "12",
         "dist": "4342.019992",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "128.9480000",
         "mapy": "37.7715000",
         "tel": "",
         "title": "(예시) 안목 해변 산책로"
        },
        {
         "addr1": "(예시 주소) 강릉시 경포 일대",
         "addr2": "",
         "contentid": "9900101",
         "contenttypeid": "12",
         "dist": "4361.195595",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "128.9090000",
         "mapy": "37.8030000",
         "tel": "",
         "title": "(예시) 경포대 앞 전망 쉼터"
        },
        {
         "addr1": "(예시 주소) 강릉시 시내 골목",
         "addr2": "",
         "contentid": "9900108",
         "contenttypeid": "12",
         "dist": "",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "",
         "mapy": "",
         "tel": "",
         "title": "(예시) 골목 정자"
        }
       ]
      },
      "numOfRows": 50,
      "pageNo": 1,
      "totalCount": 8
     }
    }
   }
  };
  o.예시창구 = (o.예시창구 || []).filter(function (n) { return n !== "관광지"; }).concat(["관광지"]);
  o.예시 = !!(o.예시창구 && o.예시창구.length);
})(window.오프라인응답 = window.오프라인응답 || {});
