# RiskShield AI — AI Risk Manager

A defense-only transaction risk intelligence system built for the Razorpay AI Buildathon 2026 — Track 2: **AI Risk Manager**.

## Problem

Payment fraud is rarely one obvious rule. A transaction can look normal in isolation but become suspicious when combined with velocity, device changes, unusual amounts, failed attempts, or geographic/device anomalies.

RiskShield AI combines:

1. **Deterministic safety rules** for high-confidence signals.
2. **Machine learning risk scoring** for non-linear combinations of transaction signals.
3. **Explainability** so every flag has human-readable reasons.
4. **Cost-aware thresholding** so false positives are measured instead of hidden.
5. **Human-in-the-loop review** for ambiguous transactions.
6. **FastAPI inference API + Streamlit dashboard** for a working demo.

> This project is intentionally defense-only. It does not contain attack generation, evasion, credential theft, or fraud-enabling functionality.

## Buildathon alignment

The Track 2 brief asks for a working detector/verifier/auto-responder for a class of loss, with measured precision and recall on a held-out test set and an honest treatment of false-positive cost.

RiskShield focuses on **payment transaction fraud detection** and reports:
- Precision
- Recall
- F1
- ROC-AUC
- Confusion matrix
- False-positive count
- Estimated false-positive friction cost
- Review queue for borderline cases

## Architecture

```text
Synthetic / merchant transaction data
             |
             v
     Feature engineering
             |
       +-----+------+
       |            |
       v            v
 Safety rules    ML model
       |            |
       +-----+------+
             |
             v
      Composite risk score
             |
      +------+-------+
      |              |
   < 40 SAFE      >= 70 HIGH
      |              |
      |          block/review
      +------> 40-69 WATCH
                 |
                 v
          Explanation + audit log
```

## Risk score

The prototype uses a transparent hybrid score:

`final_score = 0.75 * ML_probability * 100 + 0.25 * rule_score`

A hard safety rule can force a high-risk decision. This is deliberately conservative for a fintech prototype.

Decision bands:
- **SAFE**: score < 40
- **WATCH**: 40–69.99
- **HIGH**: >= 70

The threshold is configurable in the dashboard.

## Dataset

The repository generates a fully synthetic dataset so no real payment/customer data is required.

Features include:
- transaction amount
- hour
- account age
- device age
- failed attempts in last 24h
- transactions in last hour
- transactions in last 24h
- distance from normal location
- new device
- international transaction
- merchant risk score
- prior chargebacks
- payment method
- fraud label

The data generator creates realistic correlations while keeping the fraud label hidden from inference.

## Quick start

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m app.train
uvicorn app.api:app --reload
```

In another terminal:

```bash
source .venv/bin/activate
streamlit run app/dashboard.py
```

Open:
- API docs: http://127.0.0.1:8000/docs
- Dashboard: http://localhost:8501

## API example

POST `/score`

```json
{
  "amount": 42500,
  "hour": 2,
  "account_age_days": 18,
  "device_age_days": 1,
  "failed_attempts_24h": 5,
  "txns_last_hour": 7,
  "txns_last_24h": 18,
  "distance_km": 840,
  "new_device": true,
  "international": false,
  "merchant_risk": 0.62,
  "prior_chargebacks": 1,
  "payment_method": "upi"
}
```

Response contains:
- risk score
- decision
- reasons
- rule hits
- model probability

## Evaluation methodology

The training script performs a stratified train/test split. The test set is never used to fit the model or choose individual transaction decisions.

For a real deployment, the next step would be a time-based split and calibration against production fraud/chargeback labels.

## Important limitations

This is a prototype, not a production fraud engine.

- Synthetic data does not represent Razorpay's real fraud distribution.
- Fraud labels are delayed/noisy in real systems.
- Attackers adapt, causing concept drift.
- Thresholds should be optimized against actual merchant/customer friction and loss.
- Production systems need feature freshness guarantees, privacy controls, model monitoring, rate limits, authentication, and rollback procedures.
- A model should assist risk operations, not become an unreviewable black box.

## Demo scenarios

### 1. Safe
Low amount, old account/device, normal velocity.

### 2. Watch
New device + elevated velocity + moderately unusual location.

### 3. High
Very high amount + new device + multiple failed attempts + velocity spike.

## Suggested 5-minute pitch

**0:00–0:40 — Problem**
"Fraud is not a single-rule problem. RiskShield combines behavioral signals into a measurable risk decision."

**0:40–1:30 — Product**
Show the dashboard, score a transaction, and open its explanation.

**1:30–2:30 — Technical**
Explain feature engineering → ML probability → deterministic rules → composite score → decision.

**2:30–3:30 — Evidence**
Show held-out precision, recall, F1, ROC-AUC and the false-positive cost panel.

**3:30–4:20 — Failure handling**
Show borderline transactions going to review rather than automatic blocking.

**4:20–5:00 — Judgment**
Explain why the model is not allowed to make every decision, what the synthetic-data limitation is, and how you would deploy it safely.

## Repository structure

```text
riskshield-ai/
├── app/
│   ├── api.py
│   ├── dashboard.py
│   ├── features.py
│   ├── model.py
│   ├── rules.py
│   └── train.py
├── data/
│   └── generate.py
├── models/
├── tests/
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```
