// 오프라인응답/축제.js — 도구(여행도구.html)가 읽는 파일입니다. 에이전트는 열지 않습니다. gen_app.py가 만듭니다.
// 형식 견본입니다. 이름은 모두 「(예시)」로 시작하는 지어낸 것이며 실제 행사가 아닙니다.
(function (o) {
  var 시각 = "2026-10-20 03:56";
  if (!o.만든시각 || o.만든시각 > 시각) o.만든시각 = 시각;
  o.날짜 = {"시작": "2026-10-27", "끝": "2026-10-28"};
  o.축제 = {
   "요청": "https://apis.data.go.kr/B551011/KorService2/searchFestival2?serviceKey=●●●●&MobileOS=ETC&MobileApp=FRAMEtrip&_type=json&numOfRows=100&pageNo=1&eventStartDate=20261027&arrange=C (형식 견본)",
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
         "addr1": "(예시 주소) 강릉시 경포 일대",
         "addr2": "",
         "contentid": "9900001",
         "contenttypeid": "15",
         "eventenddate": "20261030",
         "eventstartdate": "20261024",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "128.9078000",
         "mapy": "37.8057000",
         "tel": "033-000-0001",
         "title": "(예시) 경포 가을 바다 음악회"
        },
        {
         "addr1": "(예시 주소) 강릉시 안목 일대",
         "addr2": "",
         "contentid": "9900002",
         "contenttypeid": "15",
         "eventenddate": "20261106",
         "eventstartdate": "20261020",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "128.9512000",
         "mapy": "37.7727000",
         "tel": "033-000-0002",
         "title": "(예시) 안목 커피 골목 시음 주간"
        },
        {
         "addr1": "(예시 주소) 강릉시 초당 일대",
         "addr2": "",
         "contentid": "9900003",
         "contenttypeid": "15",
         "eventenddate": "20261029",
         "eventstartdate": "20261028",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "128.9170000",
         "mapy": "37.7940000",
         "tel": "033-000-0003",
         "title": "(예시) 초당 두부 마을 장터"
        },
        {
         "addr1": "(예시 주소) 강릉시 죽헌 일대",
         "addr2": "",
         "contentid": "9900004",
         "contenttypeid": "15",
         "eventenddate": "20261101",
         "eventstartdate": "20261027",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "128.8790000",
         "mapy": "37.7790000",
         "tel": "033-000-0004",
         "title": "(예시) 오죽헌 달빛 산책"
        },
        {
         "addr1": "(예시 주소) 강릉시 중앙시장 일대",
         "addr2": "",
         "contentid": "9900005",
         "contenttypeid": "15",
         "eventenddate": "20261025",
         "eventstartdate": "20261015",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "128.8980000",
         "mapy": "37.7515000",
         "tel": "033-000-0005",
         "title": "(예시) 중앙시장 지난 가을 장터"
        },
        {
         "addr1": "(예시 주소) 강릉시 시내 골목",
         "addr2": "",
         "contentid": "9900006",
         "contenttypeid": "15",
         "eventenddate": "20261028",
         "eventstartdate": "20261027",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "",
         "mapy": "",
         "tel": "033-000-0006",
         "title": "(예시) 골목 책 마당"
        },
        {
         "addr1": "(예시 주소) 속초시 해안 일대",
         "addr2": "",
         "contentid": "9900007",
         "contenttypeid": "15",
         "eventenddate": "20261031",
         "eventstartdate": "20261026",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "128.5918000",
         "mapy": "38.2070000",
         "tel": "033-000-0007",
         "title": "(예시) 속초 먼 바다 불빛 축제"
        },
        {
         "addr1": "(예시 주소) 강릉시 남대천 둔치",
         "addr2": "",
         "contentid": "9900008",
         "contenttypeid": "15",
         "eventenddate": "20261030",
         "eventstartdate": "20261029",
         "firstimage": "",
         "firstimage2": "",
         "mapx": "128.9060000",
         "mapy": "37.7685000",
         "tel": "033-000-0008",
         "title": "(예시) 남대천 가을 연어 걷기"
        }
       ]
      },
      "numOfRows": 100,
      "pageNo": 1,
      "totalCount": 8
     }
    }
   }
  };
  o.예시창구 = (o.예시창구 || []).filter(function (n) { return n !== "축제"; }).concat(["축제"]);
  o.예시 = !!(o.예시창구 && o.예시창구.length);
})(window.오프라인응답 = window.오프라인응답 || {});
