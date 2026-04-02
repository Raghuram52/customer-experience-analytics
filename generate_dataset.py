"""
Customer Experience Analytics — Dataset Generator
====================================================
Generates a rich, realistic synthetic CX dataset for Power BI analysis.
Produces four related CSV files that model a real enterprise CX operation.

Run this script once to generate the data, then load into Power BI Desktop.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
START_DATE  = datetime(2023, 1, 1)
END_DATE    = datetime(2024, 12, 31)
N_CUSTOMERS = 300
N_TICKETS   = 1200
N_SURVEYS   = 600

SEGMENTS        = ["Enterprise", "Mid-Market", "SMB", "Startup"]
SEGMENT_WEIGHTS = [0.20, 0.25, 0.35, 0.20]
INDUSTRIES      = ["Financial Services", "Healthcare", "Retail", "Technology",
                   "Manufacturing", "Education", "Media", "Logistics"]
REGIONS         = ["North America", "EMEA", "APAC", "LATAM"]
CHANNELS        = ["Email", "Chat", "Phone", "Self-Service Portal"]
CHANNEL_WEIGHTS = [0.35, 0.30, 0.20, 0.15]
CATEGORIES      = ["Access & Authentication", "Billing & Payments", "Data & Reporting",
                   "Integration & API", "Performance & Stability", "Feature Request",
                   "Positive Feedback", "Security & Compliance", "User Management",
                   "Product Education"]
CAT_WEIGHTS     = [0.14, 0.10, 0.18, 0.12, 0.13, 0.10, 0.07, 0.06, 0.06, 0.04]
PRIORITIES      = ["Critical", "High", "Medium", "Low"]
PRIORITY_WEIGHTS= [0.05, 0.20, 0.45, 0.30]
SENTIMENTS      = ["Positive", "Neutral", "Negative", "Urgent"]
STATUSES        = ["Open", "In Progress", "Resolved", "Closed"]
STATUS_WEIGHTS  = [0.10, 0.15, 0.45, 0.30]
AGENTS          = ["Sarah Chen", "Marcus Johnson", "Priya Patel", "James O'Brien",
                   "Aisha Williams", "Carlos Rivera", "Emma Thompson", "David Kim"]

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days),
                             hours=random.randint(0, 23),
                             minutes=random.randint(0, 59))

# ─────────────────────────────────────────────
# TABLE 1: CUSTOMERS
# ─────────────────────────────────────────────
def generate_customers():
    print("[1/4] Generating customers...")
    customers = []
    for i in range(1, N_CUSTOMERS + 1):
        segment  = random.choices(SEGMENTS, SEGMENT_WEIGHTS)[0]
        industry = random.choice(INDUSTRIES)
        region   = random.choice(REGIONS)
        join_date= random_date(datetime(2020, 1, 1), datetime(2023, 6, 1))

        # MRR based on segment
        mrr_ranges = {"Enterprise": (5000, 25000), "Mid-Market": (1000, 5000),
                      "SMB": (200, 1000), "Startup": (50, 500)}
        mrr = random.randint(*mrr_ranges[segment])

        # Health score influenced by segment
        base_health = {"Enterprise": 75, "Mid-Market": 70, "SMB": 65, "Startup": 60}
        health_score = min(100, max(10, base_health[segment] + random.randint(-25, 25)))

        customers.append({
            "customer_id":   f"C{i:04d}",
            "company_name":  f"Company {i:04d}",
            "segment":       segment,
            "industry":      industry,
            "region":        region,
            "join_date":     join_date.strftime("%Y-%m-%d"),
            "mrr":           mrr,
            "health_score":  health_score,
            "num_users":     random.randint(5, 500) if segment == "Enterprise" else random.randint(1, 50),
            "renewal_date":  (join_date + timedelta(days=365)).strftime("%Y-%m-%d"),
            "csm_assigned":  random.choice(AGENTS),
        })

    df = pd.DataFrame(customers)
    df.to_csv(f"{OUTPUT_DIR}/customers.csv", index=False)
    print(f"   Saved {len(df)} customers → {OUTPUT_DIR}/customers.csv")
    return df

# ─────────────────────────────────────────────
# TABLE 2: SUPPORT TICKETS
# ─────────────────────────────────────────────
def generate_tickets(customers_df):
    print("[2/4] Generating support tickets...")
    tickets = []
    customer_ids = customers_df["customer_id"].tolist()

    for i in range(1, N_TICKETS + 1):
        customer_id = random.choice(customer_ids)
        customer    = customers_df[customers_df["customer_id"] == customer_id].iloc[0]
        created_at  = random_date(START_DATE, END_DATE)
        category    = random.choices(CATEGORIES, CAT_WEIGHTS)[0]
        priority    = random.choices(PRIORITIES, PRIORITY_WEIGHTS)[0]
        channel     = random.choices(CHANNELS, CHANNEL_WEIGHTS)[0]
        status      = random.choices(STATUSES, STATUS_WEIGHTS)[0]

        # Resolution time based on priority (hours)
        res_hours = {"Critical": random.randint(1, 8),   "High": random.randint(4, 24),
                     "Medium":   random.randint(8, 72),  "Low":  random.randint(24, 168)}
        resolution_hours = res_hours[priority]
        resolved_at = created_at + timedelta(hours=resolution_hours) if status in ["Resolved","Closed"] else None

        # CSAT influenced by resolution time and priority
        if status in ["Resolved", "Closed"]:
            base_csat = 4.0 if resolution_hours < 24 else 3.0
            csat = round(min(5.0, max(1.0, base_csat + random.uniform(-1.5, 1.5))), 1)
        else:
            csat = None

        tickets.append({
            "ticket_id":        f"T{i:05d}",
            "customer_id":      customer_id,
            "segment":          customer["segment"],
            "created_date":     created_at.strftime("%Y-%m-%d"),
            "created_month":    created_at.strftime("%Y-%m"),
            "created_quarter":  f"Q{(created_at.month-1)//3+1} {created_at.year}",
            "channel":          channel,
            "category":         category,
            "priority":         priority,
            "status":           status,
            "assigned_agent":   random.choice(AGENTS),
            "resolution_hours": resolution_hours if status in ["Resolved","Closed"] else None,
            "csat_score":       csat,
            "region":           customer["region"],
            "industry":         customer["industry"],
        })

    df = pd.DataFrame(tickets)
    df.to_csv(f"{OUTPUT_DIR}/tickets.csv", index=False)
    print(f"   Saved {len(df)} tickets → {OUTPUT_DIR}/tickets.csv")
    return df

# ─────────────────────────────────────────────
# TABLE 3: CSAT SURVEYS
# ─────────────────────────────────────────────
def generate_surveys(customers_df):
    print("[3/4] Generating CSAT surveys...")
    surveys = []
    customer_ids = customers_df["customer_id"].tolist()

    for i in range(1, N_SURVEYS + 1):
        customer_id  = random.choice(customer_ids)
        customer     = customers_df[customers_df["customer_id"] == customer_id].iloc[0]
        survey_date  = random_date(START_DATE, END_DATE)

        # NPS 0-10, CSAT 1-5, CES 1-7
        health       = customer["health_score"]
        nps_base     = int(health / 10)
        nps_score    = min(10, max(0, nps_base + random.randint(-3, 3)))
        csat_score   = min(5.0, max(1.0, round((health / 20) + random.uniform(-1, 1), 1)))
        ces_score    = min(7, max(1, int(8 - (health / 20)) + random.randint(-1, 1)))

        nps_category = "Promoter" if nps_score >= 9 else "Passive" if nps_score >= 7 else "Detractor"

        surveys.append({
            "survey_id":      f"S{i:05d}",
            "customer_id":    customer_id,
            "segment":        customer["segment"],
            "region":         customer["region"],
            "survey_date":    survey_date.strftime("%Y-%m-%d"),
            "survey_month":   survey_date.strftime("%Y-%m"),
            "survey_quarter": f"Q{(survey_date.month-1)//3+1} {survey_date.year}",
            "nps_score":      nps_score,
            "nps_category":   nps_category,
            "csat_score":     csat_score,
            "ces_score":      ces_score,
            "industry":       customer["industry"],
        })

    df = pd.DataFrame(surveys)
    df.to_csv(f"{OUTPUT_DIR}/surveys.csv", index=False)
    print(f"   Saved {len(df)} surveys → {OUTPUT_DIR}/surveys.csv")
    return df

# ─────────────────────────────────────────────
# TABLE 4: MONTHLY KPI SUMMARY
# ─────────────────────────────────────────────
def generate_monthly_kpis(tickets_df, surveys_df):
    print("[4/4] Generating monthly KPI summary...")

    # Ticket volume by month
    ticket_monthly = tickets_df.groupby("created_month").agg(
        total_tickets=("ticket_id", "count"),
        critical_tickets=("priority", lambda x: (x == "Critical").sum()),
        high_tickets=("priority", lambda x: (x == "High").sum()),
        avg_resolution_hours=("resolution_hours", "mean"),
        avg_csat=("csat_score", "mean"),
    ).reset_index()

    # Survey metrics by month
    survey_monthly = surveys_df.groupby("survey_month").agg(
        avg_nps=("nps_score", "mean"),
        promoter_pct=("nps_category", lambda x: round((x == "Promoter").sum() / len(x) * 100, 1)),
        detractor_pct=("nps_category", lambda x: round((x == "Detractor").sum() / len(x) * 100, 1)),
        avg_ces=("ces_score", "mean"),
    ).reset_index().rename(columns={"survey_month": "created_month"})

    # Merge
    kpis = ticket_monthly.merge(survey_monthly, on="created_month", how="left")
    kpis.columns = [c.replace("_", " ").title() for c in kpis.columns]
    kpis = kpis.round(2)

    kpis.to_csv(f"{OUTPUT_DIR}/monthly_kpis.csv", index=False)
    print(f"   Saved {len(kpis)} months → {OUTPUT_DIR}/monthly_kpis.csv")
    return kpis

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  CX Analytics Dataset Generator")
    print("  For Power BI Dashboard")
    print("=" * 55)

    customers = generate_customers()
    tickets   = generate_tickets(customers)
    surveys   = generate_surveys(customers)
    kpis      = generate_monthly_kpis(tickets, surveys)

    print("\n" + "=" * 55)
    print("  Dataset generation complete!")
    print(f"  Output files in ./{OUTPUT_DIR}/")
    print("=" * 55)
    print("\nNext steps:")
    print("  1. Open Power BI Desktop")
    print("  2. Get Data → Text/CSV")
    print("  3. Load all 4 CSV files")
    print("  4. Follow README for dashboard setup")

if __name__ == "__main__":
    main()
