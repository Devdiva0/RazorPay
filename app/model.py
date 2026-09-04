from pathlib import Path
import joblib
import pandas as pd
from .features import feature_vector

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "risk_model.joblib"

def load_model():
    if not MODEL_PATH.exists():
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        from .train import main as train_main
        train_main()
    return joblib.load(MODEL_PATH)

def explain(model, frame: pd.DataFrame, probability: float) -> list[str]:
    pipe = model
    pre = pipe.named_steps["preprocessor"]
    clf = pipe.named_steps["classifier"]

    X = pre.transform(feature_vector(frame))
    names = pre.get_feature_names_out()

    if hasattr(X, "toarray"):
        X = X.toarray()

    contributions = X[0] * clf.coef_[0]
    ranked = sorted(zip(names, contributions), key=lambda x: abs(x[1]), reverse=True)

    reasons = []
    for name, value in ranked[:5]:
        if abs(value) < 0.03:
            continue
        clean = name.replace("num__", "").replace("cat__", "")
        direction = "increases" if value > 0 else "decreases"
        reasons.append(f"{clean} {direction} model risk")
    if probability >= 0.5:
        reasons.insert(0, f"Model estimates {probability:.1%} fraud probability")
    return reasons[:5]
