from app.rules import evaluate_rules, rule_score

def test_high_value_new_device():
    t = {
        "amount": 60000, "hour": 2, "account_age_days": 10,
        "device_age_days": 1, "failed_attempts_24h": 0,
        "txns_last_hour": 1, "txns_last_24h": 3, "distance_km": 10,
        "new_device": True, "international": False, "merchant_risk": 0.2,
        "prior_chargebacks": 0, "payment_method": "upi"
    }
    score, hits = rule_score(t)
    assert score >= 30
    assert any(h["name"] == "high_value_new_device" for h in hits)
