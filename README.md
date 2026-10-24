# SalesVision — Sales Data Analysis Using Python

SalesVision is a beginner-to-intermediate data analysis project that explores order-level sales data, cleans text fields, calculates sales and profit metrics, generates business insights, creates charts, and exports an Excel report.

> **Dataset note:** The included `data/sales_data.csv` is a synthetic sample dataset generated for learning and demonstration. It is not real company data.

## Tools
- Python
- Pandas
- Matplotlib
- Seaborn
- OpenPyXL
- CSV and Excel

## Features
- Validates required dataset columns
- Cleans whitespace and text capitalization
- Converts dates and numeric fields to appropriate types
- Removes duplicate rows and rows missing essential fields
- Recalculates sales and profit consistently
- Summarizes sales by product, category, region, month, and customer segment
- Creates five charts
- Exports cleaned data and analysis tables to an Excel workbook
- Prints key performance indicators and data-backed insights

## Project structure
```text
SalesVision/
├── data/
│   └── sales_data.csv
├── outputs/
│   └── charts/              # Generated when the script runs
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Run locally in VS Code

1. Open this folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create and activate a virtual environment (Windows PowerShell):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install packages:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Run the project:

   ```powershell
   python main.py
   ```

## Outputs
After a successful run, the script creates:
- `outputs/sales_analysis.xlsx` — cleaned data, KPI summary, product/category/region/month/segment analyses, and data-quality summary.
- `outputs/charts/sales_by_product.png`
- `outputs/charts/monthly_sales_trend.png`
- `outputs/charts/sales_by_region.png`
- `outputs/charts/profit_by_category.png`
- `outputs/charts/sales_vs_profit.png`

## Main business questions
- Which product generates the most sales?
- Which category generates the most profit?
- Which region leads by sales?
- Which month has the highest sales?
- What is the overall profit margin?

## Data definitions
- **Sales** = Quantity × Unit Price
- **Profit** = Quantity × (Unit Price − Unit Cost)
- **Profit Margin (%)** = Profit ÷ Sales × 100

## Limitations
This is a portfolio learning project using synthetic data. Findings demonstrate the workflow and should not be treated as actual business recommendations.

## Possible future improvements
- Add SQL queries
- Add automated tests and logging
- Use a public real-world dataset
- Add a lightweight interactive dashboard
