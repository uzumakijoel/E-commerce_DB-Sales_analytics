from analysis import analyze_dtata
import matplotlib.pyplot as plt
import calendar

(total_general,mode_pay,livr,gn_month_anlys,mrg_month_anlys,top_products,cat_rev_anlys,top_cust) = analyze_dtata("localhost","root","","ecommerce_analysis")

figure,axes=plt.subplots(2,2, figsize=(14,10))
figure.suptitle("KPI business")

axes[0,0].bar(gn_month_anlys['month'], gn_month_anlys['total_revenue'], color="lightcoral",edgecolor="black")
axes[0,0].set_xticks(gn_month_anlys['month'])
axes[0,0].set_xticklabels(calendar.month_name[m] for m in gn_month_anlys['month'])
axes[0,0].tick_params(axis="x", labelrotation=20)
axes[0,0].set_xlabel("month")
axes[0,0].set_ylabel("revenue")
axes[0,0].set_title("Monthly revenue")

axes[0,1].bar(mrg_month_anlys['mois'], mrg_month_anlys['total_margin'], color="steelblue",edgecolor="black")
axes[0,1].set_xticks(mrg_month_anlys['mois'])
axes[0,1].set_xticklabels(calendar.month_name[m] for m in mrg_month_anlys['mois'])
axes[0,1].tick_params(axis="x", labelrotation=20)
axes[0,1].set_xlabel("month")
axes[0,1].set_ylabel("margin")
axes[0,1].set_title("Monthly margin")

axes[1,0].bar(mode_pay.index,mode_pay.values, color=["#4E79A7","#59A14F","#F28E2B"], edgecolor="black")
axes[1,0].set_ylabel("value")
axes[1,0].set_title("payement method")

axes[1,1].plot(livr.index, livr['aerien'], color="#4E79A7", label="aerien")
axes[1,1].plot(livr.index, livr['maritime'], color="#59A14F", label="maritime")
axes[1,1].plot(livr.index, livr['terrestre'], color="#F28E2B", label="terrestre")
axes[1,1].set_xlabel("Indice ")
axes[1,1].set_ylabel("Day")
axes[1,1].set_title("Shipments method")

figure.subplots_adjust(
    left=0.05,
    bottom=0.08,
    right=0.986,
    top=0.905,
    wspace=0.19,
    hspace=0.48
)
plt.legend()
plt.savefig("E-commerce_DB&Sales_analytics/Output/chart/fig.png")
plt.show()


figure,axes= plt.subplots(3,1, figsize=(12,15))
figure.suptitle("Products and customers")

cat=cat_rev_anlys.head(10)
axes[0].bar(cat['nom_cat'],cat['total_revenue'], color='lightgreen', edgecolor='black')
axes[0].set_xlabel("Categorie")
axes[0].set_ylabel("revenue")
axes[0].set_title("Category revenue")

cust=top_cust.head(10)
axes[1].bar(cust['nom'],cust['total_spent'], color='steelblue', edgecolor='black')
axes[1].set_xlabel("Customer")
axes[1].set_ylabel("Expenditure")
axes[1].set_title("Top customer")

prod=top_products.head(10)
axes[2].bar(prod['nom_prod'],prod['total_qte_sold'], color='skyblue', edgecolor='black')
axes[2].set_xlabel("Products")
axes[2].set_ylabel("Quantity")
axes[2].set_title("Top products")

figure.subplots_adjust(
    left=0.041,
    right=1
)
plt.savefig("E-commerce_DB&Sales_analytics/Output/chart/fig2.png")
plt.show()