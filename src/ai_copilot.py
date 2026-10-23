
from pathlib import Path

import duckdb
import ollama
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "retail.duckdb"
MODEL = "llama3.2:3b"

st.set_page_config(
    page_title="Retail AI Copilot",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Retail AI Copilot")
st.caption("Ask questions about retail sales in natural language")

if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.stop()

# Fixed, read-only analytical queries.
QUERIES = {
    "channel_sales": """
        SELECT order_channel,
               ROUND(SUM(total_revenue), 2) AS revenue,
               SUM(number_of_orders) AS orders,
               ROUND(
                   SUM(total_revenue) /
                   NULLIF(SUM(number_of_orders), 0), 2
               ) AS average_order_value
        FROM daily_sales
        GROUP BY order_channel
        ORDER BY revenue DESC
    """,
    "top_products": """
        SELECT p.product_name,
               ROUND(SUM(f.line_net_amount), 2) AS revenue
        FROM fact_sales f
        JOIN dim_products p ON f.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY revenue DESC
        LIMIT 5
    """,
    "category_sales": """
        SELECT p.category,
               ROUND(SUM(f.line_net_amount), 2) AS revenue,
               SUM(f.quantity) AS units_sold
        FROM fact_sales f
        JOIN dim_products p ON f.product_id = p.product_id
        GROUP BY p.category
        ORDER BY revenue DESC
    """,
    "monthly_sales": """
        SELECT strftime(order_date, '%Y-%m') AS month,
               ROUND(SUM(total_revenue), 2) AS revenue
        FROM daily_sales
        GROUP BY month
        ORDER BY month
    """,
    "forecast": """
        SELECT forecast_date,
               ROUND(forecast_revenue, 2) AS forecast_revenue
        FROM forecast_sales
        ORDER BY forecast_date
    """,
    "sales_summary": """
        SELECT ROUND(SUM(total_revenue), 2) AS total_revenue,
               SUM(number_of_orders) AS total_orders,
               ROUND(
                   SUM(total_revenue) /
                   NULLIF(SUM(number_of_orders), 0), 2
               ) AS average_order_value
        FROM daily_sales
    """,
}

INTENTS = {
    "channel_sales": "sales by channel",
    "top_products": "top products by revenue",
    "category_sales": "sales by product category",
    "monthly_sales": "monthly sales trend",
    "forecast": "seven-day sales forecast",
    "sales_summary": "overall sales summary",
}


def identify_intent(question):
    prompt = f"""
You classify questions about a retail sales database.

Choose exactly ONE key from this list:
{", ".join(INTENTS.keys())}

Rules:
- channel_sales: sales by channel, channel comparison,
  or average order value by channel
- top_products: top five products or products ranked by revenue
- category_sales: revenue or units sold by product category
- monthly_sales: sales by month or monthly trends
- forecast: forecast or predicted sales
- sales_summary: overall revenue, total orders, average order value

If the question is unrelated or cannot be answered by these options,
return: unsupported

Return only the key. Do not generate SQL.

Question: {question}
"""
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )

    intent = response["message"]["content"].strip().lower()
    return intent if intent in QUERIES else "unsupported"


def answer_question(question, con):
    intent = identify_intent(question)

    if intent == "unsupported":
        return (
            "I cannot answer that question with the current analyses. "
            "Try asking about overall sales, sales by channel, product "
            "categories, top products, monthly trends, or the forecast."
        ), None, None

    df = con.execute(QUERIES[intent]).fetchdf()

    if df.empty:
        return "No data was found for this question.", df, None

    records = df.to_json(orient="records", date_format="iso")

    prompt = f"""
You are Retail AI Copilot, a careful retail data analyst.

Answer using ONLY the query results below.
- Never invent numbers or facts.
- Mention relevant figures from the results.
- Keep the answer concise and in English.
- Explain what the returned figures show.
- Do not claim that correlation proves causation.
- If the result does not answer part of the question, say so.

User question: {question}
Analysis selected: {INTENTS[intent]}
Database results: {records}
"""
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )

    return response["message"]["content"], df, intent


with duckdb.connect(str(DB_PATH), read_only=True) as con:
    tables = con.execute("SHOW TABLES").fetchdf()["name"].tolist()

    st.sidebar.header("Data sources")
    st.sidebar.success("DuckDB connected")
    st.sidebar.write(f"LLM: {MODEL}")
    st.sidebar.write("Database: read-only")
    st.sidebar.write("Available tables:")
    st.sidebar.write(", ".join(tables))

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("data") is not None:
                st.dataframe(
                    message["data"],
                    use_container_width=True,
                )

                chart_type = message.get("chart_type")
                if chart_type == "bar":
                    st.bar_chart(
                        message["data"],
                        x=message["x_column"],
                        y=message["y_column"],
                    )
                elif chart_type == "line":
                    st.line_chart(
                        message["data"],
                        x=message["x_column"],
                        y=message["y_column"],
                    )

    question = st.chat_input(
        "Ask about sales, categories, products or forecasts..."
    )

    if question:
        st.session_state.messages.append({
            "role": "user",
            "content": question,
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing your question..."):
                try:
                    answer, result_df, intent = answer_question(
                        question, con
                    )

                    st.markdown(answer)

                    chart_type = None
                    x_column = None
                    y_column = None

                    chart_config = {
                        "channel_sales": (
                            "bar", "order_channel", "revenue"
                        ),
                        "category_sales": (
                            "bar", "category", "revenue"
                        ),
                        "top_products": (
                            "bar", "product_name", "revenue"
                        ),
                        "monthly_sales": (
                            "line", "month", "revenue"
                        ),
                        "forecast": (
                            "line", "forecast_date", "forecast_revenue"
                        ),
                    }

                    if result_df is not None:
                        st.dataframe(
                            result_df,
                            use_container_width=True,
                        )

                        if intent in chart_config:
                            (
                                chart_type,
                                x_column,
                                y_column,
                            ) = chart_config[intent]

                            st.subheader("Visualization")

                            if chart_type == "bar":
                                st.bar_chart(
                                    result_df,
                                    x=x_column,
                                    y=y_column,
                                )
                            else:
                                st.line_chart(
                                    result_df,
                                    x=x_column,
                                    y=y_column,
                                )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "data": result_df,
                        "chart_type": chart_type,
                        "x_column": x_column,
                        "y_column": y_column,
                    })

                except Exception as error:
                    st.error(
                        f"Could not process the question: {error}"
                    )
