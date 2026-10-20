# API 이름표

창구 이름은 `계획.창구`에 씁니다. 호출은 `여행도구.html`이 합니다. 에이전트는 호출 주소를 만들지 않고, 사용자가 붙인 「결과 복사」 글에서 응답을 읽습니다.

## 지명찾기 (Nominatim)

- 받는 것: 장소 이름(예: 강릉)
- 돌려주는 필드: `lat` 위도 · `lon` 경도 · `display_name` 전체 이름. 숫자도 문자열로 옵니다.
- 예시 응답(실측): `"lat":"37.7645200","lon":"128.8993979","display_name":"강릉, 176, 용지로, 교2동, 강릉시, 강원특별자치도, 25491, 대한민국"`
- 막히는 경우: 초당 1회 제한. 결과가 없으면 빈 목록입니다. 도구가 결과를 저장해 다시 부르지 않습니다.

## 날씨 (Open-Meteo)

- 받는 것: 위도 · 경도 · 시작일 · 종료일
- 돌려주는 필드: `daily.time` 날짜 · `temperature_2m_max` 최고 기온(°C) · `temperature_2m_min` 최저 기온 · `precipitation_probability_max` 강수 확률(%) · `weather_code` 날씨 코드
- 예시 응답(2026-10-20 실측): `{"latitude":37.55,"longitude":127.0,…,"daily_units":{"time":"iso8601","temperature_2m_max":"°C"},"daily":{"time":["2026-10-20",…],"temperature_2m_max":[20.4,14.9,…]}}`
- 막히는 경우: 예보 범위 밖 날짜는 400입니다(실측). 그 날은 「예보 없음」입니다. `{"error":true,"reason":"Parameter 'start_date' is out of allowed range from 2026-07-18 to 2026-11-03"}`

## 축제 (TourAPI searchFestival2)

- 받는 것: 여행 시작일 이후의 축제 목록, 키
- 돌려주는 필드(`response.body.items.item[]`): `title` 이름 · `addr1` 주소 · `eventstartdate` 시작일 · `eventenddate` 종료일 · `mapx` 경도 · `mapy` 위도 · `firstimage` 사진 · `contentid` 번호 · `tel` 전화
- 예시 응답(형식 예시): `{"response":{"body":{"items":{"item":[{"title":"…","eventstartdate":"…","mapx":"…","mapy":"…","contentid":"…"}]}}}}`
- 막히는 경우: 도구가 끝난 축제와 먼 축제를 걸러 개수를 보여 줍니다.

## 관광지 (TourAPI locationBasedList2)

- 받는 것: 여행지 좌표와 반경, 키
- 돌려주는 필드: 축제와 같은 필드와 `dist` 중심에서의 거리
- 예시 응답: 축제와 같은 모양입니다(형식 예시).
- 막히는 경우: 좌표가 없는 항목은 지도에서 빠집니다.

## TourAPI 공통 함정(도구가 처리합니다)

- `mapx`는 경도, `mapy`는 위도입니다. 위도를 먼저 읽지 않습니다.
- 0건이면 `items`가 `""`이고, 1건이면 `item`이 목록이 아닌 객체입니다.
- 숫자 필드가 문자열로 옵니다.
- 인증 오류는 JSON을 요청해도 `<`로 시작하는 XML입니다. `SERVICE_KEY_IS_NOT_REGISTERED_ERROR`(코드 30), `LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR`(코드 22). 개발계정은 하루 1,000회입니다.
