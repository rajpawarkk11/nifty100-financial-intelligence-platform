\# Sprint 2 Retrospective



\## Sprint Goal



Successfully implemented the Financial Ratio Engine and validated financial KPIs for all available company-year records.



\---



\## Completed Work



\- Implemented profitability ratios

\- Implemented leverage and efficiency ratios

\- Implemented CAGR engine

\- Implemented cash flow KPIs

\- Populated financial\_ratios SQLite table

\- Added ROE and ROCE validation

\- Generated ratio\_edge\_cases.log

\- Implemented Financial sector carve-out

\- Created KPI unit tests

\- Verified screener output



\---



\## Formula Decisions



\- ROE = Net Profit / (Equity + Reserves)

\- ROCE = EBIT / (Equity + Reserves + Borrowings)

\- ROA = Net Profit / Total Assets

\- D/E returns 0 for debt-free companies

\- Interest Coverage returns None when Interest = 0

\- CAGR handles turnaround, decline-to-loss, zero-base and insufficient-data cases



\---



\## Edge Cases



\- Negative equity handled

\- Zero denominator handled

\- Debt-free companies handled

\- Financial sector leverage carve-out implemented

\- Source ratio anomalies documented



\---



\## Validation Results



\- Financial Ratios populated: 1175 rows

\- KPI Unit Tests Passed: 42/42

\- Screener Preview: 40 companies

\- Ratio Edge Cases Logged: 1128



\---



\## Sprint Outcome



Sprint 2 completed successfully.

Financial Ratio Engine is ready for analytics and dashboard integration.

