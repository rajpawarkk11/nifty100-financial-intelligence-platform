import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

# 5 random companies
print("=" * 60)
print("5 RANDOM COMPANIES")
print("=" * 60)

companies = pd.read_sql("""
SELECT id, company_name
FROM companies
ORDER BY RANDOM()
LIMIT 5
""", conn)

print(companies)

# Year coverage
print("\n" + "=" * 60)
print("YEAR COVERAGE")
print("=" * 60)

coverage = pd.read_sql("""
SELECT
    company_id,
    COUNT(DISTINCT year) AS years_available
FROM profitandloss
GROUP BY company_id
ORDER BY years_available
""", conn)

print(coverage.head(20))

# Companies with < 5 years
print("\n" + "=" * 60)
print("COMPANIES WITH <5 YEARS")
print("=" * 60)

few_years = coverage[
    coverage["years_available"] < 5
]

print(few_years)

conn.close()