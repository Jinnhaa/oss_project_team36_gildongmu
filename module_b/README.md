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