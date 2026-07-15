# Trade Settlement Anomaly Detection & Automation Dashboard

A simulated trading-operations tool that detects anomalous or high-risk trades,
flags them for manual review, and automates the daily reporting workflow — the
kind of problem financial technology platforms (e.g. trading/settlement systems)
solve for banks and institutional clients.

## Problem it solves
Settlement teams manually review thousands of trades a day looking for failed
settlements, duplicate entries, and unusually large/risky trades. This project
automates that triage using unsupervised machine learning, so only the highest
risk trades get routed to humans.

## Architecture
1. **`generate_data.py`** — Generates a realistic synthetic dataset of 5,000+
   trades (amounts, counterparties, instruments, statuses, timestamps), with
   injected anomalies and duplicate records.
2. **`detect_anomalies.py`** — Feature engineering (per-counterparty z-scores,
   trade velocity, off-hours flag, settlement status risk) + **IsolationForest**
   for unsupervised anomaly detection (no labeled fraud data required — this
   mirrors real-world settlement data).
3. **`daily_report.py`** — Automation layer: generates a daily ops summary
   report (`daily_summary_report.txt`) listing the top flagged trades and a
   recommended action — simulating what would normally be a manual EOD task.
4. **`dashboard.py`** — Interactive Streamlit dashboard: KPIs, trend charts,
   status/instrument breakdowns, and a sortable flagged-trades table.

## How to run
```bash
pip install pandas numpy faker scikit-learn streamlit plotly

python generate_data.py        # creates trades.csv
python detect_anomalies.py     # creates trades_scored.csv
python daily_report.py         # creates daily_summary_report.txt
streamlit run dashboard.py     # launches interactive dashboard
```

## Key design decisions (good interview talking points)
- **Unsupervised over supervised**: Real settlement data rarely has labeled
  fraud/error cases, so IsolationForest was chosen over a classifier.
- **Per-counterparty normalization**: A $2M trade is normal for one client and
  anomalous for another — z-scores are computed within each counterparty's
  own history, not globally.
- **Rule-based + ML hybrid**: Duplicate trade IDs are caught by a deterministic
  rule (data quality), while subtler anomalies (unusual size, timing, velocity)
  are caught by the ML model — combining both catches more issue types.
- **Automation layer**: The daily report script demonstrates end-to-end
  workflow automation, not just a one-off analysis.

## Resume bullet points
- Built an unsupervised anomaly detection pipeline (IsolationForest,
  scikit-learn) to flag high-risk financial trades from 5,000+ simulated
  transactions, achieving ~5% precision-targeted flagging rate.
- Engineered risk features (counterparty-normalized z-scores, trade velocity,
  settlement status) to improve anomaly detection accuracy over raw-amount
  thresholds.
- Automated daily operations reporting, reducing manual review scope by
  surfacing only the top-risk trades to a compliance queue.
- Designed an interactive Streamlit dashboard for real-time trade monitoring,
  KPI tracking, and flagged-trade triage.
