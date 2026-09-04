from pathlib import Path
import numpy as np
import pandas as pd

def generate_dataset(n=20000, seed=42):
    rng = np.random.default_rng(seed)

    amount = np.exp(rng.normal(7.0, 1.0, n)).clip(50, 250000)
    hour = rng.integers(0, 24, n)
    account_age = rng.exponential(180, n).clip(1, 2500)
    device_age = rng.exponential(90, n).clip(1, 1000)
    failed = rng.poisson(0.7, n)
    tx_hour = rng.poisson(1.8, n)
    tx_day = (tx_hour * rng.uniform(3, 8, n)).clip(1, 80)
    distance = rng.exponential(80, n)
    new_device = (device_age < 7).astype(int)
    international = rng.binomial(1, 0.12, n)
    merchant_risk = rng.beta(2, 7, n)
    prior_chargebacks = rng.poisson(0.18, n).clip(0, 5)
    methods = rng.choice(["upi", "card", "netbanking", "wallet"], n,
                         p=[0.55, 0.28, 0.12, 0.05])

    # Hidden synthetic fraud-generating process.
    logit = (
        -4.8
        + 0.000010 * amount
        + 0.28 * failed
        + 0.18 * tx_hour
        + 0.018 * distance
        + 1.1 * new_device
        + 0.9 * international
        + 2.2 * merchant_risk
        + 0.55 * prior_chargebacks
        + 0.8 * (new_device * (distance > 500))
        + 0.6 * (account_age < 14)
        + 0.7 * (tx_hour >= 6)
    )
    p = 1 / (1 + np.exp(-logit))
    fraud = rng.binomial(1, p)

    return pd.DataFrame({
        "amount": amount.round(2),
        "hour": hour,
        "account_age_days": account_age.round(1),
        "device_age_days": device_age.round(1),
        "failed_attempts_24h": failed,
        "txns_last_hour": tx_hour,
        "txns_last_24h": tx_day.round().astype(int),
        "distance_km": distance.round(1),
        "new_device": new_device,
        "international": international,
        "merchant_risk": merchant_risk.round(3),
        "prior_chargebacks": prior_chargebacks,
        "payment_method": methods,
        "fraud": fraud,
    })

if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "transactions.csv"
    generate_dataset().to_csv(out, index=False)
    print(out)
