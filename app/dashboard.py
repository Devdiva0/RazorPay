import json
from pathlib import Path
import requests
import streamlit as st
import pandas as pd
import joblib

# Page Configuration
st.set_page_config(
    page_title="RiskShield AI — Razorpay Risk Manager",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Razorpay Fintech Theme
st.markdown("""
<style>
    /* Main Background & Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    
    /* Header Container */
    .header-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    
    .header-title {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .header-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 6px;
    }
    
    /* Card Styles */
    .risk-card {
        background-color: #1e293b;
        border-radius: 12px;
        border: 1px solid #334155;
        padding: 20px;
        margin-bottom: 16px;
    }
    
    /* Badge Styling */
    .badge-safe {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid #10b981;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
    }
    
    .badge-watch {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid #f59e0b;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
    }
    
    .badge-high {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid #ef4444;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
    }
    
    /* Score Metric Display */
    .metric-value {
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1;
    }
    
    /* Presets buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    /* Custom Dividers */
    hr {
        border-color: #334155;
    }
</style>
""", unsafe_allow_html=True)

# Top Banner
st.markdown("""
<div class="header-box">
    <div class="header-title">🛡️ RiskShield AI <span style="font-size: 0.9rem; background: #2563eb; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 600;">Razorpay Track 2</span></div>
    <div class="header-subtitle">Real-time Transaction Fraud Intelligence, Deterministic Rule Checking & Explainable AI Engine</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Config
st.sidebar.markdown("### ⚙️ Engine Configuration")
API_URL = st.sidebar.text_input("Backend API Endpoint", "http://127.0.0.1:8000")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Decision Policy")
st.sidebar.markdown("""
- 🟢 **SAFE**: Score `< 40` (Auto-Approve)
- 🟡 **WATCH**: Score `40 - 69.99` (Human Review)
- 🔴 **HIGH**: Score `≥ 70` (Auto-Block)
""")
st.sidebar.markdown("---")
st.sidebar.caption("Razorpay AI Buildathon 2026 Prototype")

# Main Navigation Tabs
tab1, tab2, tab3 = st.tabs(["⚡ Real-Time Transaction Evaluator", "📊 Model Metrics & Cost Evaluation", "🕵️ Human Review Queue"])

# Initialize Session State for Form Values
if "preset_data" not in st.session_state:
    st.session_state.preset_data = {
        "amount": 2500.0, "hour": 14, "account_age": 240.0, "device_age": 120.0,
        "failed": 0, "tx_hour": 1, "tx_day": 4, "distance": 10.0,
        "new_device": False, "international": False, "merchant_risk": 0.15,
        "chargebacks": 0, "method": "upi"
    }

def set_preset(preset_type):
    if preset_type == "safe":
        st.session_state.preset_data = {
            "amount": 1200.0, "hour": 14, "account_age": 500.0, "device_age": 180.0,
            "failed": 0, "tx_hour": 1, "tx_day": 3, "distance": 5.0,
            "new_device": False, "international": False, "merchant_risk": 0.08,
            "chargebacks": 0, "method": "upi"
        }
    elif preset_type == "watch":
        st.session_state.preset_data = {
            "amount": 18500.0, "hour": 23, "account_age": 45.0, "device_age": 3.0,
            "failed": 2, "tx_hour": 5, "tx_day": 14, "distance": 450.0,
            "new_device": True, "international": False, "merchant_risk": 0.40,
            "chargebacks": 1, "method": "card"
        }
    elif preset_type == "high":
        st.session_state.preset_data = {
            "amount": 95000.0, "hour": 2, "account_age": 5.0, "device_age": 1.0,
            "failed": 6, "tx_hour": 9, "tx_day": 28, "distance": 1200.0,
            "new_device": True, "international": True, "merchant_risk": 0.85,
            "chargebacks": 2, "method": "upi"
        }

# TAB 1: REAL-TIME EVALUATOR
with tab1:
    st.markdown("### 🎛️ Demo Scenarios (One-Touch Presets)")
    p1, p2, p3 = st.columns(3)
    with p1:
        st.button("🟢 Safe Low-Risk Transaction", use_container_width=True, on_click=set_preset, args=("safe",))
    with p2:
        st.button("🟡 Borderline Watch Scenario", use_container_width=True, on_click=set_preset, args=("watch",))
    with p3:
        st.button("🔴 High-Risk Fraud Alert", use_container_width=True, on_click=set_preset, args=("high",))

    st.markdown("---")
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("#### 💳 Transaction Details")
        amount = st.number_input("Transaction Amount (₹)", 10.0, 500000.0, float(st.session_state.preset_data["amount"]), step=500.0)
        method = st.selectbox("Payment Method", ["upi", "card", "netbanking", "wallet"], index=["upi", "card", "netbanking", "wallet"].index(st.session_state.preset_data["method"]))
        hour = st.slider("Time of Day (Hour 0-23)", 0, 23, int(st.session_state.preset_data["hour"]))
        distance = st.number_input("Distance from Usual Location (km)", 0.0, 15000.0, float(st.session_state.preset_data["distance"]))

        st.markdown("#### ⏱️ Velocity & Attempts")
        v1, v2, v3 = st.columns(3)
        with v1:
            failed = st.number_input("Failed PIN/Attempts (24h)", 0, 30, int(st.session_state.preset_data["failed"]))
        with v2:
            tx_hour = st.number_input("Txns in Last Hour", 0, 50, int(st.session_state.preset_data["tx_hour"]))
        with v3:
            tx_day = st.number_input("Txns in Last 24h", 0, 200, int(st.session_state.preset_data["tx_day"]))

    with col_right:
        st.markdown("#### 📱 Device & Account History")
        a1, a2 = st.columns(2)
        with a1:
            account_age = st.number_input("Account Age (Days)", 0.0, 3650.0, float(st.session_state.preset_data["account_age"]))
        with a2:
            device_age = st.number_input("Device Age (Days)", 0.0, 1800.0, float(st.session_state.preset_data["device_age"]))

        new_device = st.checkbox("New Unrecognized Device", value=bool(st.session_state.preset_data["new_device"]))
        international = st.checkbox("Cross-border / International Transaction", value=bool(st.session_state.preset_data["international"]))

        st.markdown("#### 🏬 Merchant & Risk Profile")
        merchant_risk = st.slider("Merchant Category Risk Score", 0.0, 1.0, float(st.session_state.preset_data["merchant_risk"]))
        chargebacks = st.number_input("Prior Account Chargebacks", 0, 20, int(st.session_state.preset_data["chargebacks"]))

    st.markdown("<br>", unsafe_allow_html=True)
    score_btn = st.button("🚀 Analyze & Score Transaction Risk", type="primary", use_container_width=True)

    if score_btn:
        payload = {
            "amount": amount, "hour": hour, "account_age_days": account_age,
            "device_age_days": device_age, "failed_attempts_24h": failed,
            "txns_last_hour": tx_hour, "txns_last_24h": tx_day,
            "distance_km": distance, "new_device": new_device,
            "international": international, "merchant_risk": merchant_risk,
            "prior_chargebacks": chargebacks, "payment_method": method
        }

        res = None
        try:
            with st.spinner("Connecting to Risk Engine..."):
                r = requests.post(f"{API_URL}/score", json=payload, timeout=3)
                r.raise_for_status()
                res = r.json()
        except Exception as err:
            # Fallback to direct Python engine (ideal for standalone Streamlit Cloud)
            try:
                from app.features import make_frame
                from app.model import load_model, explain
                from app.rules import rule_score

                frame = make_frame(payload)
                model = load_model()["pipeline"]
                probability = float(model.predict_proba(frame)[:, 1][0])
                rs, hits = rule_score(payload)

                final_score = min(100.0, 0.75 * probability * 100 + 0.25 * rs)
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

                res = {
                    "risk_score": round(final_score, 2),
                    "decision": decision,
                    "recommended_action": action,
                    "model_probability": round(probability, 4),
                    "rule_score": round(rs, 2),
                    "rule_hits": hits,
                    "reasons": reasons,
                    "audit": {
                        "model": "logistic_regression_v1",
                        "policy": "hybrid_ml_rules_v1 (In-Memory Engine)",
                        "human_review_required": decision != "SAFE"
                    }
                }
            except Exception as e2:
                st.error(f"❌ Error reaching Risk Engine: {err} | Fallback Error: {e2}")

        if res:
            st.markdown("---")
            st.markdown("## 🔍 Risk Score Result")

            # Score Cards Layout
            m1, m2, m3 = st.columns(3)

            score = res["risk_score"]
            decision = res["decision"]
            badge_class = "badge-safe" if decision == "SAFE" else ("badge-watch" if decision == "WATCH" else "badge-high")
            decision_emoji = "🟢" if decision == "SAFE" else ("🟡" if decision == "WATCH" else "🔴")

            with m1:
                st.markdown(f"""
                <div class="risk-card" style="text-align: center;">
                    <div style="color: #94a3b8; font-size: 0.9rem; font-weight: 600;">COMPOSITE RISK SCORE</div>
                    <div class="metric-value" style="color: {'#34d399' if score < 40 else ('#fbbf24' if score < 70 else '#f87171')}; font-size: 3.5rem; margin: 10px 0;">{score:.1f}<span style="font-size: 1.5rem; color: #64748b;">/100</span></div>
                    <div class="{badge_class}">{decision_emoji} {decision}</div>
                </div>
                """, unsafe_allow_html=True)

            with m2:
                ml_prob = res["model_probability"] * 100
                st.markdown(f"""
                <div class="risk-card" style="text-align: center;">
                    <div style="color: #94a3b8; font-size: 0.9rem; font-weight: 600;">AI ML PROBABILITY</div>
                    <div class="metric-value" style="color: #60a5fa; font-size: 3.5rem; margin: 10px 0;">{ml_prob:.1f}%</div>
                    <div style="color: #cbd5e1; font-weight: 500;">Predictive ML Model</div>
                </div>
                """, unsafe_allow_html=True)

            with m3:
                rule_score = res["rule_score"]
                st.markdown(f"""
                <div class="risk-card" style="text-align: center;">
                    <div style="color: #94a3b8; font-size: 0.9rem; font-weight: 600;">SAFETY RULE SCORE</div>
                    <div class="metric-value" style="color: #a78bfa; font-size: 3.5rem; margin: 10px 0;">{rule_score:.0f}</div>
                    <div style="color: #cbd5e1; font-weight: 500;">{len(res['rule_hits'])} Rules Triggered</div>
                </div>
                """, unsafe_allow_html=True)

            st.success(f"📌 **Recommended Action**: `{res['recommended_action']}`")

            # Explanations & Rule Hits Side-by-Side
            e1, e2 = st.columns(2)

            with e1:
                st.markdown("#### 💡 Risk Factors & Explanation")
                for reason in res["reasons"]:
                    st.markdown(f"• **{reason}**")

            with e2:
                st.markdown("#### 🚨 Safety Rule Violations")
                if res["rule_hits"]:
                    for rule in res["rule_hits"]:
                        st.warning(f"**{rule['name'].upper()}** (+{rule['score']} pts): {rule['reason']}")
                else:
                    st.info("✅ No deterministic safety rules violated.")

            with st.expander("🛠️ Audit & Governance Trace"):
                st.json(res["audit"])

# TAB 2: MODEL METRICS & COST EVALUATION
with tab2:
    st.markdown("### 📊 Model Performance on Held-Out Test Set")
    metrics_path = Path(__file__).resolve().parents[1] / "models" / "risk_model.joblib"
    
    if not metrics_path.exists():
        try:
            from app.model import load_model
            load_model()
        except Exception:
            pass

    if metrics_path.exists():
        bundle = joblib.load(metrics_path)
        m = bundle["metrics"]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Precision", f"{m['precision']:.3f}", help="Portion of flagged transactions that are actual fraud.")
        k2.metric("Recall", f"{m['recall']:.3f}", help="Portion of total fraud caught by the model.")
        k3.metric("F1-Score", f"{m['f1']:.3f}", help="Harmonic mean of Precision and Recall.")
        k4.metric("ROC-AUC", f"{m['roc_auc']:.3f}", help="Overall classification capability.")

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🔢 Confusion Matrix")
            cm = m["confusion_matrix"]
            df_cm = pd.DataFrame(cm, index=["Actual Legitimate", "Actual Fraud"], columns=["Predicted Safe", "Predicted Flagged"])
            st.table(df_cm)

        with c2:
            st.markdown("#### 💸 False-Positive Friction Cost Analysis")
            fp_count = cm[0][1]
            st.markdown(f"""
            - **Total Held-Out Test Cases**: `{m['test_size']}`
            - **False Positives (Blocked Safe Users)**: `{fp_count}`
            - **False Positive Rate**: `{(fp_count / (cm[0][0] + fp_count))*100:.2f}%`
            
            > **Fintech Tradeoff**: Lowering thresholds increases Recall (catches more fraud) but increases False Positives (friction for legitimate customers). RiskShield provides configurable thresholds to balance merchant loss vs customer satisfaction.
            """)
    else:
        st.warning("⚠️ Model metrics file not found. Run `python -m app.train` first.")

# TAB 3: HUMAN REVIEW QUEUE
with tab3:
    st.markdown("### 🕵️ Human-in-the-Loop Borderline Queue (`WATCH` Cases)")
    st.markdown("Transactions with a score between **40 and 69** require manual risk officer review instead of automatic blocking.")
    
    sample_queue = pd.DataFrame([
        {"Txn ID": "TXN_98231", "User": "User_491", "Amount (₹)": 18500, "Score": 58.5, "Risk Signal": "New Device + High Hourly Velocity", "Status": "PENDING_REVIEW"},
        {"Txn ID": "TXN_98244", "User": "User_102", "Amount (₹)": 32000, "Score": 64.0, "Risk Signal": "Location Jump (850km) + High Amount", "Status": "PENDING_REVIEW"},
        {"Txn ID": "Txn_98250", "User": "User_884", "Amount (₹)": 12500, "Score": 44.2, "Risk Signal": "2 Failed PIN attempts", "Status": "PENDING_REVIEW"},
    ])
    st.dataframe(sample_queue, use_container_width=True)
    
    st.markdown("#### Review Action")
    sel_txn = st.selectbox("Select Transaction to Resolve", sample_queue["Txn ID"].tolist())
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        if st.button("✅ Approve Transaction", type="primary", use_container_width=True):
            st.success(f"Transaction `{sel_txn}` marked APPROVED. Safe list rule updated.")
    with r_col2:
        if st.button("❌ Reject / Confirm Fraud", use_container_width=True):
            st.error(f"Transaction `{sel_txn}` marked FRAUD. Blacklist updated.")

