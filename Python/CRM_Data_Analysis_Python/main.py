import plotly.io as pio
pio.renderers.default = "browser" 

from scripts.load_data import load_crm_data
from scripts.clean_deals import clean_deals

calls, contacts, deals, spend = load_crm_data()
deals_clean = clean_deals(deals)

print(deals_clean.head())

print(deals_clean["stage"].value_counts())


#Анализ и графики продаж
from tabulate import tabulate
from scripts.analyze_sales import analyze_sales_efficiency

owner_stats, campaign_stats = analyze_sales_efficiency(deals_clean)

from tabulate import tabulate
from scripts.visualize_sales import plot_sales_by_owner, plot_sales_by_campaign

#По владельцам сделок
print("\n=== Owner ===")
print(tabulate(owner_stats.head(10), headers='keys', tablefmt='grid', floatfmt=".2f"))

#По кампаниям
print("\n=== Campaign ===")
print(tabulate(campaign_stats.head(10), headers='keys', tablefmt='grid', floatfmt=".2f"))

plot_sales_by_owner(owner_stats)
plot_sales_by_campaign(campaign_stats)


#Анализ и графики платежей, продуктов, обучения
from scripts.analyze_payments_products import analyze_payment_types, analyze_products_and_education

payment_stats = analyze_payment_types(deals_clean)
print("\n=== By Payment Types ===")
print(tabulate(payment_stats, headers='keys', tablefmt='grid', floatfmt=".2f"))

product_stats, education_stats = analyze_products_and_education(deals_clean)

print("\n=== By Products===")
print(tabulate(product_stats.head(10), headers='keys', tablefmt='grid', floatfmt=".2f"))

print("\n=== By Education Types ===")
print(tabulate(education_stats, headers='keys', tablefmt='grid', floatfmt=".2f"))

from scripts.visualize_payments_products import (
    plot_payment_types,
    plot_product_revenue,
    plot_education_conversion
)

plot_payment_types(payment_stats)
plot_product_revenue(product_stats)
plot_education_conversion(education_stats)


#Географический анализ и графики
from scripts.analyze_geography import analyze_deals_by_city, analyze_language_effect

geo_stats = analyze_deals_by_city(deals_clean)
lang_geo_stats = analyze_language_effect(deals_clean)

print("\n=== By City ===")
print(tabulate(geo_stats.head(15), headers="keys", tablefmt="grid", floatfmt=".2f"))

print("\n=== By City and Language Level ===")
print(tabulate(lang_geo_stats.head(20), headers="keys", tablefmt="grid", floatfmt=".2f"))

from scripts.visualize_geography import (
    plot_city_conversion,
    plot_city_revenue_map,
    plot_language_conversion
)

plot_city_conversion(geo_stats)
plot_city_revenue_map(geo_stats)
plot_language_conversion(deals_clean)

from scripts.cohort_analysis import build_cohort_table

# Анализ когорт по Created и Closed
print("\n=== Cohort Table: Created Time ===")
cohort_created = build_cohort_table(deals_clean, date_col="created_time")
print(cohort_created)

print("\n=== Cohort Table: Closing Date ===")
cohort_closed = build_cohort_table(deals_clean, date_col="closing_date")
print(cohort_closed)