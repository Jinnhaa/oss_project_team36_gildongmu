# Colab 장소 추출 NER 모델 학습 셀

## 1. GPU 확인

```python
!nvidia-smi
```

GPU가 안 뜨면 `런타임 > 런타임 유형 변경 > T4 GPU`로 변경합니다.

## 2. GitHub repo clone

```python
!git clone https://github.com/Jinnhaa/oss_project_team36_gildongmu.git
%cd oss_project_team36_gildongmu
!git checkout feature/module-b-location-ner
```

## 3. 패키지 설치

```python
!pip install transformers datasets scikit-learn pandas numpy accelerate seqeval
```

## 4. 데이터셋 확인

```python
!head -3 module_b/data/location_ner_dataset.jsonl
```

## 5. 학습 실행

```python
!python3 module_b/train_location_ner.py
```

## 6. 모델 파일 확인

```python
!ls module_b/models/location_ner_model
!ls module_b/location_label_map.json
!ls module_b/location_surface_map.json
```

## 7. 예측 테스트

```python
!python3 module_b/test_location_ner.py
```

## 8. 수동 테스트

```python
!python3 - <<'EOF'
from module_b.predict_location_ner import predict_locations

tests = [
    "사울약에서 숙대입고까지 가고 싶어",
    "서울약 에서 숙대 입고 여기 까지 가고 싶어요",
    "강남약에서 숙대입고까지 막차 남았어?",
    "홍대 입구 약에서 사울역까지 가는 길 알려줘",
]

for text in tests:
    print("입력:", text)
    print(predict_locations(text))
    print("-" * 50)
EOF
```

## 9. 모델 압축

```python
!zip -r location_ner_model.zip module_b/models/location_ner_model module_b/location_label_map.json module_b/location_surface_map.json
```

왼쪽 파일 탭에서 `location_ner_model.zip`을 다운로드합니다.
