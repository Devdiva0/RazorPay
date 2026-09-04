from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .features import make_frame
from .model import load_model, explain
from .rules import rule_score

app = FastAPI(
    title="RiskShield AI",
    version="1.0.0",
    description="Defense-only transaction fraud risk scoring prototype."
)

class Transaction(BaseModel):
    amount: float = Field(gt=0)
    hour: int = Field(ge=0, le=23)
    account_age_days: float = Field(ge=0)
    device_age_days: float = Field(ge=0)
    failed_attempts_24h: int = Field(ge=0)
    txns_last_hour: int = Field(ge=0)
    txns_last_24h: int = Field(ge=0)
    distance_km: float = Field(ge=0)
    new_device: bool
    international: bool
    merchant_risk: float = Field(ge=0, le=1)
    prior_chargebacks: int = Field(ge=0)
    payment_method: Literal["upi", "card", "netbanking", "wallet"] = "upi"

_model = None

def get_model():
    global _model
    if _model is None:
        try:
            _model = load_model()["pipeline"]
        except FileNotFoundError as e:
            raise HTTPException(status_code=503, detail=str(e))
    return _model

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/score")
def score(t: Transaction):
    payload = t.model_dump()
    frame = make_frame(payload)
    model = get_model()

    probability = float(model.predict_proba(frame)[:, 1][0])
    rs, hits = rule_score(payload)

    final_score = min(100.0, 0.75 * probability * 100 + 0.25 * rs)

    # High-confidence safety floor: rules can force a review/high-risk state,
    # but rules never reduce model risk.
    if rs >= 70:
        final_score = max(final_score, 70.0)

    if final_score >= 70:
        decision = "HIGH"
        action = "BLOCK_OR_MANUAL_REVIEW"
    elif final_score >= 40:
        decision = "WATCH"
        action = "STEP_UP_VERIFICATION"
    else:
        decision = "SAFE"
        action = "ALLOW"

    reasons = explain(model, frame, probability)
    reasons.extend(h["reason"] for h in hits)
    reasons = list(dict.fromkeys(reasons))[:7]

    return {
        "risk_score": round(final_score, 2),
        "decision": decision,
        "recommended_action": action,
        "model_probability": round(probability, 4),
        "rule_score": round(rs, 2),
        "rule_hits": hits,
        "reasons": reasons,
        "audit": {
            "model": "logistic_regression_v1",
            "policy": "hybrid_ml_rules_v1",
            "human_review_required": decision != "SAFE"
        }
    }
