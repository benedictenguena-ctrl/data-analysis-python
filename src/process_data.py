from __future__ import annotations

from pathlib import Path

import pandas as pd


SLA_TARGET_HOURS = {
    "Low": 72,
    "Medium": 48,
    "High": 24,
    "Critical": 8,
}


def clean_tickets(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich ticket data with resolution and SLA metrics."""
    cleaned = df.copy()

    text_cols = ["ticket_id", "priority", "category", "agent", "team", "status", "location"]
    for col in text_cols:
        cleaned[col] = cleaned[col].astype(str).str.strip()

    cleaned["priority"] = cleaned["priority"].str.title()
    cleaned["category"] = cleaned["category"].str.title()
    cleaned["team"] = cleaned["team"].str.title()
    cleaned["status"] = cleaned["status"].str.title()
    cleaned["location"] = cleaned["location"].str.title()

    cleaned["created_at"] = pd.to_datetime(cleaned["created_at"], errors="coerce")
    cleaned["resolved_at"] = pd.to_datetime(cleaned["resolved_at"], errors="coerce")
    cleaned["satisfaction_score"] = pd.to_numeric(cleaned["satisfaction_score"], errors="coerce")

    cleaned = cleaned.dropna(subset=["ticket_id", "created_at"]).drop_duplicates(subset=["ticket_id"])

    invalid_resolution = cleaned["resolved_at"].notna() & (cleaned["resolved_at"] < cleaned["created_at"])
    cleaned.loc[invalid_resolution, "resolved_at"] = pd.NaT
    cleaned.loc[invalid_resolution, "status"] = "Open"

    cleaned["sla_target_hours"] = cleaned["priority"].map(SLA_TARGET_HOURS).fillna(48)
    cleaned["resolution_time_hours"] = (
        (cleaned["resolved_at"] - cleaned["created_at"]).dt.total_seconds() / 3600
    ).round(2)

    now = pd.Timestamp.now()
    due_at = cleaned["created_at"] + pd.to_timedelta(cleaned["sla_target_hours"], unit="h")
    resolved_mask = cleaned["resolved_at"].notna()

    breached_resolved = resolved_mask & (cleaned["resolved_at"] > due_at)
    breached_open = (~resolved_mask) & (now > due_at)
    cleaned["SLA_breached"] = breached_resolved | breached_open

    cleaned["satisfaction_score"] = cleaned["satisfaction_score"].clip(1, 5).round(1)

    columns_order = [
        "ticket_id",
        "created_at",
        "resolved_at",
        "priority",
        "category",
        "agent",
        "team",
        "status",
        "location",
        "satisfaction_score",
        "sla_target_hours",
        "resolution_time_hours",
        "SLA_breached"
    ]
    return cleaned[columns_order].sort_values("created_at").reset_index(drop=True)


def main() -> None:
    input_path = Path("data/raw/tickets_raw.csv")
    output_path = Path("data/processed/tickets_cleaned.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Raw data not found at {input_path}. Run src/generate_data.py first."
        )

    raw_df = pd.read_csv(input_path)
    cleaned_df = clean_tickets(raw_df)
    cleaned_df.to_csv(output_path, index=False)

    print(f"Processed {len(cleaned_df)} rows -> {output_path}")


if __name__ == "__main__":
    main()
