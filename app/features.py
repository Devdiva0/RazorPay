import pandas as pd

FEATURES = [
    "amount",
    "hour",
    "account_age_days",
    "device_age_days",
    "failed_attempts_24h",
    "txns_last_hour",
    "txns_last_24h",
    "distance_km",
    "new_device",
    "international",
    "merchant_risk",
    "prior_chargebacks",
]

CATEGORICAL = ["payment_method"]

def make_frame(payload: dict) -> pd.DataFrame:
    row = {k: payload[k] for k in FEATURES}
    row["new_device"] = int(bool(row["new_device"]))
    row["international"] = int(bool(row["international"]))
    row["payment_method"] = payload.get("payment_method", "upi")
    return pd.DataFrame([row])

def feature_vector(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[FEATURES + CATEGORICAL].copy()
