"""
Module B - 장소 추출 NER 모델 예측 코드

역할:
- 학습된 location_ner_model을 불러온다.
- 사용자 발화에서 출발지와 목적지 표면형을 추출한다.
- 표면형을 canonical 역명으로 변환한다.
- 예: "사울약에서 숙대입고까지 가고 싶어"
  → start="서울역", destination="숙대입구역"

사용:
from module_b.predict_location_ner import predict_locations
result = predict_locations("사울약에서 숙대입고까지 가고 싶어")
"""

import json
import os
import re
from pathlib import Path

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer


MODEL_PATH = Path("module_b/models/location_ner_model")
LABEL_MAP_PATH = Path("module_b/location_label_map.json")
SURFACE_MAP_PATH = Path("module_b/location_surface_map.json")

_model = None
_tokenizer = None
_id2label = None
_surface_map = None


PARTICLES = [
    "에서부터",
    "에서",
    "까지",
    "으로",
    "로",
    "부터",
]


def normalize_surface(value: str) -> str:
    if value is None:
        return ""
    return str(value).strip().replace(" ", "")


def split_attached_particles(token: str):
    """
    STT 결과에는 '사울약에서', '숙대입고까지'처럼 조사/어미가 붙어서 올 수 있다.
    학습 데이터처럼 장소 표면형과 조사를 분리하기 위해 간단히 후처리한다.
    """
    if not token:
        return []

    # 문장부호 제거
    token = token.strip()
    token = re.sub(r"[,.!?~]+$", "", token)

    if not token:
        return []

    for particle in PARTICLES:
        if token.endswith(particle) and len(token) > len(particle):
            stem = token[:-len(particle)]
            if stem:
                return [stem, particle]

    return [token]


def simple_tokenize(text: str):
    """
    NER 학습 데이터의 tokens와 최대한 비슷하게 맞추는 간단 토크나이저.
    공백 기준으로 나눈 뒤 조사 결합을 한 번 더 분리한다.
    """
    if not text:
        return []

    raw_tokens = str(text).strip().split()
    tokens = []

    for raw_token in raw_tokens:
        tokens.extend(split_attached_particles(raw_token))

    return tokens


def load_label_map():
    if not LABEL_MAP_PATH.exists():
        raise FileNotFoundError(
            f"location_label_map.json을 찾을 수 없습니다: {LABEL_MAP_PATH}. "
            "먼저 module_b/train_location_ner.py를 실행해 주세요."
        )

    with LABEL_MAP_PATH.open("r", encoding="utf-8") as file:
        label_map = json.load(file)

    return {int(key): value for key, value in label_map["id2label"].items()}


def load_surface_map():
    if not SURFACE_MAP_PATH.exists():
        return {"start": {}, "destination": {}, "all": {}}

    with SURFACE_MAP_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_location_model():
    global _model, _tokenizer, _id2label, _surface_map

    if _model is None or _tokenizer is None or _id2label is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"학습된 장소 추출 모델을 찾을 수 없습니다: {MODEL_PATH}. "
                "먼저 Colab에서 train_location_ner.py를 실행하고 모델을 저장해 주세요."
            )

        _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        _model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)
        _model.eval()
        _id2label = load_label_map()
        _surface_map = load_surface_map()

    return _model, _tokenizer, _id2label, _surface_map


def canonicalize_surface(surface: str, role: str, surface_map: dict):
    """
    모델이 추출한 표면형을 실제 역명으로 변환한다.
    role: start 또는 destination
    """
    if not surface:
        return None

    surface = surface.strip()
    compact = normalize_surface(surface)

    role_map = surface_map.get(role, {})
    all_map = surface_map.get("all", {})

    candidates = [
        surface,
        compact,
    ]

    for candidate in candidates:
        if candidate in role_map:
            return role_map[candidate]
        if candidate in all_map:
            return all_map[candidate]

    # 데이터셋 매핑에 없지만 이미 정상 역명처럼 보이면 그대로 반환
    if surface.endswith("역"):
        return surface

    return None


