from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate_tickets(n_rows: int = 1200, seed: int = 42) -> pd.DataFrame:
    """Generate a realistic synthetic IT support ticket dataset."""
    rng = np.random.default_rng(seed)

    teams = ["Service Desk", "Infrastructure", "Applications", "Security", "Network"]
    categories = [
        "Access Request",
        "Hardware",
        "Software",
        "Network",
        "Email",
        "Security Incident",
        "Onboarding",
        "VPN",
    ]
    category_weights = [0.16, 0.14, 0.20, 0.15, 0.12, 0.06, 0.10, 0.07]

    priorities = ["Low", "Medium", "High", "Critical"]
    priority_weights = [0.25, 0.45, 0.23, 0.07]

    statuses = ["Resolved", "Closed", "Open", "In Progress", "Pending"]
    status_weights = [0.56, 0.20, 0.10, 0.09, 0.05]

    locations = ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", "Remote"]
    location_weights = [0.22, 0.16, 0.13, 0.14, 0.11, 0.24]

    agents_by_team = {
        "Service Desk": ["Alice Brown", "Marco Klein", "Lina Schmitt", "Priya Sharma"],
        "Infrastructure": ["Jonas Weber", "Nina Falk", "David Ross"],
        "Applications": ["Sofia Lang", "Emre Kaya", "Chris Miller"],
        "Security": ["Marta Novak", "Noah Fischer"],
        "Network": ["Tim Bauer", "Kevin Zhang", "Olivia Reed"],
    }

    start = pd.Timestamp.today().normalize() - pd.Timedelta(days=240)
    end = pd.Timestamp.today().normalize()
    total_hours = int((end - start).total_seconds() // 3600)

    created_offsets = rng.integers(0, max(total_hours, 1), size=n_rows)
    created_at = start + pd.to_timedelta(created_offsets, unit="h")

    team = rng.choice(teams, size=n_rows, p=[0.34, 0.20, 0.18, 0.12, 0.16])
    category = rng.choice(categories, size=n_rows, p=category_weights)
    priority = rng.choice(priorities, size=n_rows, p=priority_weights)
    status = rng.choice(statuses, size=n_rows, p=status_weights)
    location = rng.choice(locations, size=n_rows, p=location_weights)

    agent = [rng.choice(agents_by_team[t]) for t in team]

    base_by_priority = {"Low": 20, "Medium": 14, "High": 9, "Critical": 5}
    resolution_hours = []
    for p in priority:
        # Right-skewed distribution for realistic handling times.
        sampled = rng.gamma(shape=2.4, scale=base_by_priority[p])
        resolution_hours.append(max(1.0, sampled))

    resolved_at = []
    satisfaction = []
    for i in range(n_rows):
        is_resolved = status[i] in {"Resolved", "Closed"}
        if is_resolved:
            resolved_ts = created_at[i] + pd.Timedelta(hours=float(resolution_hours[i]))
            resolved_at.append(resolved_ts)

            score_center = {"Low": 4.4, "Medium": 4.0, "High": 3.6, "Critical": 3.3}[priority[i]]
            score = float(np.clip(rng.normal(loc=score_center, scale=0.55), 1.0, 5.0))
            satisfaction.append(round(score, 1))
        else:
            resolved_at.append(pd.NaT)
            satisfaction.append(np.nan)

    tickets = pd.DataFrame(
        {
            "ticket_id": [f"INC-{100000 + i}" for i in range(1, n_rows + 1)],
            "created_at": created_at,
            "resolved_at": resolved_at,
            "priority": priority,
            "category": category,
            "agent": agent,
            "team": team,
            "status": status,
            "location": location,
            "satisfaction_score": satisfaction,
        }
    ).sort_values("created_at")

    return tickets.reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic IT support ticket data.")
    parser.add_argument("--rows", type=int, default=1200, help="Number of tickets to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    output_path = Path("data/raw/tickets_raw.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = generate_tickets(n_rows=args.rows, seed=args.seed)
    df.to_csv(output_path, index=False)

    print(f"Generated {len(df)} rows -> {output_path}")


if __name__ == "__main__":
    main()
