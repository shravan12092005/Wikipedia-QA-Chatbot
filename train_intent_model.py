"""
train_intent_model.py
---------------------
Fine-tunes DistilBERT for 5-class intent detection.
Run this ONCE before launching the app:
    python train_intent_model.py

Model is saved to: models/intent_model/
"""

import json
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report

import torch
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)

# ── Config ──────────────────────────────────────────────────────────────────
BASE_MODEL   = "distilbert-base-uncased"
DATA_PATH    = os.path.join(os.path.dirname(__file__), "data", "intent_data.json")
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), "models", "intent_model")
NUM_LABELS   = 5
MAX_LEN      = 64
EPOCHS       = 12
BATCH_SIZE   = 8
SEED         = 42

INTENT_LABELS = {
    0: "greeting",
    1: "topic_request",
    2: "question_answering",
    3: "summarization",
    4: "farewell",
}

# ── Dataset ──────────────────────────────────────────────────────────────────
class IntentDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels    = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item


# ── Metrics ──────────────────────────────────────────────────────────────────
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc   = accuracy_score(labels, preds)
    f1    = f1_score(labels, preds, average="weighted")
    return {"accuracy": acc, "f1": f1}


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  DistilBERT Intent Classifier — Training")
    print("=" * 60)

    # 1. Load data
    print(f"\n📂 Loading data from: {DATA_PATH}")
    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    texts  = [item["text"]  for item in data]
    labels = [item["label"] for item in data]
    print(f"   Total samples: {len(texts)}")
    for lbl, name in INTENT_LABELS.items():
        cnt = labels.count(lbl)
        print(f"   [{lbl}] {name}: {cnt} samples")

    # 2. Train / val split
    X_train, X_val, y_train, y_val = train_test_split(
        texts, labels, test_size=0.2, random_state=SEED, stratify=labels
    )
    print(f"\n✂️  Train: {len(X_train)}  |  Val: {len(X_val)}")

    # 3. Tokenize
    print(f"\n🔤 Loading tokenizer: {BASE_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    train_enc = tokenizer(X_train, padding=True, truncation=True, max_length=MAX_LEN)
    val_enc   = tokenizer(X_val,   padding=True, truncation=True, max_length=MAX_LEN)

    train_dataset = IntentDataset(train_enc, y_train)
    val_dataset   = IntentDataset(val_enc,   y_val)

    # 4. Load model
    print(f"\n🤖 Loading model: {BASE_MODEL} (num_labels={NUM_LABELS})")
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=NUM_LABELS,
        id2label=INTENT_LABELS,
        label2id={v: k for k, v in INTENT_LABELS.items()},
    )

    # 5. Training args
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        warmup_steps=10,
        weight_decay=0.01,
        logging_dir=os.path.join(OUTPUT_DIR, "logs"),
        logging_steps=5,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        save_total_limit=3,
        seed=SEED,
        report_to="none",
    )

    # 6. Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
    )

    print("\n🚀 Starting training...\n")
    trainer.train()

    # 7. Final evaluation
    print("\n📊 Final Evaluation:")
    results = trainer.evaluate()
    print(f"   Accuracy : {results['eval_accuracy']:.4f}")
    print(f"   F1 Score : {results['eval_f1']:.4f}")

    # Detailed report
    preds_output = trainer.predict(val_dataset)
    preds = np.argmax(preds_output.predictions, axis=-1)
    print("\nClassification Report:")
    print(classification_report(y_val, preds, target_names=list(INTENT_LABELS.values())))

    # 8. Save model + tokenizer
    print(f"\n💾 Saving model to: {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("\n✅ Training complete! Model saved successfully.")
    print(f"   Run 'python app.py' to launch the chatbot.\n")


if __name__ == "__main__":
    main()
