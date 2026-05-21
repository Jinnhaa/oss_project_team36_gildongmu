# 길동무 모듈 통합 규칙

## 1. 전체 실행 흐름

길동무 프로젝트는 사용자 입력을 받아 다음 순서로 처리한다.

```text
사용자 입력
→ Module A: 음성 입력 및 음성 인식
→ Module B: 장소·의도 분석 및 교통 판단
→ Module C: 안내문 생성·음성 출력·모바일형 인터페이스
````

## 2. 모듈 역할

| 모듈       | 담당   | 역할                       | 주요 파일                                               |
| -------- | ---- | ------------------------ | --------------------------------------------------- |
| Module A | 김유진  | 음성 또는 텍스트 입력을 받아 텍스트로 변환 | `speech_to_text.py`                                 |
| Module B | 양이진하 | 출발지·목적지 추출, 의도 분석, 교통 판단 | `route_ai_analyzer.py`                              |
| Module C | 이예원  | 쉬운 안내문 생성, 음성 출력, 화면 구성  | `guide_generator.py`, `text_to_speech.py`, `app.py` |

## 3. 공통 데이터 전달 규칙

모듈 간 데이터는 `dict` 또는 `JSON` 형식으로 전달한다.

모든 모듈의 기본 반환 형식은 다음과 같다.

```json
{
  "status": "success",
  "data": {},
  "error": null
}
```

오류 발생 시에는 다음 형식을 따른다.

```json
{
  "status": "error",
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "오류 안내 메시지"
  }
}
```

## 4. Module A → Module B 전달 규칙

### 4.1 Module A 입력

#### 음성 입력

```json
{
  "input_type": "audio",
  "audio_path": "data/audio/sample.wav",
  "text": null
}
```

#### 텍스트 직접 입력

```json
{
  "input_type": "text",
  "audio_path": null,
  "text": "서울역에서 숙대입구역까지 가고 싶어요"
}
```

### 4.2 Module A 출력

Module A는 사용자 입력을 텍스트로 변환한 뒤 `recognized_text`를 반환한다.

```json
{
  "status": "success",
  "data": {
    "recognized_text": "서울역에서 숙대입구역까지 가고 싶어요",
    "input_type": "text",
    "audio_path": null
  },
  "error": null
}
```

### 4.3 Module A 오류 코드

| 코드                           | 의미            |
| ---------------------------- | ------------- |
| `A_EMPTY_INPUT`              | 입력값 없음        |
| `A_AUDIO_FILE_NOT_FOUND`     | 음성 파일 없음      |
| `A_UNSUPPORTED_AUDIO_FORMAT` | 지원하지 않는 음성 형식 |
| `A_STT_FAILED`               | 음성 인식 실패      |

## 5. Module B → Module C 전달 규칙

### 5.1 Module B 입력

Module B는 Module A의 `recognized_text`를 입력으로 받는다.

```json
{
  "recognized_text": "서울역에서 숙대입구역까지 가고 싶어요"
}
```

### 5.2 Module B 출력

Module B는 장소, 의도, 교통 판단 결과를 반환한다.

```json
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
```

### 5.3 intent 값

| 값                           | 의미              |
| --------------------------- | --------------- |
| `route_search`              | 경로 탐색           |
| `last_train_check`          | 막차 확인           |
| `alternative_route`         | 대체 교통수단 요청      |
| `subway_availability_check` | 지하철 이용 가능 여부 확인 |
| `unknown`                   | 의도 파악 실패        |

### 5.4 scenario 값

| 값                  | 의미        |
| ------------------ | --------- |
| `subway_available` | 지하철 이용 가능 |
| `last_train_ended` | 막차 종료     |
| `bus_alternative`  | 버스 대체 필요  |
| `walking_needed`   | 도보 이동 필요  |
| `need_more_info`   | 추가 정보 필요  |
| `unknown`          | 판단 불가     |

### 5.5 추천 교통수단 값

| 값        | 의미    |
| -------- | ----- |
| `subway` | 지하철   |
| `bus`    | 버스    |
| `walk`   | 도보    |
| `taxi`   | 택시    |
| `none`   | 추천 불가 |

### 5.6 Module B 오류 코드

| 코드                     | 의미                |
| ---------------------- | ----------------- |
| `B_EMPTY_TEXT`         | 분석할 텍스트 없음        |
| `B_LOCATION_NOT_FOUND` | 출발지 또는 목적지 추출 실패  |
| `B_ROUTE_NOT_FOUND`    | 샘플 교통 데이터에서 경로 없음 |
| `B_INTENT_UNKNOWN`     | 의도 분석 실패          |
| `B_DATA_LOAD_FAILED`   | 데이터 파일 로드 실패      |

## 6. Module C 최종 출력 규칙

### 6.1 Module C 입력

Module C는 Module B의 판단 결과를 입력으로 받는다.

```json
{
  "status": "success",
  "data": {
    "start": "서울역",
    "destination": "숙대입구역",
    "scenario": "subway_available",
    "recommended_transport": "subway",
    "route_summary": {
      "estimated_time": "약 10분",
      "transfer": "환승 없음"
    }
  },
  "error": null
}
```

### 6.2 Module C 출력

Module C는 화면 출력용 안내문과 음성 출력용 문장을 생성한다.

```json
{
  "status": "success",
  "data": {
    "title": "지하철로 이동할 수 있어요",
    "summary_message": "서울역에서 숙대입구역까지 지하철로 이동할 수 있습니다.",
    "guide_steps": [
      "서울역에서 지하철을 타세요.",
      "숙대입구역에서 내리세요.",
      "예상 이동 시간은 약 10분입니다."
    ],
    "voice_text": "서울역에서 숙대입구역까지 지하철로 이동할 수 있습니다. 예상 이동 시간은 약 10분입니다.",
    "screen_type": "route_available",
    "tts_file_path": "outputs/voice/voice_guide.mp3"
  },
  "error": null
}
```

### 6.3 screen_type 값

| 값                   | 의미         |
| ------------------- | ---------- |
| `route_available`   | 이동 가능 안내   |
| `alternative_route` | 대체 교통수단 안내 |
| `last_train_ended`  | 막차 종료 안내   |
| `need_more_info`    | 추가 정보 요청   |
| `error`             | 오류 안내      |

### 6.4 Module C 오류 코드

| 코드                          | 의미         |
| --------------------------- | ---------- |
| `C_EMPTY_ROUTE_RESULT`      | B 모듈 결과 없음 |
| `C_GUIDE_GENERATION_FAILED` | 안내문 생성 실패  |
| `C_TTS_FAILED`              | 음성 출력 실패   |
| `C_UI_RENDER_FAILED`        | 화면 출력 실패   |

## 7. 최종 통합 실행 규칙

최종 통합 실행은 `app.py`에서 수행한다.

```python
from module_a.speech_to_text import process_input
from module_b.route_ai_analyzer import analyze_route
from module_c.guide_generator import generate_guide

