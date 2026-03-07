# IT Operations Analytics Platform (V1)

## Project Overview
This project is a portfolio-ready IT Operations Analytics Platform built with Python, pandas, and Streamlit. It simulates an IT support environment, processes ticket data, and presents operational KPIs in an interactive dashboard.

## Business Problem
IT support teams need fast visibility into service performance:
- How many tickets are open vs resolved?
- Which categories and priorities create the most workload?
- Are SLAs being breached?
- How satisfied are users with support outcomes?

Without this visibility, teams struggle to prioritize improvements and communicate performance to stakeholders.

## Features
- Synthetic IT support ticket dataset generation (500+ rows)
- Data cleaning and transformation pipeline
- KPI engineering:
  - `resolution_time_hours`
  - `SLA_breached`
- Interactive Streamlit dashboard with:
  - total tickets
  - open tickets
  - resolved tickets
  - average resolution time
  - SLA breach rate
  - tickets by category
  - tickets by priority
  - tickets over time
  - satisfaction score overview
- Sidebar filters for category, priority, team, and location

## Tech Stack
- Python
- pandas
- numpy
- Streamlit
- Plotly

## Project Structure
```text
it-operations-analytics-platform/
|-- app/
|   `-- app.py
|-- data/
|   |-- raw/
|   |   `-- tickets_raw.csv
|   `-- processed/
|       `-- tickets_cleaned.csv
|-- src/
|   |-- generate_data.py
|   `-- process_data.py
|-- requirements.txt
|-- .gitignore
`-- README.md
```

## How to Run Locally
1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Generate synthetic raw data:
   ```bash
   python src/generate_data.py
   ```
4. Process the data:
   ```bash
   python src/process_data.py
   ```
5. Launch the dashboard:
   ```bash
   streamlit run app/app.py
   ```

## What This Project Demonstrates for Recruiters
- Data Analyst: data cleaning, KPI modeling, trend analysis, dashboarding
- IT Support: ticket lifecycle analysis, SLA monitoring, operational insights
- Software Development: clean Python scripts, structured project layout, reusable logic
- IT Consulting: turning operational data into clear, decision-ready reporting

## Current Scope
V1 focuses on a complete, clean baseline workflow from raw data generation to dashboard insights. Automated tests and advanced modeling are intentionally deferred to future versions.
