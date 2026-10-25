"""Analyses métier : promotions, clients, magasins, stocks à risque.

Règles : voir docs/business_rules.md (commandes Completed ; Net Sales = SUM(line_net_amount)).
Les résultats sont affichés et enregistrés en CSV dans data/analysis/.
"""
from pathlib import Path

import duckdb

project_dir = Path(__file__).resolve().parent.parent
db_path = project_dir / "retail.duckdb"
raw_dir = project_dir / "data" / "raw"
out_dir = project_dir / "data" / "analysis"
out_dir.mkdir(parents=True, exist_ok=True)

promotions_csv = (raw_dir / "promotions.csv").as_posix()
suppliers_csv = (raw_dir / "suppliers.csv").as_posix()

ANALYSES = {
    "1_promotions": ("PROMOTIONS : lignes de vente avec et sans promotion", f"""
        SELECT COALESCE(p.promotion_name, 'Sans promotion') AS promotion,
               COUNT(*) AS lines,
               SUM(f.quantity) AS units,
               ROUND(SUM(f.line_net_amount), 2) AS net_sales,
               ROUND(SUM(f.discount_amount), 2) AS discount_given,
               ROUND(100 * SUM(f.discount_amount)
                     / NULLIF(SUM(f.quantity * f.unit_price), 0), 1) AS discount_pct_of_list_price
        FROM fact_sales f
        LEFT JOIN read_csv_auto('{promotions_csv}') p ON f.promotion_id = p.promotion_id
        WHERE f.order_status = 'Completed'
        GROUP BY 1 ORDER BY net_sales DESC"""),

    "2a_clients_identifies": ("CLIENTS : commandes identifiées et anonymes", """
        SELECT CASE WHEN customer_id IS NULL THEN 'Anonyme' ELSE 'Identifié' END AS client_type,
               COUNT(DISTINCT order_id) AS orders,
               ROUND(SUM(line_net_amount), 2) AS net_sales,
               ROUND(SUM(line_net_amount) / COUNT(DISTINCT order_id), 2) AS net_sales_per_order
        FROM fact_sales WHERE order_status = 'Completed'
        GROUP BY 1 ORDER BY orders DESC"""),

    "2b_clients_fidelite": ("CLIENTS : niveau de fidélité (clients identifiés)", """
        SELECT c.loyalty_tier,
               COUNT(DISTINCT f.customer_id) AS customers,
               COUNT(DISTINCT f.order_id) AS orders,
               ROUND(SUM(f.line_net_amount), 2) AS net_sales,
               ROUND(SUM(f.line_net_amount) / COUNT(DISTINCT f.order_id), 2) AS net_sales_per_order
        FROM fact_sales f JOIN dim_customers c USING (customer_id)
        WHERE f.order_status = 'Completed'
        GROUP BY 1 ORDER BY net_sales DESC"""),

    "2c_clients_segments": ("CLIENTS : segments (clients identifiés)", """
        SELECT c.customer_segment,
               COUNT(DISTINCT f.customer_id) AS customers,
               COUNT(DISTINCT f.order_id) AS orders,
               ROUND(SUM(f.line_net_amount), 2) AS net_sales,
               ROUND(SUM(f.line_net_amount) / COUNT(DISTINCT f.order_id), 2) AS net_sales_per_order
        FROM fact_sales f JOIN dim_customers c USING (customer_id)
        WHERE f.order_status = 'Completed'
        GROUP BY 1 ORDER BY net_sales DESC"""),

    "3_magasins": ("MAGASINS : classement par Net Sales", """
        SELECT s.store_id, s.store_name, s.city, s.store_format, s.staff_count,
               COUNT(DISTINCT f.order_id) AS orders,
               ROUND(SUM(f.line_net_amount), 2) AS net_sales,
               ROUND(SUM(f.line_net_amount) / COUNT(DISTINCT f.order_id), 2) AS net_sales_per_order,
               ROUND(SUM(f.line_net_amount) / s.staff_count, 0) AS net_sales_per_staff
        FROM fact_sales f JOIN dim_stores s USING (store_id)
        WHERE f.order_status = 'Completed'
        GROUP BY s.store_id, s.store_name, s.city, s.store_format, s.staff_count
        ORDER BY net_sales DESC"""),

    "4a_stock_par_magasin": ("STOCKS : couples magasin-produit sous le seuil de réapprovisionnement", """
        SELECT i.store_id,
               COUNT(*) AS below_reorder_level,
               COUNT(*) FILTER (WHERE i.stock_on_hand + i.stock_on_order < p.reorder_level) AS not_covered_by_pending_order
        FROM fact_inventory i JOIN dim_products p USING (product_id)
        WHERE i.stock_on_hand < p.reorder_level
        GROUP BY 1 ORDER BY below_reorder_level DESC"""),

    "4b_stock_a_commander": ("STOCKS : 10 plus grands manques non couverts par une commande en cours", f"""
        SELECT i.store_id, i.product_id, p.product_name, p.category,
               i.stock_on_hand, i.stock_on_order, p.reorder_level,
               p.reorder_level - (i.stock_on_hand + i.stock_on_order) AS shortfall,
               su.lead_time_days
        FROM fact_inventory i
        JOIN dim_products p USING (product_id)
        LEFT JOIN read_csv_auto('{suppliers_csv}') su ON p.supplier_id = su.supplier_id
        WHERE i.stock_on_hand + i.stock_on_order < p.reorder_level
        ORDER BY shortfall DESC, i.stock_on_hand ASC
        LIMIT 10"""),

    "5_statuts_par_canal": ("STATUTS : part des remboursements et annulations par canal", """
        SELECT order_channel,
               COUNT(DISTINCT order_id) AS orders,
               ROUND(100.0 * COUNT(DISTINCT order_id) FILTER (WHERE order_status = 'Refunded')
                     / COUNT(DISTINCT order_id), 2) AS refunded_pct,
               ROUND(100.0 * COUNT(DISTINCT order_id) FILTER (WHERE order_status = 'Cancelled')
                     / COUNT(DISTINCT order_id), 2) AS cancelled_pct
        FROM fact_sales GROUP BY 1 ORDER BY orders DESC"""),
}

with duckdb.connect(str(db_path), read_only=True) as con:
    for name, (title, sql) in ANALYSES.items():
        df = con.execute(sql).fetchdf()
        df.to_csv(out_dir / f"{name}.csv", index=False)
        print(f"\n{title}")
        print("-" * len(title))
        print(df.to_string(index=False))

print(f"\nFichiers enregistrés dans : {out_dir}")
