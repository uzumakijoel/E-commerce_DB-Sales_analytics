from database import db_connection
import pandas as pd
import time
from functools import wraps

def measur_time(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        start=time.time()
        rv= func(*args,**kwargs)
        end=time.time()
        print(f"Time Execution : {end-start:.4f} seconds")
        return rv
    return wrapper
@measur_time
def analyze_dtata(host,user,password,database):
    with db_connection(host,user,password,database) as conn:
        cur=conn.cursor()
#       =========== GENERAL ANALYSIS SQL ===========

    # average order amount, nb of customers(real customers), total revenue
        cur.execute("""
            SELECT AVG(o.montant) AS avg_order_amount,
            COUNT(DISTINCT o.id_cust) AS total_nb_customers,
            SUM(p.montant) AS total_revenue
            FROM orders o
            INNER JOIN payement p
            ON o.id_ord = p.id_ord
            WHERE p.statut = 'accept?';
            """)
        total_general=pd.Series(
            cur.fetchone(),
            index=["avg_order_amount","total_nb_customers","total_revenue"]
        )

    #nb of order validated
        cur.execute("""
            SELECT count(*) AS total_nb_orders
            FROM orders
            WHERE statut = 'valid?';
        """)
        total_general["total_nb_orders"]=cur.fetchone()[0]

    #total cost, total quantity sold, and number of distinct products sold.
        cur.execute("""
            SELECT SUM(p.cout * oi.qte) AS total_cost,
            SUM(oi.qte) AS total_quantity,
            COUNT(DISTINCT oi.id_prod) AS total_products_sold
            FROM order_items oi
            INNER JOIN orders o
                ON oi.id_ord = o.id_ord
            INNER JOIN products p
                ON oi.id_prod = p.id_prod
            WHERE o.id_ord IN(
                    SELECT id_ord
                    FROM payement
                    WHERE statut = 'accept?'
                    );
            """)
        cur.fetchall()

    #payment methods and the number of successful payments for each method.
        cur.execute("""
            SELECT mode_pay, COUNT(*) AS nb
            FROM payement
            WHERE statut = 'accept?'
            GROUP BY mode_pay;
        """)
        rows=cur.fetchall()
        mode_pay= pd.Series(
            data=[row[1] for row in rows],
            index=[row[0] for row in rows]
        )

    #delivery delay by shipping method and rank of each delivered shipment based on its delivery time.
        cur.execute("""
            SELECT mode_livr, DATEDIFF(date_livr, date_exp) AS delay,
            ROW_NUMBER() OVER(PARTITION BY mode_livr ORDER BY DATEDIFF(date_livr, date_exp)) AS rank
            FROM shipments
            WHERE statut = 'livr?';
        """)
        livr=pd.DataFrame(
            cur.fetchall(),
            columns=[desc[0] for desc in cur.description]
        )
        livr= livr.pivot(
            columns="mode_livr",
            index="rank",
            values="delay"
        )
        
#       =========== TEMPORAL ANALYSIS SQL ===========

#Daily total_revenue
        cur.execute("""
            SELECT date AS day,
            COUNT(*) AS total_sales,
            SUM(montant) AS total_revenue
            FROM payement
            WHERE statut = 'accept?'
            GROUP BY date
            ORDER BY date;
        """)
        cur.fetchall()

#Weekly total_revenue
        cur.execute("""
            SELECT YEARWEEK(date) AS week,
            COUNT(*) AS total_sales,
            SUM(montant) AS total_revenue
            FROM payement
            WHERE statut = 'accept?'
            GROUP BY YEARWEEK(date)
            ORDER BY YEARWEEK(date);
        """)
        cur.fetchall()

#Quarterly total_revenue
        cur.execute("""
           
            SELECT QUARTER(date) AS quarter,
            COUNT(*) AS total_sales,
            SUM(montant) AS total_revenue
            FROM payement
            WHERE statut = 'accept?'
            GROUP BY QUARTER(date)
            ORDER BY QUARTER(date);
        """)
        cur.fetchall()

    #monthly sales count, monthly revenue, cumulative revenue, and month-over-month revenue difference.
        cur.execute("""
             WITH monthly_revenue AS(
                    SELECT MONTH(date) AS month,
                    COUNT(*) AS total_sales,
                    SUM(montant) AS total_revenue,
                    SUM(SUM(montant)) OVER (ORDER BY MONTH(date)) AS cumulative_revenue
                    FROM payement
                    WHERE statut = 'accept?'
                    GROUP BY MONTH(date)
                    ORDER BY MONTH(date)
                        )

            SELECT month,
            total_sales,
            total_revenue,
            cumulative_revenue,
            COALESCE(total_revenue-LAG(total_revenue) OVER (ORDER BY month),0) AS revenue_difference
            FROM monthly_revenue;
        """)
        column= [desc[0] for desc in cur.description]
        gn_month_anlys= pd.DataFrame(
            cur.fetchall(),
            columns=column
        )

    #monthly profit margin (revenue minus product costs) for paid orders.  
        cur.execute("""
            WITH cost AS(
                    SELECT
                    MONTH(o.date_cmd) AS mois,
                    o.id_ord,
                    o.montant AS revenue,
                    SUM(p.cout * oi.qte) AS cost
                    FROM orders o
                    INNER JOIN order_items oi
                    ON o.id_ord = oi.id_ord
                    INNER JOIN products p
                    ON oi.id_prod = p.id_prod
                    WHERE o.id_ord IN (
                        SELECT id_ord
                        FROM payement
                        WHERE statut = 'accept?'
                    )
                    GROUP BY o.id_ord, MONTH(o.date_cmd), o.montant
            )
            SELECT
                mois,
                SUM(revenue) - SUM(cost) AS total_margin
                FROM cost
            GROUP BY mois
            ORDER BY mois;""")
        column= [desc[0] for desc in cur.description]
        mrg_month_anlys= pd.DataFrame(
                cur.fetchall(),
                columns=column
            )
#       =========== PRODUCTS ANALYSIS SQL ===========

#top-selling products with total quantity sold and total
        cur.execute("""
            SELECT p.id_prod,p.nom_prod, SUM(oi.qte) AS total_qte_sold, 
            SUM(oi.qte * p.prix)- SUM(oi.qte * p.cout) AS total_profit
            FROM order_items oi
            INNER JOIN products p
            ON oi.id_prod = p.id_prod
            WHERE oi.id_ord IN(
                    SELECT id_ord
                    FROM payement
                    WHERE statut = 'accept?')
            GROUP BY p.id_prod, p.nom_prod
            ORDER BY total_qte_sold DESC
            LIMIT 20;
        """)    
        column=[desc[0] for desc in cur.description]
        top_products=pd.DataFrame(
            cur.fetchall(),
            columns=column
        )

    #top revenue-generating products with total quantity sold and total revenue. 
        cur.execute("""
            SELECT p.id_prod,p.nom_prod, SUM(oi.qte) AS total_qte_sold, 
            SUM(oi.qte * p.prix) AS total_revenue
            FROM order_items oi
            INNER JOIN products p
            ON oi.id_prod = p.id_prod
            WHERE oi.id_ord IN(
                    SELECT id_ord
                    FROM payement
                    WHERE statut = 'accept?')
            GROUP BY p.id_prod, p.nom_prod
            ORDER BY total_revenue DESC
            LIMIT 20;
        """)
        cur.fetchall()

    #most profitable products with total quantity sold and total profit generated.
        cur.execute("""
            SELECT p.id_prod,p.nom_prod, SUM(oi.qte) AS total_qte_sold, 
            SUM(oi.qte * p.prix)- SUM(oi.qte * p.cout) AS total_profit
            FROM order_items oi
            INNER JOIN products p
            ON oi.id_prod = p.id_prod
            WHERE oi.id_ord IN(
                    SELECT id_ord
                    FROM payement
                    WHERE statut = 'accept?')
            GROUP BY p.id_prod, p.nom_prod
            ORDER BY total_profit DESC
            LIMIT 20;
        """)   
        cur.fetchall()

    #underperforming products with below-average sales, revenue, profit, margin, and order count.
        cur.execute("""
            WITH product_analysis AS(
                SELECT p.id_prod,p.nom_prod, SUM(oi.qte) AS total_qte_sold, 
                SUM(oi.qte * (p.prix - p.cout)) AS total_profit,
                SUM(oi.qte * p.prix) AS total_revenue,
                COUNT(DISTINCT oi.id_ord) AS total_orders,
                (p.prix - p.cout) / p.prix * 100 AS profit_margin_percent
                FROM order_items oi
                INNER JOIN products p
                ON oi.id_prod = p.id_prod
                WHERE oi.id_ord IN(
                        SELECT id_ord
                        FROM payement
                        WHERE statut = 'accept?')
                GROUP BY p.id_prod, p.nom_prod
                )
            SELECT *
            FROM product_analysis
            WHERE total_qte_sold < (SELECT AVG(total_qte_sold) FROM product_analysis)
            AND total_revenue < (SELECT AVG(total_revenue) FROM product_analysis)
            AND total_profit < (SELECT AVG(total_profit) FROM product_analysis)
            AND profit_margin_percent < (SELECT AVG(profit_margin_percent) FROM product_analysis)
            AND total_orders < (SELECT AVG(total_orders) FROM product_analysis);
        """) 
        cur.fetchall()

    #products ranked by total number of orders in which they were sold.
        cur.execute("""
            SELECT p.id_prod,p.nom_prod, COUNT(DISTINCT oi.id_ord) AS total_orders_sold
            FROM order_items oi
            INNER JOIN products p
            ON oi.id_prod = p.id_prod
            GROUP BY p.id_prod, p.nom_prod
            ORDER BY total_orders_sold DESC;
        """)
        cur.fetchall()

#       =========== PRODUCT_CATEGORY ANALYSIS SQL ===========

    #category performance metrics including total revenue, quantity sold, and profit margin.
        cur.execute("""
            SELECT pc.id_cat,pc.nom_cat, SUM(oi.qte * oi.prix_unit) AS total_revenue,
            SUM(oi.qte) AS total_qte_sold,
            SUM(p.prix - p.cout) AS total_margin
            FROM order_items oi
            INNER JOIN products p
            ON oi.id_prod = p.id_prod
            INNER JOIN categories pc
            ON p.id_cat = pc.id_cat
            WHERE oi.id_ord IN(
                    SELECT id_ord
                    FROM payement
                    WHERE statut = 'accept?')
            GROUP BY pc.id_cat, pc.nom_cat
            ORDER BY total_revenue DESC;
        """)
        column=[desc[0] for desc in cur.description]
        cat_rev_anlys=pd.DataFrame(
            cur.fetchall(),
            columns=column
        )

    #monthly revenue by category, previous month's revenue, and month-over-month revenue change.
        cur.execute("""
            WITH mensual_revenue AS(
                    SELECT MONTH(pe.date) AS month, pc.id_cat, pc.nom_cat, 
                    SUM(oi.qte * oi.prix_unit) AS total_revenue
                    FROM order_items oi
                    INNER JOIN products p
                    ON oi.id_prod = p.id_prod
                    INNER JOIN categories pc
                    ON p.id_cat = pc.id_cat
                    INNER JOIN payement pe
                    ON oi.id_ord = pe.id_ord
                    WHERE pe.statut = 'accept?'
                    GROUP BY MONTH(pe.date), pc.id_cat, pc.nom_cat
                    )
                SELECT month,id_cat, nom_cat, total_revenue,
                COALESCE(LAG(total_revenue) OVER (PARTITION BY id_cat ORDER BY month),0) AS previous_month_revenue,
                COALESCE((total_revenue - LAG(total_revenue) OVER (PARTITION BY id_cat ORDER BY month)),0) AS revenue_change
                FROM mensual_revenue
                ORDER BY month, id_cat;
                """)
        cur.fetchall()

#       =========== CUSTOMER ANALYSIS SQL ===========

    #top customers ranked by total amount spent on paid orders.
        cur.execute("""
            SELECT c.id_cust, c.nom, c.pays, SUM(o.montant) AS total_spent
            FROM customers c
            JOIN orders o
            ON c.id_cust = o.id_cust
            WHERE o.id_ord IN (
                SELECT id_ord
                FROM payement
                WHERE statut = 'accept?')
            GROUP BY c.id_cust, c.nom, c.pays
            ORDER BY total_spent DESC
            LIMIT 20;
        """)
        column=[desc[0] for desc in cur.description]
        top_cust=pd.DataFrame(
            cur.fetchall(),
            columns=column
        )
    #customers ranked by total number of paid orders and average order value.
        cur.execute("""
            SELECT c.id_cust, c.nom, c.pays, COUNT(o.id_ord) AS total_order,
            AVG(o.montant) AS average_amount
            FROM customers c
            JOIN orders o
            ON c.id_cust = o.id_cust
            WHERE o.id_ord IN (
                SELECT id_ord
                FROM payement
                WHERE statut = 'accept?')
            GROUP BY c.id_cust, c.nom, c.pays
            ORDER BY total_order DESC;
        """)
        cur.fetchall()

    #first paid order with customer details, order amount, and order date.
        cur.execute("""
            SELECT c.id_cust, c.nom, c.pays, o.montant, o.date_cmd 
            FROM customers c
            JOIN orders o
            ON c.id_cust = o.id_cust
            WHERE o.id_ord IN (
                SELECT id_ord
                FROM payement
                WHERE statut = 'accept?')
            ORDER BY o.date_cmd 
            LIMIT 1;
                """)
        cur.fetchall()

    #most recent paid order with customer details, order amount, and order date.
        cur.execute("""
            SELECT c.id_cust, c.nom, c.pays, o.montant, o.date_cmd 
            FROM customers c
            JOIN orders o
            ON c.id_cust = o.id_cust
            WHERE o.id_ord IN (
                SELECT id_ord
                FROM payement
                WHERE statut = 'accept?')
            ORDER BY o.date_cmd DESC
            LIMIT 1;
            """)
        return (total_general,mode_pay,livr,gn_month_anlys,mrg_month_anlys,top_products,cat_rev_anlys,top_cust)


        