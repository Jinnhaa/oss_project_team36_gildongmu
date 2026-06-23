# Module B: 장소·의도 분석 및 교통 판단 모듈

## 1. 모듈 개요

Module B는 사용자의 입력 문장을 분석하여 출발지, 목적지, 요청 의도를 추출하고, 이를 바탕으로 교통 경로 및 이동 가능 여부를 판단하는 모듈입니다.

Module A에서 전달된 음성 인식 결과 또는 사용자가 직접 입력한 텍스트를 받아 분석하며, 최종 결과는 Module C가 안내문을 생성할 수 있도록 JSON 형태로 반환합니다.

## 2. 주요 기능

* 사용자 입력 문장에서 출발지·목적지 추출
* BERT 기반 사용자 의도 분류
* NER 기반 장소 추출 및 역명 오인식 보정
* ODsay API 기반 대중교통 경로 조회
* CSV fallback 기반 보조 경로 조회
* Module C 전달용 JSON 결과 반환
* 오류 상황별 코드 반환

## 3. 처리 흐름

```text
사용자 입력 텍스트
→ 장소 추출
→ 의도 분류
→ 경로 조회
→ 이동 가능 여부 판단
→ JSON 결과 반환
```

## 4. 구현 모델 및 데이터셋

### BERT 기반 의도 분류

사용자의 발화가 어떤 요청인지 분류하기 위해 BERT 기반 의도 분류 모델을 사용했습니다.

의도 라벨은 다음과 같습니다.

* route_search: 경로 검색
* last_train_check: 막차 확인
* alternative_route: 대체 경로 요청
* subway_availability_check: 지하철 이용 가능 여부 확인
* unknown: 알 수 없는 요청

사용 데이터셋:

```text
module_b/data/intent_dataset.csv
```

약 1,000개 이상의 사용자 발화 문장을 구축하여 의도 분류 모델 학습에 활용했습니다.

### NER 기반 장소 추출

음성 인식 과정에서 역명이 잘못 인식되는 문제를 보완하기 위해 장소 추출 NER 모델을 구축했습니다.

사용 데이터셋:

```text
module_b/data/location_dataset.csv
module_b/data/location_ner_dataset.jsonl
```

`location_dataset.csv`는 장소 추출 원본 데이터셋이며, 총 1,600개의 사용자 발화 데이터를 포함합니다.
`location_ner_dataset.jsonl`은 NER 학습을 위해 토큰 단위 BIO 태그 형식으로 변환한 데이터셋입니다.

태그 구성은 다음과 같습니다.

* B-START: 출발지 시작 토큰
* I-START: 출발지 내부 토큰
* B-DEST: 목적지 시작 토큰
* I-DEST: 목적지 내부 토큰
* O: 장소명이 아닌 토큰

예시:

```json
{
  "text": "사울약에서 숙대입고까지 가고 싶어",
  "tokens": ["사울약", "에서", "숙대입고", "까지", "가고", "싶어"],
  "tags": ["B-START", "O", "B-DEST", "O", "O", "O"],
  "start": "서울역",
  "destination": "숙대입구역"
}
```

## 5. 역명 오인식 보정

Whisper 음성 인식 결과에서 발생할 수 있는 역명 오인식을 보완하기 위해 `location_surface_map.json`을 사용합니다.

예시:

```text
사울약 → 서울역
서울약 → 서울역
숙대입고 → 숙대입구역
강남약 → 강남역
```

NER 모델이 장소를 추출하지 못하는 경우에는 `stations.csv` 기반 역명 사전 매칭을 fallback으로 사용합니다.

## 6. 교통 경로 조회

Module B는 출발지와 목적지를 추출한 뒤 ODsay API를 통해 대중교통 경로 조회를 시도합니다.

API Key는 보안상 코드에 직접 작성하지 않고 환경변수로 설정합니다. 보고서에 첨부되어 있습니다.

### macOS / Linux

```bash
export ODSAY_API_KEY="발급받은_API_KEY"
python app.py
```

### Windows PowerShell

```powershell
$env:ODSAY_API_KEY="발급받은_API_KEY"
python app.py
```

ODsay API Key가 없거나 API 호출에 실패하는 경우, CSV 기반 fallback 데이터를 사용하여 기본 경로 정보를 반환합니다.

## 7. 주요 파일 설명

| 파일명                         | 설명                             |
| --------------------------- | ------------------------------ |
| `route_ai_analyzer.py`      | Module B 전체 분석 파이프라인           |
| `realtime_transport_api.py` | ODsay API 및 CSV fallback 경로 조회 |
| `train_bert_intent.py`      | BERT 의도 분류 모델 학습 코드            |
| `predict_bert_intent.py`    | 의도 분류 예측 코드                    |
| `train_location_ner.py`     | 장소 추출 NER 모델 학습 코드             |
| `predict_location_ner.py`   | 장소 추출 NER 예측 코드                |
| `test_location_ner.py`      | 장소 추출 모델 테스트 코드                |
| `location_surface_map.json` | 오인식 표현과 실제 역명 매핑               |
| `stations.csv`              | 역명 사전 fallback 데이터             |

## 8. 반환 결과 예시

```json
{
  "status": "success",
  "data": {
    "original_text": "사울약에서 숙대입고까지 가고 싶어",
    "start": "서울역",
    "destination": "숙대입구역",
    "intent": "route_search",
    "intent_method": "bert_classifier",
    "location_method": "location_ner",
    "recommended_transport": "subway",
    "route_summary": {
      "estimated_time": "약 10분",
      "transfer": "환승 없음"
    }
  },
  "error": null
}
```

## 9. 오류 코드 예시

| 오류 코드                  | 설명                |
| ---------------------- | ----------------- |
| `B_EMPTY_TEXT`         | 입력 텍스트가 비어 있음     |
| `B_LOCATION_NOT_FOUND` | 출발지 또는 목적지를 찾지 못함 |
| `B_ROUTE_NOT_FOUND`    | 경로 정보를 찾지 못함      |
| `B_DATA_LOAD_FAILED`   | 데이터 파일 로드 실패      |

## 10. 실행 방법

프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python app.py
```

Module B는 전체 앱 실행 과정에서 자동으로 호출됩니다.
