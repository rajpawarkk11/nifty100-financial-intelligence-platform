-- Query 1
SELECT COUNT(*) FROM companies;

-- Query 2
SELECT company_id, COUNT(*) years
FROM profitandloss
GROUP BY company_id
ORDER BY years DESC;

-- Query 3
SELECT company_id, sales
FROM profitandloss
ORDER BY sales DESC
LIMIT 10;

-- Query 4
SELECT company_id, net_profit
FROM profitandloss
ORDER BY net_profit DESC
LIMIT 10;

-- Query 5
SELECT company_id, roe_percentage
FROM companies
ORDER BY roe_percentage DESC
LIMIT 10;

-- Query 6
SELECT company_id, market_cap_crore
FROM market_cap
ORDER BY market_cap_crore DESC
LIMIT 10;

-- Query 7
SELECT broad_sector, COUNT(*)
FROM sectors
GROUP BY broad_sector;

-- Query 8
SELECT company_id, close_price
FROM stock_prices
ORDER BY close_price DESC
LIMIT 10;

-- Query 9
SELECT company_id,
AVG(net_profit_margin_pct) avg_margin
FROM financial_ratios
GROUP BY company_id
ORDER BY avg_margin DESC
LIMIT 10;

-- Query 10
SELECT COUNT(*) FROM stock_prices;