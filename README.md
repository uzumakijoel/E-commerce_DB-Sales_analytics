**E-commerce database & Sales analytics**

A data analysis project based on an e-commerce database, built with *MYSQL,Python,Pandas,Matplotlib*.

The objective of this project is to analyse e-commerce data in order to understand sales performance, products, categorie, customers, payements, and shipments, and then transform SQL results into data analysis and visualizations using python

TECHNOLOGIE 
    *MYSQL/MariaDB
    *XAMPP/phpMyAdmin
    *Python3
    *mysql-connector-python
    *Pandas
    *Matplotlib

PROJECT STRUCTURE
    E-commerce_DB&Sales_analytics
    |
    |--Database/
    |   |_ecommerce_analysis.sql
    |
    |--Output/
    |   |_chart/
    |
    |--python
    |   |_analysis.py
    |   |_database.py
    |   |_visualization.py
    |
    |--README.md
    |--requirements.txt

ANALYSES PERFORMED
_General analysis
    The project calculates:
        *Total revenue
        *Number of customers
        *Number of orders
        *Average order amount
        *Total quantity sold
        *Number of products sold
        *Total cost

_Time-Based analysis
    Sales are analysed:
        *Daily
        *Weekly
        *Monthly
        *Quarterly
    The monthly analysis also calculate
        *Monthly revenue
        *Number of sales
        *Cumulative revenue
        *Revenue difference compared with the previous month

_Margin analysis
_Products analysis
_Category analysis
_Customers analysis
_payement analysis
_shipment analysis

SQL
The project uses several SQL features, including:
    *INNER JOIN
    *GROUP BY
    *ORDER BY
    *WHERE
    *Subqueries
    *CASE
    *COALESCE
    *CTEs(WITH)
    *Aggregate functions
    *ROW_NUMBER()
    *LAG()
    *SUM() OVER()
    *PARTITION BY

INSTALLATION
1.Clone the repository
    git clone <REPOSITORY_URL>
    cd E-commerce_DB&Sales_analytics

2.Install dependencies
    pip install -r requirement.txt

3.Set up MySQL
    a. Start MYSQL from XAMPP
    b. Open myPhpAdmin
    c. Execute ecommerce_analysis.sql
    d. Make sure the ecommerce_analysis database is available

4.Run the analysis script
5.Generate the visualizations
    Run visualization.py

The chart will be saved in Output/chart/

Possible future improvements...

Author

    NAMBIGUE joel

    computer science student focused on Deep Learning, Machine learning, and data engineering

