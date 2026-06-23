# Module B 장소 추출 NER 모델 추가 패키지

이 패키지는 기존 Module B 구조에 맞춰 장소 추출용 AI 모델을 추가하기 위한 파일입니다.

## 핵심 구조

기존:
- `predict_bert_intent.py`: 의도 분류 모델
- `route_ai_analyzer.py`: 장소 추출은 stations.csv 기반 규칙 처리

추가:
- `train_location_ner.py`: 장소 추출 NER 모델 학습
- `predict_location_ner.py`: 학습된 장소 추출 모델 예측
- `location_ner_dataset.jsonl`: 장소 추출 학습 데이터셋

## 데이터셋 특징

이번 데이터셋은 의도 분류용 데이터셋이 아닙니다.
출발지/목적지를 뽑기 위한 NER 데이터셋입니다.

예:
```json
{
  "text": "사울약 에서 숙대입고 까지 가고 싶어요",
  "tokens": ["사울약", "에서", "숙대입고", "까지", "가고", "싶어요"],
  "tags": ["B-START", "O", "B-DEST", "O", "O", "O"],
  "start": "서울역",
  "destination": "숙대입구역"
}
```

## Colab 실행 순서

```bash
!git clone https://github.com/Jinnhaa/oss_project_team36_gildongmu.git
%cd oss_project_team36_gildongmu
!git checkout feature/module-b-location-ner
```

```bash
!pip install transformers datasets scikit-learn pandas numpy accelerate seqeval
```

```bash
!python3 module_b/train_location_ner.py
```

```bash
!python3 module_b/test_location_ner.py
```

## route_ai_analyzer.py 연결

`location_ner_integration.patch`를 참고해 아래 구조로 연결합니다.

- `predict_location_ner.predict_locations()`를 먼저 사용
- 성공하면 NER 결과 사용
- 실패하면 기존 `extract_locations()` fallback
- 최종 결과에 `location_method` 추가
