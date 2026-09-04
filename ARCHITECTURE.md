# Architecture & Design Decisions

## 1. Why hybrid ML + rules?

A pure model can be hard to audit. A pure rules engine misses combinations of weak signals.

RiskShield therefore uses:
- ML for probabilistic pattern detection.
- Rules for high-confidence, easy-to-explain risk signals.
- A deterministic policy layer for the final action.

## 2. Why logistic regression?

For a buildathon prototype, the priority is measurable behavior and explainability rather than using the largest possible model.

Logistic regression:
- is fast enough for synchronous scoring,
- provides calibrated-ish probabilities after proper production calibration,
- exposes feature coefficients,
- is easy to reproduce,
- provides a clean baseline against which tree/boosting models can later be compared.

## 3. Why human review?

A risk system should not blindly block every uncertain transaction.

The middle band is routed to:
`STEP_UP_VERIFICATION`

High-risk transactions are:
`BLOCK_OR_MANUAL_REVIEW`

A production system would connect these decisions to merchant/customer verification workflows.

## 4. False-positive cost

Suppose a legitimate transaction is incorrectly blocked.

Example prototype assumption:
- false-positive friction = ₹500
- false negative loss = ₹5,000

Expected cost can be estimated as:

`FP × 500 + FN × 5000`

The exact values are illustrative and must be replaced with merchant-specific economics.

## 5. Production evolution

1. Replace synthetic data with consented/approved historical labels.
2. Use time-based validation.
3. Add probability calibration.
4. Compare logistic regression against gradient-boosted trees.
5. Add feature freshness checks.
6. Add model drift and data drift monitoring.
7. Add shadow deployment and rollback.
8. Add analyst feedback labels.
9. Add privacy-preserving feature stores and access controls.
10. Continuously evaluate false-positive cost by merchant segment.
