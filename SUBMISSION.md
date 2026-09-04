# Buildathon Submission Notes

## Project
RiskShield AI — Explainable Transaction Fraud Risk Manager

## One-line pitch
"RiskShield combines ML, deterministic fraud rules and human review to detect suspicious payment transactions while making false-positive cost visible."

## What to demo

1. Start dashboard.
2. Click **Safe** and score.
3. Click **Watch** and show step-up verification.
4. Click **High** and show risk reasons + rule hits.
5. Show held-out precision, recall, F1 and ROC-AUC.
6. Open the API docs.
7. Explain the architecture and limitations.

## What makes it more than a CRUD app?

The core product decision is risk classification under asymmetric cost:
- The model estimates probability.
- Rules capture high-confidence signals.
- Policy converts risk into bounded action.
- Explanations make the decision reviewable.
- Evaluation includes false positives, not only accuracy.

## Honest statement for the pitch

"These metrics are on synthetic data generated for the prototype. I would not claim they represent Razorpay production performance. My next validation step would be a time-based test on approved historical labels, with merchant-segment false-positive cost."

## Failure recovery to discuss

If the model service is unavailable:
- do not silently pretend a model score exists,
- return a service-unavailable response,
- keep deterministic policy available only if the business explicitly approves a safe degraded mode,
- log the failure for observability.

If a transaction is borderline:
- send it to verification/review instead of automatically blocking.

If model performance drifts:
- stop automatic threshold changes,
- alert risk operations,
- compare against a known-good model,
- roll back.

## Interview questions you should be ready for

### Why not accuracy?
Fraud is usually imbalanced. Accuracy can look high while missing many fraud cases. Precision and recall directly expose the trade-off.

### Why not an LLM?
Transaction risk scoring is structured numerical classification. An LLM is unnecessary for the core decision and can add cost/variance. AI should be used where it improves the workflow; deterministic/ML methods are preferable for this decision.

### How would you reduce false positives?
Calibrate probabilities, tune thresholds against business cost, segment by merchant/risk cohort, add better behavioral features, and route ambiguous cases to step-up verification.

### How would you prevent leakage?
Use time-based splits for production evaluation, ensure features only contain information available at transaction time, and freeze the test set.

### What happens when fraud patterns change?
Monitor drift, retrain with fresh labels, compare champion/challenger models, and use rollback/shadow deployment.

### What is the biggest weakness?
Synthetic data. It is useful for a reproducible demo but cannot establish real-world fraud performance.
