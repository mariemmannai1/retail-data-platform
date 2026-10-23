# Retail Data Platform & AI Copilot

An end-to-end retail analytics project combining data engineering, business intelligence, machine learning, and a local AI assistant.

## Project Overview

This project transforms retail sales data into validated analytical datasets, business insights, sales forecasts, and natural-language answers.

### Key Features

- **Data Engineering:** Python-based data processing and pipeline orchestration.
- **Analytical Database:** DuckDB with fact and dimension tables.
- **Data Quality:** Validation of keys, relationships, missing values, duplicates, and analytical consistency.
- **Business Intelligence:** Power BI dashboard for sales performance analysis.
- **Sales Forecasting:** Random Forest regression model forecasting sales for seven days.
- **AI Copilot:** Local LLM powered by Ollama and Llama 3.2, with a Streamlit interface.
- **Data Export:** Parquet datasets prepared for Power BI.

## Technology Stack

| Area | Technologies |
|---|---|
| Programming | Python, SQL |
| Data Processing | Pandas, DuckDB |
| Data Storage | DuckDB, Parquet |
| Visualization | Power BI, Streamlit |
| Machine Learning | Scikit-learn, Random Forest |
| Local AI | Ollama, Llama 3.2 |
| Version Control | Git |

## Architecture

1. Raw retail CSV files are loaded from `data/raw/`.
2. Python and SQL scripts transform the data.
3. DuckDB stores the analytical model.
4. Validation scripts check data quality and model consistency.
5. Analytical datasets are exported to Parquet for Power BI.
6. A machine learning model generates a seven-day sales forecast.
7. The AI Copilot answers supported business questions using predefined, read-only SQL queries.

## Analytical Model

The project includes the following analytical tables:

- `fact_sales`
- `dim_products`
- `dim_stores`
- `dim_customers`
- `fact_inventory`
- `daily_sales`
- `forecast_sales`
- `forecast_model_metrics`

The model was validated against key data-quality and consistency checks.

## Sales Forecasting

A Random Forest regression model was evaluated against a seasonal baseline using a time-based train/test split.

| Metric | Result |
|---|---:|
| Training period | 327 days |
| Test period | 31 days |
| Random Forest MAE | 151.19 |
| Random Forest RMSE | 179.19 |
| Baseline MAE | 177.48 |
| MAE improvement over baseline | 14.8% |

**Important:** The available dataset covers 2025. The generated forecast for January 1–7, 2026 is a historical project output, not a current forecast.

## Power BI Dashboard

The Power BI report includes:

- **Sales Overview:** revenue, order count, quantity, average order value, sales by channel, monthly trends, and top products.
- **AI Sales Forecast:** forecast values, model evaluation metrics, and comparison with the baseline.

Open `Retail_Data_Platform.pbix` using Power BI Desktop.
After regenerating the Parquet exports, refresh the data in Power BI Desktop to update the report.

## AI Copilot

The local Streamlit application uses Ollama and Llama 3.2 to interpret questions and summarize results from predefined analytical SQL queries.

Supported topics include:

- Overall sales summary
- Sales by channel
- Top products by revenue
- Monthly sales trends
- Sales by product category
- Seven-day forecast

The model does not generate executable SQL. Python selects an approved query, and DuckDB is opened in read-only mode.

## Prerequisites

- Windows
- Python 3.11
- Git
- Power BI Desktop (for the report)
- Ollama with the `llama3.2:3b` model (for the AI Copilot)

## Setup

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd retail-data-platform
```

Create a virtual environment and install the required packages:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pandas duckdb scikit-learn streamlit ollama pyarrow
```

Install Ollama from its official website and download the model:

```powershell
ollama pull llama3.2:3b
```

## Running the Project

Run the main pipeline:

```powershell
.\.venv\Scripts\python.exe .\src\run_pipeline.py
```

Run the pipeline with forecasting:

```powershell
.\.venv\Scripts\python.exe .\src\run_pipeline.py --with-forecast
```

Launch the AI Copilot after the pipeline has generated the required local database and tables:

```powershell
.\.venv\Scripts\python.exe -m streamlit run .\src\ai_copilot.py
```

Run the AI Copilot tests:

```powershell
.\.venv\Scripts\python.exe -m py_compile .\src\ai_copilot.py
```

## Repository Structure

```text
retail-data-platform/
├── data/
│   ├── raw/                 # Local source CSV files (not tracked)
│   └── powerbi/             # Generated Parquet exports (not tracked)
├── sql/                     # SQL transformations and analysis
├── src/                     # Python pipeline, validation, forecasting, and AI
├── Retail_Data_Platform.pbix
├── run_project.bat
├── .gitignore
└── README.md
```

## Data Availability

Raw CSV files, generated Parquet exports, and local DuckDB databases are excluded from version control. The source data must be obtained separately and placed in `data/raw/` before running the pipeline.

## Limitations

- The forecast is based on historical synthetic/project data and should not be treated as a production business forecast.
- The AI Copilot only supports the analyses implemented in its approved query set.
- Forecast quality may change with additional data, seasonality, and future business conditions.

## Author

Developed as a portfolio project demonstrating practical skills in data engineering, analytics, business intelligence, machine learning, and local AI integration.
