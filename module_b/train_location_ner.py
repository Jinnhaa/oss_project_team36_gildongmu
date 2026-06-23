"""
Module B - 장소 추출 NER 모델 학습 코드

목적:
- module_b/data/location_ner_dataset.jsonl 파일을 읽는다.
- tokens/tags 기반으로 KLUE-BERT Token Classification 모델을 학습한다.
- 출발지 START, 목적지 DEST를 토큰 단위로 추출하는 모델을 만든다.
- 학습된 모델은 module_b/models/location_ner_model/에 저장한다.

데이터셋 형식(JSONL):
{
  "text": "사울약 에서 숙대입고 까지 가고 싶어요",
  "tokens": ["사울약", "에서", "숙대입고", "까지", "가고", "싶어요"],
  "tags": ["B-START", "O", "B-DEST", "O", "O", "O"],
  "start": "서울역",
  "destination": "숙대입구역",
  "start_surface": "사울약",
  "destination_surface": "숙대입고",
  "split": "train"
}

Colab 실행:
python3 module_b/train_location_ner.py
"""

import json
import os
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from datasets import Dataset, DatasetDict
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
    Trainer,
    TrainingArguments,
)

try:
    from seqeval.metrics import accuracy_score, f1_score, precision_score, recall_score
    SEQEVAL_AVAILABLE = True
except ImportError:
    SEQEVAL_AVAILABLE = False


MODEL_NAME = "klue/bert-base"
DATA_PATH = Path("module_b/data/location_ner_dataset.jsonl")
SAVE_PATH = Path("module_b/models/location_ner_model")
LABEL_MAP_PATH = Path("module_b/location_label_map.json")
SURFACE_MAP_PATH = Path("module_b/location_surface_map.json")

LABELS = ["O", "B-START", "I-START", "B-DEST", "I-DEST"]
LABEL2ID = {label: idx for idx, label in enumerate(LABELS)}
ID2LABEL = {idx: label for label, idx in LABEL2ID.items()}


def normalize_surface(value: str) -> str:
    """표면형 매핑용 정규화. 공백 차이로 인한 미매칭을 줄인다."""
    if value is None:
        return ""
    return str(value).strip().replace(" ", "")


def load_jsonl_dataset():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"장소 추출 데이터셋을 찾을 수 없습니다: {DATA_PATH}")

    rows = []
    with DATA_PATH.open("r", encoding="utf-8") as file:
        for line_no, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue

            item = json.loads(line)
            tokens = item.get("tokens", [])
            tags = item.get("tags", [])

            if not tokens or not tags:
                raise ValueError(f"{line_no}번째 행에 tokens/tags가 없습니다.")

            if len(tokens) != len(tags):
                raise ValueError(
                    f"{line_no}번째 행 tokens/tags 길이 불일치: "
                    f"{len(tokens)} != {len(tags)}"
                )

            for tag in tags:
                if tag not in LABEL2ID:
                    raise ValueError(f"{line_no}번째 행에 알 수 없는 태그가 있습니다: {tag}")

            split = item.get("split", "train")
            if split not in {"train", "valid", "test"}:
                split = "train"

            rows.append({
                "text": item.get("text", " ".join(tokens)),
                "tokens": tokens,
                "tags": tags,
                "labels": [LABEL2ID[tag] for tag in tags],
                "start": item.get("start"),
                "destination": item.get("destination"),
                "start_surface": item.get("start_surface"),
                "destination_surface": item.get("destination_surface"),
                "split": split,
            })

    if not rows:
        raise ValueError("데이터셋이 비어 있습니다.")

    return rows


def build_surface_map(rows):
    """
    NER 모델은 표면형을 추출한다.
    예: 사울약, 서울약, 서울력
    이 표면형을 실제 canonical 역명으로 바꾸기 위한 매핑을 데이터셋에서 만든다.
    """
    start_counter = defaultdict(Counter)
    dest_counter = defaultdict(Counter)

    for row in rows:
        start = row.get("start")
        destination = row.get("destination")
        start_surface = row.get("start_surface")
        destination_surface = row.get("destination_surface")

        if start and start_surface:
            start_counter[normalize_surface(start_surface)][start] += 1
            start_counter[str(start_surface).strip()][start] += 1

        if destination and destination_surface:
            dest_counter[normalize_surface(destination_surface)][destination] += 1
            dest_counter[str(destination_surface).strip()][destination] += 1

    def most_common_map(counter_dict):
        result = {}
        for surface, counter in counter_dict.items():
            if not surface:
                continue
            canonical, count = counter.most_common(1)[0]
            result[surface] = canonical
        return result

    surface_map = {
        "start": most_common_map(start_counter),
        "destination": most_common_map(dest_counter),
        "all": {},
    }

    # start/destination 양쪽에서 모두 쓸 수 있게 통합 맵도 만든다.
    for key in ["start", "destination"]:
        for surface, canonical in surface_map[key].items():
            surface_map["all"][surface] = canonical

    return surface_map


