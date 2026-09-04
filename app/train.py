from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report
)
from .features import FEATURES, CATEGORICAL
from data.generate import generate_dataset

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "risk_model.joblib"
DATA_PATH = ROOT / "data" / "transactions.csv"

def main():
    df = generate_dataset(20000, seed=42)
    df.to_csv(DATA_PATH, index=False)

    X = df[FEATURES + CATEGORICAL]
    y = df["fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL)
    ])

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=42
        ))
    ])

    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "precision": float(precision_score(y_test, pred)),
        "recall": float(recall_score(y_test, pred)),
        "f1": float(f1_score(y_test, pred)),
        "roc_auc": float(roc_auc_score(y_test, prob)),
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
        "test_size": len(y_test),
        "fraud_rate": float(y_test.mean()),
    }

    joblib.dump({"pipeline": model, "metrics": metrics}, MODEL_PATH)

    print("=== RiskShield evaluation (held-out test set) ===")
    print(f"Precision : {metrics['precision']:.3f}")
    print(f"Recall    : {metrics['recall']:.3f}")
    print(f"F1        : {metrics['f1']:.3f}")
    print(f"ROC-AUC   : {metrics['roc_auc']:.3f}")
    print("Confusion:", metrics["confusion_matrix"])
    print("Model:", MODEL_PATH)

if __name__ == "__main__":
    main()
