def evaluate_rules(t: dict) -> list[dict]:
    hits = []

    if t["amount"] >= 50000 and t["new_device"]:
        hits.append({"name": "high_value_new_device", "score": 30,
                     "reason": "High-value payment from a newly seen device."})

    if t["failed_attempts_24h"] >= 4:
        hits.append({"name": "failed_attempt_velocity", "score": 22,
                     "reason": "Multiple failed payment attempts in 24 hours."})

    if t["txns_last_hour"] >= 6:
        hits.append({"name": "hourly_velocity", "score": 20,
                     "reason": "Unusually high transaction velocity in one hour."})

    if t["distance_km"] >= 700 and t["new_device"]:
        hits.append({"name": "location_device_mismatch", "score": 24,
                     "reason": "Large location deviation combined with a new device."})

    if t["prior_chargebacks"] >= 2 and t["amount"] >= 20000:
        hits.append({"name": "prior_chargeback_history", "score": 18,
                     "reason": "Prior chargebacks combined with a high-value payment."})

    if t["international"] and t["account_age_days"] < 14:
        hits.append({"name": "new_account_international", "score": 20,
                     "reason": "New account attempting an international payment."})

    return hits

def rule_score(t: dict) -> tuple[float, list[dict]]:
    hits = evaluate_rules(t)
    score = min(100.0, sum(h["score"] for h in hits))
    return score, hits