def split_dataset(rows):
    train_rows = [row for row in rows if row["split"] == "train"]
    valid_rows = [row for row in rows if row["split"] == "valid"]
    test_rows = [row for row in rows if row["split"] == "test"]

    # split 컬럼이 없거나 한쪽이 비어 있는 경우 안전 fallback
    if not train_rows or not valid_rows:
        rng = np.random.default_rng(42)
        shuffled = list(rows)
        rng.shuffle(shuffled)

        n = len(shuffled)
        train_end = int(n * 0.8)
        valid_end = int(n * 0.9)

        train_rows = shuffled[:train_end]
        valid_rows = shuffled[train_end:valid_end]
        test_rows = shuffled[valid_end:]

    return DatasetDict({
        "train": Dataset.from_list(train_rows),
        "validation": Dataset.from_list(valid_rows),
        "test": Dataset.from_list(test_rows),
    })


def tokenize_and_align_labels(dataset, tokenizer):
    def tokenize_batch(batch):
        tokenized = tokenizer(
            batch["tokens"],
            is_split_into_words=True,
            truncation=True,
            padding=False,
            max_length=96,
        )

        aligned_labels = []

        for batch_index, labels in enumerate(batch["labels"]):
            word_ids = tokenized.word_ids(batch_index=batch_index)
            previous_word_id = None
            label_ids = []

            for word_id in word_ids:
                if word_id is None:
                    label_ids.append(-100)
                elif word_id != previous_word_id:
                    label_ids.append(labels[word_id])
                else:
                    # 같은 단어가 subword로 쪼개진 경우
                    # B- 라벨은 I- 라벨로 바꿔 이어붙인다.
                    label = labels[word_id]
                    label_name = ID2LABEL[label]

                    if label_name == "B-START":
                        label = LABEL2ID["I-START"]
                    elif label_name == "B-DEST":
                        label = LABEL2ID["I-DEST"]

                    label_ids.append(label)

                previous_word_id = word_id

            aligned_labels.append(label_ids)

        tokenized["labels"] = aligned_labels
        return tokenized

    return dataset.map(tokenize_batch, batched=True)


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)

    true_predictions = []
    true_labels = []

    for prediction, label in zip(predictions, labels):
        pred_labels = []
        gold_labels = []

        for pred_id, label_id in zip(prediction, label):
            if label_id == -100:
                continue
            pred_labels.append(ID2LABEL[int(pred_id)])
            gold_labels.append(ID2LABEL[int(label_id)])

        true_predictions.append(pred_labels)
        true_labels.append(gold_labels)

    if SEQEVAL_AVAILABLE:
        return {
            "precision": precision_score(true_labels, true_predictions),
            "recall": recall_score(true_labels, true_predictions),
            "f1": f1_score(true_labels, true_predictions),
            "accuracy": accuracy_score(true_labels, true_predictions),
        }

    # seqeval이 없을 때 fallback
    total = 0
    correct = 0

    for gold_seq, pred_seq in zip(true_labels, true_predictions):
        for gold, pred in zip(gold_seq, pred_seq):
            total += 1
            if gold == pred:
                correct += 1

    return {"token_accuracy": correct / total if total else 0.0}


def main():
    rows = load_jsonl_dataset()
    surface_map = build_surface_map(rows)
    dataset = split_dataset(rows)

    print("장소 추출 NER 데이터셋 로드 완료")
    print("train:", len(dataset["train"]))
    print("valid:", len(dataset["validation"]))
    print("test :", len(dataset["test"]))
    print("라벨:", LABELS)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenized_dataset = tokenize_and_align_labels(dataset, tokenizer)

    model = AutoModelForTokenClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(LABELS),
        id2label={str(idx): label for idx, label in ID2LABEL.items()},
        label2id=LABEL2ID,
    )

    data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

    training_args = TrainingArguments(
        output_dir="module_b/models/location_ner_checkpoints",
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=5,
        weight_decay=0.01,
        logging_dir="module_b/models/location_ner_logs",
        load_best_model_at_end=True,
        metric_for_best_model="f1" if SEQEVAL_AVAILABLE else "token_accuracy",
        greater_is_better=True,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    trainer.train()

    print("검증 데이터 평가:")
    print(trainer.evaluate(tokenized_dataset["validation"]))

    print("테스트 데이터 평가:")
    print(trainer.evaluate(tokenized_dataset["test"]))

    SAVE_PATH.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(SAVE_PATH)
    tokenizer.save_pretrained(SAVE_PATH)

    with LABEL_MAP_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            {
                "label2id": LABEL2ID,
                "id2label": {str(k): v for k, v in ID2LABEL.items()},
            },
            file,
            ensure_ascii=False,
            indent=2,
        )

    with SURFACE_MAP_PATH.open("w", encoding="utf-8") as file:
        json.dump(surface_map, file, ensure_ascii=False, indent=2)

    print("장소 추출 NER 모델 학습 완료")
    print(f"모델 저장 위치: {SAVE_PATH}")
    print(f"라벨 맵 저장 위치: {LABEL_MAP_PATH}")
    print(f"표면형 매핑 저장 위치: {SURFACE_MAP_PATH}")


if __name__ == "__main__":
    main()