def extract_spans(tokens, labels, confidences):
    spans = []
    current_role = None
    current_tokens = []
    current_confidences = []

    def flush():
        nonlocal current_role, current_tokens, current_confidences

        if current_role and current_tokens:
            spans.append({
                "role": current_role,
                "surface": " ".join(current_tokens).strip(),
                "confidence": (
                    sum(current_confidences) / len(current_confidences)
                    if current_confidences else 0.0
                ),
            })

        current_role = None
        current_tokens = []
        current_confidences = []

    for token, label, confidence in zip(tokens, labels, confidences):
        if label == "B-START":
            flush()
            current_role = "start"
            current_tokens = [token]
            current_confidences = [confidence]

        elif label == "I-START":
            if current_role == "start":
                current_tokens.append(token)
                current_confidences.append(confidence)
            else:
                flush()

        elif label == "B-DEST":
            flush()
            current_role = "destination"
            current_tokens = [token]
            current_confidences = [confidence]

        elif label == "I-DEST":
            if current_role == "destination":
                current_tokens.append(token)
                current_confidences.append(confidence)
            else:
                flush()

        else:
            flush()

    flush()
    return spans


def predict_locations(text: str, confidence_threshold: float = 0.35):
    """
    사용자 입력 문장에서 출발지/목적지를 예측한다.

    반환 예:
    {
      "start": "서울역",
      "destination": "숙대입구역",
      "start_surface": "사울약",
      "destination_surface": "숙대입고",
      "confidence": 0.91,
      "method": "location_ner"
    }

    모델이 없거나 예측 실패 시 None을 반환한다.
    """
    try:
        model, tokenizer, id2label, surface_map = load_location_model()
    except Exception:
        return None

    tokens = simple_tokenize(text)

    if not tokens:
        return None

    inputs = tokenizer(
        tokens,
        is_split_into_words=True,
        return_tensors="pt",
        truncation=True,
        max_length=96,
    )

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.softmax(outputs.logits, dim=-1)[0]
    predicted_ids = torch.argmax(probabilities, dim=-1).tolist()

    word_ids = inputs.word_ids(batch_index=0)

    word_predictions = {}
    word_confidences = {}

    for token_index, word_id in enumerate(word_ids):
        if word_id is None:
            continue

        # 각 word의 첫 subtoken 예측만 사용한다.
        if word_id not in word_predictions:
            pred_id = int(predicted_ids[token_index])
            confidence = float(probabilities[token_index][pred_id].item())
            word_predictions[word_id] = id2label[pred_id]
            word_confidences[word_id] = confidence

    labels = []
    confidences = []

    for word_index in range(len(tokens)):
        labels.append(word_predictions.get(word_index, "O"))
        confidences.append(word_confidences.get(word_index, 0.0))

    spans = extract_spans(tokens, labels, confidences)

    start_surface = None
    destination_surface = None
    start_confidence = 0.0
    destination_confidence = 0.0

    for span in spans:
        if span["confidence"] < confidence_threshold:
            continue

        if span["role"] == "start" and start_surface is None:
            start_surface = span["surface"]
            start_confidence = span["confidence"]

        elif span["role"] == "destination" and destination_surface is None:
            destination_surface = span["surface"]
            destination_confidence = span["confidence"]

    start = canonicalize_surface(start_surface, "start", surface_map)
    destination = canonicalize_surface(destination_surface, "destination", surface_map)

    if start is None and destination is None:
        return None

    span_confidences = [
        value for value in [start_confidence, destination_confidence] if value > 0
    ]

    return {
        "start": start,
        "destination": destination,
        "start_surface": start_surface,
        "destination_surface": destination_surface,
        "confidence": round(
            sum(span_confidences) / len(span_confidences),
            4
        ) if span_confidences else None,
        "method": "location_ner",
        "tokens": tokens,
        "predicted_labels": labels,
    }


if __name__ == "__main__":
    samples = [
        "사울약에서 숙대입고까지 가고 싶어",
        "서울약 에서 숙대 입고 여기 까지 가고 싶어요",
        "홍대 입구 약에서 사울역까지 가는 길 알려줘",
    ]

    for sample in samples:
        print("입력:", sample)
        print(predict_locations(sample))
        print("-" * 50)
