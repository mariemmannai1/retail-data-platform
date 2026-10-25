
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st


# --------------------------------------------------
# Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="📊",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "retail.duckdb"

st.title("Retail Sales Dashboard")
st.caption("Sales performance, product analysis and 7-day forecast")


# --------------------------------------------------
# Database connection
# --------------------------------------------------
@st.cache_data(ttl=60)
def load_data():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        sales = con.execute("""
            SELECT
                order_date,
                order_channel,
                number_of_orders,
                total_revenue,
                average_order_value
            FROM daily_sales
            ORDER BY order_date
        """).fetchdf()

        products = con.execute("""
            SELECT
            f.order_date,
            f.order_channel,
            p.product_id,
            p.product_name,
            p.category,
            f.quantity,
            f.line_net_amount
            FROM fact_sales f
            LEFT JOIN dim_products p
                ON f.product_id = p.product_id
            WHERE f.order_status = 'Completed'
        """).fetchdf()

        kpis = con.execute("""
            SELECT
                COUNT(DISTINCT order_id) AS orders,
                COALESCE(SUM(line_net_amount), 0) AS revenue,
                COALESCE(SUM(quantity), 0) AS units_sold
            FROM fact_sales
            WHERE order_status = 'Completed'
        """).fetchdf()

        forecast = con.execute("""
            SELECT
                forecast_date,
                forecast_revenue,
                model_name
            FROM forecast_sales_champion
            ORDER BY forecast_date
        """).fetchdf()

    sales["order_date"] = pd.to_datetime(sales["order_date"])
    forecast["forecast_date"] = pd.to_datetime(
        forecast["forecast_date"]
    )

    return sales, products, kpis, forecast


try:
    sales, products, kpis, forecast = load_data()
except Exception as exc:
    st.error(f"Unable to load dashboard data: {exc}")
    st.stop()


# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------
st.sidebar.header("Filters")

if sales.empty:
    st.warning("No daily sales data available.")
    st.stop()

min_date = sales["order_date"].min().date()
max_date = sales["order_date"].max().date()

date_range = st.sidebar.date_input(
    "Sales period",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

filtered_sales = sales[
    sales["order_date"].dt.date.between(start_date, end_date)
].copy()

channels = sorted(
    filtered_sales["order_channel"].dropna().unique().tolist()
)

selected_channels = st.sidebar.multiselect(
    "Sales channels",
    options=channels,
    default=channels,
)

filtered_sales = filtered_sales[
    filtered_sales["order_channel"].isin(selected_channels)
]


# --------------------------------------------------
# KPI cards
# --------------------------------------------------
st.subheader("Key Performance Indicators")

# Revenue and orders are calculated for the selected period
# and selected channels.
revenue = filtered_sales["total_revenue"].sum()
orders = filtered_sales["number_of_orders"].sum()

aov = revenue / orders if orders else 0

# Product metrics use completed sales in the selected period.
with duckdb.connect(str(DB_PATH), read_only=True) as con:
    product_kpis = con.execute("""
        SELECT
            COALESCE(SUM(f.quantity), 0) AS units_sold
        FROM fact_sales f
        WHERE f.order_status = 'Completed'
          AND f.order_date BETWEEN ? AND ?
          AND f.order_channel IN (
              SELECT unnest(?)
          )
    """, [start_date, end_date, selected_channels]).fetchone()

units_sold = product_kpis[0] if product_kpis else 0

c1, c2, c3, c4 = st.columns(4)

c1.metric("Revenue", f"{revenue:,.2f} DT")
c2.metric("Orders", f"{orders:,.0f}")
c3.metric("Average Order Value", f"{aov:,.2f} DT")
c4.metric("Units Sold", f"{units_sold:,.0f}")


# --------------------------------------------------
# Daily sales trend
# --------------------------------------------------
st.subheader("Daily Revenue Trend")

daily = (
    filtered_sales.groupby("order_date", as_index=False)
    ["total_revenue"].sum()
    .sort_values("order_date")
)

if not daily.empty:
    st.line_chart(
        daily.set_index("order_date")["total_revenue"],
        x_label="Date",
        y_label="Revenue (DT)",
    )
else:
    st.info("No sales for the selected filters.")


# --------------------------------------------------
# Sales by channel
# --------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Revenue by Channel")

    channel_data = (
        filtered_sales.groupby("order_channel", as_index=False)
        .agg(
            revenue=("total_revenue", "sum"),
            orders=("number_of_orders", "sum"),
        )
        .sort_values("revenue", ascending=False)
    )

    if not channel_data.empty:
        st.bar_chart(
            channel_data.set_index("order_channel")["revenue"],
            x_label="Channel",
            y_label="Revenue (DT)",
        )
        st.dataframe(channel_data, hide_index=True, use_container_width=True)
    else:
        st.info("No channel data available.")



# --------------------------------------------------
# Top 5 products
# --------------------------------------------------
with right:
    st.subheader("Top 5 Products by Revenue")

    filtered_products = products[
        products["order_date"].dt.date.between(start_date, end_date)
        & products["order_channel"].isin(selected_channels)
    ].copy()

    top_products = (
        filtered_products
        .groupby(
            ["product_id", "product_name", "category"],
            as_index=False
        )
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("line_net_amount", "sum")
        )
        .sort_values("revenue", ascending=False)
        .head(5)
    )

    if not top_products.empty:
        top_products["revenue"] = top_products["revenue"].round(2)

        st.bar_chart(
            top_products.set_index("product_name")["revenue"],
            x_label="Product",
            y_label="Revenue (DT)",
        )

        st.dataframe(
            top_products[
                ["product_name", "category", "units_sold", "revenue"]
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No product data available.")



# --------------------------------------------------
# 7-day sales forecast
# --------------------------------------------------
st.subheader("Sales Forecast — Champion Model")

if not forecast.empty:
    latest_run = forecast["forecast_date"].max()
    forecast_view = forecast[
        forecast["forecast_date"] >= latest_run - pd.Timedelta(days=6)
    ].copy()

    st.caption(
        "Forecasts are taken from forecast_sales_champion. "
        "They are model predictions, not actual sales."
    )

    st.line_chart(
        forecast_view.set_index("forecast_date")["forecast_revenue"],
        x_label="Forecast date",
        y_label="Predicted revenue (DT)",
    )

    st.dataframe(
        forecast_view[
            ["forecast_date", "forecast_revenue", "model_name"]
        ].rename(
            columns={
                "forecast_date": "Date",
                "forecast_revenue": "Predicted Revenue (DT)",
                "model_name": "Model",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )
else:
    st.warning(
        "No forecast rows found. Run the forecasting pipeline first."
    )


# --------------------------------------------------
# Data export
# --------------------------------------------------
st.subheader("Export")

csv = filtered_sales.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download filtered sales (CSV)",
    data=csv,
    file_name="retail_sales_filtered.csv",
    mime="text/csv",
)

st.caption("Data source: local DuckDB analytical database.")
