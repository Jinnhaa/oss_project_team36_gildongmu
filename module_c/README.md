# Module C: 안내문 생성, 음성 출력 및 모바일형 인터페이스 모듈

## 1. 역할

Module C는 Module B에서 전달받은 교통 판단 결과를 바탕으로 노인 친화적인 안내문을 생성하고, 음성으로 출력하며, 모바일형 화면에 표시한다.

## 2. 입력

Module B의 출력값을 입력으로 받는다.

```json
{
  "status": "success",
  "data": {
    "start": "서울역",
    "destination": "숙대입구역",
    "intent": "route_search",
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

## 3. 출력

안내문, 음성 출력용 문장, 화면 구성에 필요한 값을 JSON 형식으로 반환한다.

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
    "voice_text": "서울역에서 숙대입구역까지 지하철로 이동할 수 있습니다. 서울역에서 지하철을 타세요. 숙대입구역에서 내리세요. 예상 이동 시간은 약 10분입니다.",
    "screen_type": "route_available",
    "tts_file_path": "outputs/voice/voice_guide.mp3"
  },
  "error": null
}
```

## 4. 담당 파일

| 파일 | 역할 |
|---|---|
| `guide_generator.py` | Module B 결과를 받아 시나리오별 노인 친화 안내문 생성 |
| `text_to_speech.py` | 안내문 텍스트를 MP3 음성 파일로 변환 (gTTS 활용) |
| `test_guide_generator.py` | guide_generator 단위 테스트 실행 파일 |
| `test_cases.csv` | 시나리오별 테스트 케이스 데이터 |
| `app.py` (루트) | 전체 모듈 통합 실행 및 Gradio 기반 모바일형 UI |

## 5. 테스트 방법

Module C 테스트는 `test_guide_generator.py`를 통해 실행한다.

```bash
py module_c/test_guide_generator.py
```

## 6. 테스트 결과

테스트 케이스 7개 중 7개가 성공하였다.

| 구분 | 테스트 내용 | 결과 |
|---|---|---|
| subway_available | 지하철 이용 가능 안내문 생성 | 성공 |
| last_train_ended | 막차 종료 안내문 생성 | 성공 |
| bus_alternative | 버스 대체 안내문 생성 | 성공 |
| walking_needed | 도보 안내문 생성 | 성공 |
| need_more_info | 추가 정보 요청 안내문 생성 | 성공 |
| unknown | 판단 불가 안내문 생성 | 성공 |
| B 오류 입력 | C_EMPTY_ROUTE_RESULT 오류 처리 | 성공 |

## 7. 활용 오픈소스

| 라이브러리 | 활용 목적 |
|---|---|
| `gTTS` (Google Text-to-Speech) | 한국어 안내문을 MP3 음성 파일로 변환 |
| `gradio` | 모바일 친화형 웹 UI 구성 |

### gTTS 활용 방식

- 언어: 한국어 (`lang="ko"`)
- 속도: 느리게 (`slow=True`) — 노인 사용자를 위한 천천히 읽기 적용
- 출력 경로: `outputs/voice/voice_guide.mp3`

## 8. UI 실행 방법

```bash
py app.py
```

실행 후 터미널에 표시되는 주소(예: `http://127.0.0.1:7860`)를 브라우저에서 열면 모바일형 UI를 확인할 수 있다.

## 9. 현재 한계

- gTTS는 인터넷 연결이 필요하므로 오프라인 환경에서는 음성 출력이 불가능하다.
- Module B의 샘플 데이터에 있는 경로만 안내 가능하다.
- Module A가 통합되기 전까지는 텍스트 직접 입력 방식으로 동작한다.

## 10. 다음 개선 방향

- 오프라인 TTS fallback 적용 (`pyttsx3`)
- Module A 음성 입력 통합 연동
- UI 글자 크기 조절 기능 추가
- Module A, B와의 통합 테스트 수행

## 11. 설치 방법

프로젝트 실행 전 필요한 패키지는 다음 명령어로 설치한다.

```bash
py -m pip install -r requirements.txt
```
