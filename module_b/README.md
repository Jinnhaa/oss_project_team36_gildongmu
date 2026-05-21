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

현재 직접 구축한 테스트 케이스 15개 중 15개가 성공하였다.

| 구분 | 테스트 내용 | 결과 |
|---|---|---|
| 기본 경로 탐색 | 출발지와 목적지가 모두 포함된 문장 분석 | 성공 |
| 막차 확인 | “막차”, “끊겼나요” 등의 표현이 포함된 문장 분석 | 성공 |
| 대체 교통수단 요청 | “버스”, “다른 방법” 등의 표현이 포함된 문장 분석 | 성공 |
| 지하철 이용 가능 여부 | “지하철 탈 수 있나요?” 유형의 문장 분석 | 성공 |
| 출발지 누락 예외 처리 | 목적지만 입력된 문장에 대해 재입력 요청 오류 반환 | 성공 |
| 경로 데이터 매칭 | `routes.csv` 기반 추천 교통수단 및 예상 시간 반환 | 성공 |

## 7. 직접 구축한 샘플 데이터

Module B에서는 외부 교통 데이터셋을 그대로 사용하지 않고, MVP 검증을 위해 팀이 직접 샘플 데이터를 구축하였다.

- `routes.csv`: 출발지, 목적지, 시간, 지하철 상태, 막차 상태, 추천 교통수단, 예상 소요 시간 데이터
- `test_cases.csv`: 사용자가 실제로 말할 수 있는 자연어 입력 문장과 예상 결과
- `scenario_prompts.csv`: 의도 분석을 위한 교통 상황 시나리오 문장

## 8. 현재 한계

- 실제 교통 API를 사용하지 않기 때문에 실시간 교통 정보는 반영하지 않는다.
- 현재 장소 추출은 사전에 등록된 역명만 인식한다.
- `routes.csv`에 없는 경로는 판단하지 못한다.
- 현재 의도 분석은 키워드 기반이며, 추후 Sentence-Transformers 기반 의미 유사도 분석으로 확장할 예정이다.

## 9. 다음 개선 방향

- 주요 역명 사전 확대
- 사용자 발화 데이터 추가 구축
- `routes.csv` 샘플 경로 추가
- `scenario_prompts.csv` 기반 의미 유사도 분석 기능 추가
- Module A, Module C와의 통합 테스트 수행

## 10. C 모듈 전달용 샘플 출력

Module B의 분석 결과는 Module C에서 안내문 생성에 사용할 수 있도록 JSON 형식으로 전달한다.

샘플 출력 파일은 다음 위치에 저장되어 있다.

```text
module_b/sample_output.json

샘플 출력 주요 필드
필드	의미
status	처리 성공 또는 오류 여부
original_text	사용자 원문
start	출발지
destination	목적지
intent	사용자 요청 의도
scenario	교통 상황 시나리오
recommended_transport	추천 교통수단
route_summary	C 모듈 안내문 생성에 필요한 요약 경로 정보
C 모듈에서 활용할 값

C 모듈은 주로 다음 값을 사용한다.

start
destination
recommended_transport
route_summary.estimated_time
route_summary.transfer
scenario