def main():
    a_result = process_input()

    if a_result["status"] == "error":
        return a_result

    b_result = analyze_route(a_result)

    if b_result["status"] == "error":
        return b_result

    c_result = generate_guide(b_result)

    return c_result

if __name__ == "__main__":
    result = main()
    print(result)
```

## 8. 폴더 구조

```text
oss_project_team36_gildongmu/
│
├── README.md
├── requirements.txt
├── app.py
│
├── module_a/
│   ├── speech_to_text.py
│   └── README.md
│
├── module_b/
│   ├── route_ai_analyzer.py
│   ├── routes.csv
│   ├── scenario_prompts.csv
│   ├── test_cases.csv
│   └── README.md
│
├── module_c/
│   ├── guide_generator.py
│   ├── text_to_speech.py
│   └── README.md
│
├── data/
│   └── audio/
│
├── outputs/
│   ├── screenshots/
│   └── voice/
│
├── tests/
│   └── test_integration.py
│
└── docs/
    ├── integration_rule.md
    └── meeting_log.md
```

## 9. 브랜치 규칙

| 브랜치명                        | 용도          |
| --------------------------- | ----------- |
| `main`                      | 최종 안정 버전    |
| `dev`                       | 통합 개발 버전    |
| `feature/module-a-stt`      | Module A 개발 |
| `feature/module-b-route-ai` | Module B 개발 |
| `feature/module-c-guide-ui` | Module C 개발 |
| `docs/update-docs`          | 문서 수정       |

## 10. 커밋 메시지 규칙

커밋 메시지는 다음 형식을 따른다.

```text
[모듈명] 작업 내용
```

예시:

```text
[A] Add speech to text function
[B] Add route analyzer
[C] Add guide generator
[DOCS] Add integration rule
[TEST] Add integration test
```

## 11. 통합 전 체크리스트

### Module A

* [ ] 음성 입력을 텍스트로 변환할 수 있는가?
* [ ] 텍스트 직접 입력을 처리할 수 있는가?
* [ ] `recognized_text`를 반환하는가?
* [ ] 빈 입력 오류 처리를 했는가?

### Module B

* [ ] `recognized_text`를 입력으로 받을 수 있는가?
* [ ] 출발지와 목적지를 추출할 수 있는가?
* [ ] 사용자 의도를 분석할 수 있는가?
* [ ] 교통 판단 결과를 JSON으로 반환하는가?

### Module C

* [ ] B 모듈 결과를 입력으로 받을 수 있는가?
* [ ] 쉬운 안내문을 생성할 수 있는가?
* [ ] 음성 출력용 문장을 생성할 수 있는가?
* [ ] 화면 출력에 필요한 값을 반환하는가?

### 전체 통합

* [ ] A → B → C 순서로 실행되는가?
* [ ] 정상 입력 시 최종 안내문이 생성되는가?
* [ ] 오류 발생 시 안내 메시지가 출력되는가?
* [ ] GitHub에 코드, 데이터, 문서가 정리되어 있는가?
