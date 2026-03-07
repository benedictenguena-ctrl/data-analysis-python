from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path("data/processed/tickets_cleaned.csv")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["resolved_at"] = pd.to_datetime(df["resolved_at"], errors="coerce")
    return df


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    categories = sorted(df["category"].dropna().unique())
    priorities = sorted(df["priority"].dropna().unique())
    teams = sorted(df["team"].dropna().unique())
    locations = sorted(df["location"].dropna().unique())

    selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
    selected_priorities = st.sidebar.multiselect("Priority", priorities, default=priorities)
    selected_teams = st.sidebar.multiselect("Team", teams, default=teams)
    selected_locations = st.sidebar.multiselect("Location", locations, default=locations)

    filtered = df[
        df["category"].isin(selected_categories)
        & df["priority"].isin(selected_priorities)
        & df["team"].isin(selected_teams)
        & df["location"].isin(selected_locations)
    ].copy()

    return filtered


def render_kpis(df: pd.DataFrame) -> None:
    total_tickets = len(df)
    open_tickets = int(df["status"].isin(["Open", "In Progress", "Pending"]).sum())
    resolved_tickets = int(df["status"].isin(["Resolved", "Closed"]).sum())
    avg_resolution = float(df["resolution_time_hours"].dropna().mean()) if total_tickets else 0.0
    sla_breach_rate = float(df["SLA_breached"].mean() * 100) if total_tickets else 0.0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Tickets", f"{total_tickets:,}")
    c2.metric("Open Tickets", f"{open_tickets:,}")
    c3.metric("Resolved Tickets", f"{resolved_tickets:,}")
    c4.metric("Avg Resolution (hrs)", f"{avg_resolution:.1f}")
    c5.metric("SLA Breach Rate", f"{sla_breach_rate:.1f}%")


def render_charts(df: pd.DataFrame) -> None:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Tickets by Category")
        category_counts = df["category"].value_counts().reset_index()
        category_counts.columns = ["category", "tickets"]
        fig_category = px.bar(category_counts, x="category", y="tickets", color="category")
        st.plotly_chart(fig_category, use_container_width=True)

    with col_b:
        st.subheader("Tickets by Priority")
        priority_order = ["Low", "Medium", "High", "Critical"]
        priority_counts = (
            df["priority"]
            .value_counts()
            .reindex(priority_order)
            .fillna(0)
            .reset_index()
        )
        priority_counts.columns = ["priority", "tickets"]
        fig_priority = px.bar(priority_counts, x="priority", y="tickets", color="priority")
        st.plotly_chart(fig_priority, use_container_width=True)

    st.subheader("Tickets Over Time")
    over_time = (
        df.set_index("created_at")
        .resample("W")
        .size()
        .reset_index(name="tickets")
        .dropna()
    )
    fig_time = px.line(over_time, x="created_at", y="tickets", markers=True)
    st.plotly_chart(fig_time, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("Satisfaction Score Distribution")
        scores = df["satisfaction_score"].dropna()
        if not scores.empty:
            fig_scores = px.histogram(scores, nbins=10, x="satisfaction_score")
            st.plotly_chart(fig_scores, use_container_width=True)
        else:
            st.info("No satisfaction scores available for current filters.")

    with col_d:
        st.subheader("Satisfaction by Priority")
        sat_by_priority = (
            df.dropna(subset=["satisfaction_score"])
            .groupby("priority", as_index=False)["satisfaction_score"]
            .mean()
        )
        if not sat_by_priority.empty:
            fig_sat = px.bar(sat_by_priority, x="priority", y="satisfaction_score", color="priority")
            st.plotly_chart(fig_sat, use_container_width=True)
        else:
            st.info("No satisfaction data available for current filters.")


def main() -> None:
    st.set_page_config(page_title="IT Operations Analytics Platform", layout="wide")
    st.title("IT Operations Analytics Platform")
    st.caption("V1 portfolio dashboard for IT support ticket performance")

    if not DATA_PATH.exists():
        st.error("Processed data not found. Run src/generate_data.py and src/process_data.py first.")
        st.stop()

    df = load_data()
    filtered_df = apply_filters(df)

    if filtered_df.empty:
        st.warning("No data matches the selected filters.")
        st.stop()

    render_kpis(filtered_df)
    render_charts(filtered_df)

    st.subheader("Sample Ticket Data")
    st.dataframe(filtered_df.head(25), use_container_width=True)
e

if __name__ == "__main__":
    main()
