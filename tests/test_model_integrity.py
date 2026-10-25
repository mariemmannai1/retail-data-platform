
import duckdb


def test_fact_sales_dimension_joins():
    con = duckdb.connect(":memory:")

    try:
        con.execute("""
            CREATE TABLE dim_products (product_id VARCHAR PRIMARY KEY)
        """)
        con.execute("""
            CREATE TABLE dim_stores (store_id VARCHAR PRIMARY KEY)
        """)
        con.execute("""
            CREATE TABLE dim_customers (customer_id VARCHAR PRIMARY KEY)
        """)
        con.execute("""
            CREATE TABLE fact_sales (
                order_id VARCHAR,
                product_id VARCHAR,
                store_id VARCHAR,
                customer_id VARCHAR
            )
        """)

        con.execute("INSERT INTO dim_products VALUES ('P1')")
        con.execute("INSERT INTO dim_stores VALUES ('S1')")
        con.execute("INSERT INTO dim_customers VALUES ('C1')")
        con.execute("""
            INSERT INTO fact_sales VALUES ('O1', 'P1', 'S1', 'C1')
        """)

        for dimension in ["products", "stores", "customers"]:
            key = {
                "products": "product_id",
                "stores": "store_id",
                "customers": "customer_id",
            }[dimension]

            missing = con.execute(f"""
                SELECT COUNT(*)
                FROM fact_sales f
                LEFT JOIN dim_{dimension} d
                    ON f.{key} = d.{key}
                WHERE d.{key} IS NULL
            """).fetchone()[0]

            assert missing == 0, f"Missing {dimension} reference"

    finally:
        con.close()
