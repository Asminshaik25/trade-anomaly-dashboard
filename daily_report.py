"""
daily_report.py
Simulates the 'automation' layer: auto-generates a daily ops summary
that would normally be produced manually by a settlements/ops team.
"""

import pandas as pd
from datetime import datetime

def generate_report(scored_csv="trades_scored.csv", out_file="daily_summary_report.txt"):
    df = pd.read_csv(scored_csv)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    total = len(df)
    failed = (df["status"] == "FAILED").sum()
    flagged = df["flagged"].sum()
    top_risky = df[df["flagged"]].sort_values("risk_score", ascending=False).head(5)

    lines = []
    lines.append(f"DAILY TRADE OPERATIONS SUMMARY — Generated {datetime.now():%Y-%m-%d %H:%M}")
    lines.append("=" * 60)
    lines.append(f"Total trades processed:        {total}")
    lines.append(f"Failed settlements:            {failed} ({failed/total*100:.1f}%)")
    lines.append(f"Flagged for manual review:     {flagged} ({flagged/total*100:.1f}%)")
    lines.append("")
    lines.append("TOP 5 TRADES REQUIRING REVIEW:")
    lines.append("-" * 60)
    for _, row in top_risky.iterrows():
        lines.append(
            f"  {row['trade_id']:<15} {row['counterparty'][:25]:<25} "
            f"${row['amount_usd']:>12,.2f}  risk={row['risk_score']:.3f}"
        )
    lines.append("")
    lines.append("Recommended action: Route flagged trades to compliance queue.")

    report = "\n".join(lines)
    with open(out_file, "w") as f:
        f.write(report)

    print(report)
    print(f"\nSaved to {out_file}")

if __name__ == "__main__":
    generate_report()
