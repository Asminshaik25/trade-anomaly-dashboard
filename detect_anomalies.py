"""
detect_anomalies.py
Feature engineering + unsupervised anomaly detection on trade data.
Uses IsolationForest since real settlement data rarely has labeled fraud.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Amount z-score per counterparty (is this trade unusual FOR THIS client?)
    df["amount_zscore"] = df.groupby("counterparty")["amount_usd"].transform(
        lambda x: (x - x.mean()) / (x.std() + 1e-6)
    )

    # Trade velocity: how many trades this counterparty made same day
    df["trade_date"] = df["timestamp"].dt.date
    df["daily_trade_count"] = df.groupby(["counterparty", "trade_date"])["trade_id"].transform("count")

    # Flag duplicate-looking IDs (data quality signal)
    df["is_duplicate_flagged"] = df["trade_id"].str.contains("_DUP").astype(int)

    # Off-hours trading flag (before 6am or after 8pm)
    df["is_off_hours"] = ((df["hour_of_day"] < 6) | (df["hour_of_day"] > 20)).astype(int)

    # Failed/cancelled status as numeric risk signal
    df["status_risk"] = df["status"].map({
        "SETTLED": 0, "PENDING": 1, "CANCELLED": 2, "FAILED": 3
    })

    return df

def run_detection(df: pd.DataFrame) -> pd.DataFrame:
    df = engineer_features(df)

    feature_cols = [
        "amount_usd", "amount_zscore", "daily_trade_count",
        "settlement_days", "is_off_hours", "status_risk"
    ]
    X = df[feature_cols].fillna(0)
    X_scaled = StandardScaler().fit_transform(X)

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,  # assume ~5% of trades are anomalous
        random_state=42
    )
    df["anomaly_score"] = model.fit_predict(X_scaled)  # -1 = anomaly, 1 = normal
    df["risk_score"] = -model.decision_function(X_scaled)  # higher = riskier

    df["flagged"] = (df["anomaly_score"] == -1) | (df["is_duplicate_flagged"] == 1)

    return df

if __name__ == "__main__":
    df = pd.read_csv("trades.csv")
    result = run_detection(df)
    result.to_csv("trades_scored.csv", index=False)

    flagged = result[result["flagged"]].sort_values("risk_score", ascending=False)
    print(f"Total trades: {len(result)}")
    print(f"Flagged trades: {len(flagged)} ({len(flagged)/len(result)*100:.1f}%)")
    print("\nTop 10 riskiest trades:")
    print(flagged[["trade_id", "counterparty", "amount_usd", "status", "risk_score"]].head(10))
