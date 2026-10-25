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

   A Random Forest model forecasts daily sales for seven days. It was first evaluated on one test month, then on 26 rolling periods against simpler references.

   | Model | MAE (26 periods) |
   |---|---:|
   | Historical average | 117.80 |
   | Average by weekday | 119.02 |
   | Random Forest | 128.21 |
   | lag_7 baseline | 167.76 |

   The Random Forest beats the lag_7 baseline (14.8% lower MAE on the December test month) but does not beat a simple historical average on this synthetic dataset. The seven-day forecast therefore uses the best-performing model (`src/forecast_champion.py`). The data covers 2025: the January 1–7, 2026 forecast is a historical project output.

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
## Business Rules and KPIs

Defined in `docs/business_rules.md`: only `Completed` orders count; amounts are in GBP (per the data dictionary).

| KPI | Value |
|---|---:|
| Net Sales (excl. VAT) | 228,457.01 |
| Revenue incl. VAT and delivery | 249,520.30 |
| Orders | 9,589 |
| Quantity | 90,585 |
| Average order value | 26.02 |

## Key Findings

See `docs/analysis_findings.md`. Highlights: promotions represent 4.9% of net sales; identified and anonymous customers have the same basket (23.84 vs 23.78); convenience stores sell as much as large supermarkets with about three times fewer staff per sale; 92 store-product pairs are below their reorder level, 57 of them without a pending order.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

41 tests passed successfully. They cover the project's existing data integrity, analytical consistency, and forecasting checks.

## Prerequisites

- Windows
- Python 3.11
- Git
- Power BI Desktop (for the report)
- Ollama with the `llama3.2:3b` model (for the AI Copilot)

## Setup

Clone the repository:

```bash
git clone https://github.com/mariemmannai1/retail-data-platform.git
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

### Run with Docker

Docker Desktop must be installed and running.

Build and execute the Dockerized pipeline:

```powershell
docker compose run --rm retail-pipeline
```

The pipeline runs the analytical model, data-quality validations, daily-sales consistency checks, forecast loading, and Parquet export validation.

The Docker test pipeline uses a separate database (`retail_docker_test.duckdb`) and export directory (`data/powerbi_docker_test/`) to avoid overwriting the original local project outputs.

To rebuild the Docker image after changing the Docker configuration or dependencies:

```powershell
docker compose build --no-cache
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


## Recent Improvements

### Sales Dashboard with Streamlit

Added `dashboards/sales_dashboard.py`, a separate interactive sales dashboard built with Streamlit.

The dashboard includes:
- Key performance indicators: revenue, order count, average order value, and units sold.
- Daily sales trends and revenue by sales channel.
- Top five products by revenue.
- Sales forecast visualization.
- Date and sales-channel filters.
- CSV download functionality.

This application complements the existing two-page Power BI report.

### SQL and Daily Sales Validation

Updated `sql/build_analytics.sql` to improve the calculation of `average_order_value` using decimal arithmetic and a division-by-zero safeguard.

Updated `src/compare_daily_sales.py` to compare aggregated sales from the source orders with the `daily_sales` analytical table. The checks cover:
- Missing date/channel groups.
- Order count differences.
- Revenue differences.
- Average order value differences.

A rounding discrepancy was investigated for online orders on March 20, 2025. The source and analytical model can produce different rounded AOV values at a half-cent boundary because of floating-point and rounding behavior. The current comparison uses a tolerance of `0.010001` for AOV differences. Therefore, the check confirms consistency within this tolerance rather than exact equality.

### Additional Validation Scripts

Added `src/check_numeric_types.py` to support the inspection of numeric data types.

Renamed `src/validate_exports_test.py` to `src/validate_exports.py`. This script validates the exported Parquet datasets against their corresponding DuckDB tables by checking file existence and row counts.

The rename prevents this standalone validation script from being collected as a pytest test module. Its validation logic remains available as a separate script.

### Automated Test Collection Fix

The standalone export validation script previously used `sys.exit()` at module level and had a filename matching pytest's test-file naming pattern. This caused an error during test collection.

After renaming the script, the project test suite completed successfully:

- **41 tests passed**
- **Execution time: 18.58 seconds**

Command used:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### Power BI Refresh Issue

Resolved a cyclic-reference error encountered while refreshing the existing Power BI report. The issue was addressed by disabling the automatic date/time option in Power BI Desktop.

After the change, the report refreshed successfully, and both existing pages were checked:
- Sales Overview
- AI Sales Forecast

The existing report and its visuals were preserved.

### Version Control

The recent SQL, Python validation, and Streamlit dashboard changes were committed and pushed to the GitHub repository on the `main` branch.

