"""
Module B - 학습된 BERT 의도 분류 모델 예측 코드

역할:
1. module_b/models/bert_intent_model/에 저장된 모델을 불러온다.
2. module_b/label_map.json을 읽어 id와 intent 라벨을 매핑한다.
3. 사용자 입력 문장을 BERT 모델에 넣어 intent를 예측한다.
4. intent와 confidence를 반환한다.
"""

import json
import os

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


MODEL_PATH = "module_b/models/bert_intent_model"
LABEL_MAP_PATH = "module_b/label_map.json"

_model = None
_tokenizer = None
_id2label = None


def load_label_map():
    """
    label_map.json에서 id2label 정보를 불러온다.
    JSON에서는 key가 문자열로 저장되므로 문자열 key 기준으로 사용한다.
    """

    if not os.path.exists(LABEL_MAP_PATH):
        raise FileNotFoundError(
            "label_map.json을 찾을 수 없습니다. "
            "먼저 module_b/train_bert_intent.py를 실행해 주세요."
        )

    with open(LABEL_MAP_PATH, "r", encoding="utf-8") as file:
        label_map = json.load(file)

    return label_map["id2label"]


def load_intent_model():
    """
    학습된 BERT 의도 분류 모델과 tokenizer를 로드한다.
    한 번 로드한 뒤에는 전역 변수에 저장하여 재사용한다.
    """

    global _model, _tokenizer, _id2label

    if _model is None or _tokenizer is None or _id2label is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "학습된 BERT 모델을 찾을 수 없습니다. "
                "먼저 module_b/train_bert_intent.py를 실행해 주세요."
            )

        _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        _model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        _model.eval()
        _id2label = load_label_map()

    return _model, _tokenizer, _id2label


def predict_intent(text):
    """
    사용자 입력 문장의 intent를 예측한다.
    """

    model, tokenizer, id2label = load_intent_model()

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=64,
    )

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.softmax(outputs.logits, dim=1)
    confidence, predicted_class_id = torch.max(probabilities, dim=1)

    predicted_id = str(predicted_class_id.item())
    intent = id2label[predicted_id]

    return {
        "intent": intent,
        "confidence": round(confidence.item(), 4),
    }


if __name__ == "__main__":
    sample_text = "서울역에서 숙대입구역까지 막차 남았어?"
    result = predict_intent(sample_text)
    print(result)