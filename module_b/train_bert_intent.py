"""
Module B - BERT 기반 의도 분류 모델 학습 코드

역할:
1. module_b/data/intent_dataset.csv 파일을 읽는다.
2. text, intent 데이터를 이용해 KLUE-BERT 모델을 fine-tuning 한다.
3. 학습된 모델과 tokenizer를 module_b/models/bert_intent_model/에 저장한다.
"""

import json
import os

import numpy as np
import pandas as pd
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)


MODEL_NAME = "klue/bert-base"
DATA_PATH = "module_b/data/intent_dataset.csv"
SAVE_PATH = "module_b/models/bert_intent_model"
LABEL_MAP_PATH = "module_b/label_map.json"


def load_dataset():
    """
    의도 분류 데이터셋을 불러오고 기본 검증을 수행한다.
    """

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"데이터셋 파일을 찾을 수 없습니다: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    required_columns = {"text", "intent"}
    if not required_columns.issubset(df.columns):
        raise ValueError("intent_dataset.csv에는 text, intent 컬럼이 필요합니다.")

    df = df.dropna(subset=["text", "intent"])
    df["text"] = df["text"].astype(str).str.strip()
    df["intent"] = df["intent"].astype(str).str.strip()

    df = df[(df["text"] != "") & (df["intent"] != "")]

    return df


def build_label_maps(df):
    """
    intent 문자열 라벨을 숫자 라벨로 변환하기 위한 매핑을 생성한다.
    """

    labels = sorted(df["intent"].unique())

    label2id = {label: index for index, label in enumerate(labels)}
    id2label = {index: label for label, index in label2id.items()}

    return labels, label2id, id2label


def tokenize_dataset(train_df, test_df, tokenizer):
    """
    BERT 입력 형식에 맞게 문장을 토큰화한다.
    """

    train_dataset = Dataset.from_pandas(train_df[["text", "label"]])
    test_dataset = Dataset.from_pandas(test_df[["text", "label"]])

    def tokenize(batch):
        return tokenizer(
            batch["text"],
            padding="max_length",
            truncation=True,
            max_length=64,
        )

    train_dataset = train_dataset.map(tokenize, batched=True)
    test_dataset = test_dataset.map(tokenize, batched=True)

    return train_dataset, test_dataset


def compute_metrics(eval_pred):
    """
    학습 성능 평가 지표를 계산한다.
    """

    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)

    return {
        "accuracy": accuracy_score(labels, predictions),
        "f1": f1_score(labels, predictions, average="weighted"),
    }


def main():
    df = load_dataset()

    labels, label2id, id2label = build_label_maps(df)
    df["label"] = df["intent"].map(label2id)

    print("데이터셋 개수:", len(df))
    print("라벨 목록:", labels)
    print("라벨별 개수:")
    print(df["intent"].value_counts())

    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["label"],
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    train_dataset, test_dataset = tokenize_dataset(train_df, test_df, tokenizer)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(labels),
        id2label={str(key): value for key, value in id2label.items()},
        label2id=label2id,
    )

    training_args = TrainingArguments(
        output_dir="module_b/models/checkpoints",
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=5,
        weight_decay=0.01,
        logging_dir="module_b/models/logs",
        load_best_model_at_end=True,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics,
    )

    trainer.train()

    os.makedirs(SAVE_PATH, exist_ok=True)

    model.save_pretrained(SAVE_PATH)
    tokenizer.save_pretrained(SAVE_PATH)

    with open(LABEL_MAP_PATH, "w", encoding="utf-8") as file:
        json.dump(
            {
                "label2id": label2id,
                "id2label": id2label,
            },
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("BERT 의도 분류 모델 학습 완료")
    print(f"모델 저장 위치: {SAVE_PATH}")
    print(f"라벨 맵 저장 위치: {LABEL_MAP_PATH}")


if __name__ == "__main__":
    main()