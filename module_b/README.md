# Module B: 장소·의도 분석 및 교통 판단 모듈

## 1. 역할

Module B는 Module A에서 전달받은 사용자 입력 텍스트를 분석하여 출발지, 목적지, 사용자 의도, 교통 상황을 판단한다.

## 2. 입력

Module A의 출력값 중 `recognized_text`를 입력으로 받는다.

```json
{
  "recognized_text": "서울역에서 숙대입구역까지 가고 싶어요"
}
3. 출력

Module C에서 안내문을 생성할 수 있도록 구조화된 JSON 형식으로 결과를 반환한다.

{
  "status": "success",
  "data": {
    "original_text": "서울역에서 숙대입구역까지 가고 싶어요",
    "start": "서울역",
    "destination": "숙대입구역",
    "intent": "route_search",
    "scenario": "subway_available",
    "subway_status": "available",
    "last_train_status": "available",
    "alternative_needed": false,
    "recommended_transport": "subway",
    "route_summary": {
      "start": "서울역",
      "end": "숙대입구역",
      "transport": "subway",
      "estimated_time": "약 10분",
      "transfer": "환승 없음"
    }
  },
  "error": null
}
4. 담당 파일
route_ai_analyzer.py: 장소 추출, 의도 분석, 교통 판단 코드
routes.csv: 샘플 교통 데이터
scenario_prompts.csv: 의도 분석용 시나리오 문장
test_cases.csv: 테스트 문장

그다음 `module_b/routes.csv`에 아래 내용 넣어.

```csv
start,end,time,subway_status,last_train_status,scenario,transport,estimated_time,transfer
서울역,숙대입구역,23:00,available,available,subway_available,subway,약 10분,환승 없음
서울역,숙대입구역,00:30,unavailable,ended,last_train_ended,bus,약 25분,환승 없음
을지로입구역,숙대입구역,22:30,available,available,subway_available,subway,약 20분,1회 환승
을지로입구역,숙대입구역,00:20,unavailable,ended,bus_alternative,bus,약 35분,1회 환승
숙대입구역,서울역,23:10,available,available,subway_available,subway,약 10분,환승 없음
숙대입구역,서울역,00:40,unavailable,ended,last_train_ended,bus,약 25분,환승 없음

## 5. 테스트 방법

Module B 테스트는 `test_route_ai_analyzer.py`를 통해 실행한다.

```bash
python3 module_b/test_route_ai_analyzer.py

## 6. 테스트 결과

현재 테스트 케이스 5개 중 5개가 성공하였다.

| 번호 | 입력 문장 | 결과 | 비고 |
|---|---|---|---|
| 1 | 서울역에서 숙대입구역까지 가고 싶어요 | 성공 | 출발지·목적지·의도 정상 추출 |
| 2 | 지금 서울역에서 숙대입구역 갈 수 있어요? | 성공 | 경로 탐색 의도 정상 분류 |
| 3 | 서울역에서 숙대입구역 가는 막차 끊겼나요? | 성공 | 막차 확인 의도 정상 분류 |
| 4 | 지하철 없으면 버스로 숙대입구역까지 갈 수 있나요? | 성공 | 출발지 누락 상황을 `B_LOCATION_NOT_FOUND`로 정상 예외 처리 |
| 5 | 을지로입구역에서 숙대입구역까지 가고 싶어요 | 성공 | 문장 내 장소 등장 순서 기준으로 출발지·목적지 정상 추출 |

## 7. 현재 한계

- 현재 장소 추출은 사전에 등록된 역명만 인식한다.
- 출발지가 생략된 문장은 경로 판단을 수행하지 않고 재입력 요청 오류를 반환한다.
- `routes.csv`에 없는 경로는 판단하지 못한다.
- 현재 의도 분석은 키워드 기반이며, 추후 Sentence-Transformers 기반 의미 유사도 분석으로 확장할 예정이다.

## 8. 다음 개선 방향

- 주요 역명 사전 확대
- 출발지 생략 시 현재 위치 입력 요청 흐름 추가
- `routes.csv` 샘플 경로 추가
- `scenario_prompts.csv` 기반 의미 유사도 분석 기능 추가