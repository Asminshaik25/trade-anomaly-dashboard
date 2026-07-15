"""
generate_data.py
Generates a synthetic trade/transaction dataset simulating what a
trading/settlement system (like ION's clients) would produce.
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)
np.random.seed(42)

N_TRADES = 5000

COUNTERPARTIES = [fake.company() for _ in range(40)]
STATUSES = ["SETTLED", "FAILED", "PENDING", "CANCELLED"]
STATUS_WEIGHTS = [0.85, 0.06, 0.06, 0.03]
INSTRUMENTS = ["EQUITY", "BOND", "FX", "DERIVATIVE", "COMMODITY"]

def random_timestamp(start_days_ago=90):
    start = datetime.now() - timedelta(days=start_days_ago)
    random_seconds = random.randint(0, start_days_ago * 24 * 3600)
    return start + timedelta(seconds=random_seconds)

rows = []
for i in range(N_TRADES):
    ts = random_timestamp()
    base_amount = np.random.lognormal(mean=9, sigma=1.2)  # realistic skew

    # Inject anomalies (~4% of trades)
    is_anomaly_seed = random.random() < 0.04
    if is_anomaly_seed:
        base_amount *= random.uniform(8, 25)  # unusually large trade

    row = {
        "trade_id": f"TRD{100000+i}",
        "timestamp": ts,
        "counterparty": random.choice(COUNTERPARTIES),
        "instrument": random.choice(INSTRUMENTS),
        "amount_usd": round(base_amount, 2),
        "status": random.choices(STATUS_WEIGHTS and STATUSES, weights=STATUS_WEIGHTS)[0],
        "settlement_days": max(0, int(np.random.normal(2, 1))),
        "hour_of_day": ts.hour,
    }
    rows.append(row)

df = pd.DataFrame(rows)

# Add a few duplicate trades (data quality issue -> should be flagged)
duplicates = df.sample(15, random_state=1).copy()
duplicates["trade_id"] = duplicates["trade_id"] + "_DUP"
df = pd.concat([df, duplicates], ignore_index=True)

df = df.sort_values("timestamp").reset_index(drop=True)
df.to_csv("trades.csv", index=False)

print(f"Generated {len(df)} trades -> trades.csv")
print(df["status"].value_counts())
