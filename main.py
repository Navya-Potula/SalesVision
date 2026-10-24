from pathlib import Path
import warnings

import matplotlib
matplotlib.use("Agg")  # Allows charts to be saved without opening separate windows.
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# -----------------------------
# SalesVision: project settings
# -----------------------------
PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "data" / "sales_data.csv"
OUTPUT_DIR = PROJECT_DIR / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"
REPORT_FILE = OUTPUT_DIR / "sales_analysis.xlsx"

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["axes.titleweight"] = "bold"
warnings.filterwarnings("ignore", category=FutureWarning)


def load_and_clean_data(file_path: Path) -> tuple[pd.DataFrame, dict]:
    """Load the CSV, validate required fields, and apply safe cleaning."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}\n"
            "Make sure data/sales_data.csv exists inside the SalesVision folder."
        )

    data = pd.read_csv(file_path)
    original_rows = len(data)

    required_columns = [
        "Order_ID", "Order_Date", "Product", "Category", "Region",
        "Segment", "Quantity", "Unit_Price", "Unit_Cost", "Sales", "Profit"
    ]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    # Standardize text fields to avoid differences caused by spaces/capitalization.
    for col in ["Product", "Category", "Region", "Segment"]:
        data[col] = data[col].astype("string").str.strip().str.title()

    data["Order_Date"] = pd.to_datetime(data["Order_Date"], errors="coerce")
    numeric_columns = ["Quantity", "Unit_Price", "Unit_Cost", "Sales", "Profit"]
    for col in numeric_columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    missing_before = int(data.isna().sum().sum())
    data = data.drop_duplicates()
    duplicate_rows_removed = original_rows - len(data)

    # Rows without essential analysis fields cannot be used reliably.
    essential = ["Order_ID", "Order_Date", "Product", "Category", "Region",
                 "Quantity", "Unit_Price", "Unit_Cost"]
    data = data.dropna(subset=essential).copy()

    # Recalculate metrics from source fields to keep values consistent.
    data["Sales"] = (data["Quantity"] * data["Unit_Price"]).round(2)
    data["Profit"] = (data["Quantity"] * (data["Unit_Price"] - data["Unit_Cost"])).round(2)
    data["Profit_Margin_%"] = (
        data["Profit"].div(data["Sales"].replace(0, pd.NA)).fillna(0) * 100
    ).round(2)
    data["Month"] = data["Order_Date"].dt.to_period("M").astype(str)

    cleaning_summary = {
        "Rows in source file": original_rows,
        "Rows after cleaning": len(data),
        "Duplicate rows removed": duplicate_rows_removed,
        "Missing cells found before essential-row cleanup": missing_before,
    }
    return data, cleaning_summary


def create_charts(data: pd.DataFrame) -> list[Path]:
    """Create charts and save them in outputs/charts."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    chart_paths = []

    # 1. Sales by product
    product_sales = data.groupby("Product", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.barplot(data=product_sales, x="Sales", y="Product", color="steelblue", ax=ax)
    ax.set_title("Total Sales by Product")
    ax.set_xlabel("Sales")
    ax.set_ylabel("")
    fig.tight_layout()
    path = CHART_DIR / "sales_by_product.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    chart_paths.append(path)

    # 2. Monthly sales trend
    monthly_sales = data.groupby("Month", as_index=False)["Sales"].sum().sort_values("Month")
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.lineplot(data=monthly_sales, x="Month", y="Sales", marker="o", linewidth=2.5, ax=ax)
    ax.set_title("Monthly Sales Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Sales")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    path = CHART_DIR / "monthly_sales_trend.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    chart_paths.append(path)

    # 3. Sales by region
    region_sales = data.groupby("Region", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=region_sales, x="Region", y="Sales", color="steelblue", ax=ax)
    ax.set_title("Sales by Region")
    ax.set_xlabel("Region")
    ax.set_ylabel("Sales")
    fig.tight_layout()
    path = CHART_DIR / "sales_by_region.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    chart_paths.append(path)

    # 4. Profit by category
    category_profit = data.groupby("Category", as_index=False)["Profit"].sum().sort_values("Profit", ascending=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=category_profit, x="Category", y="Profit", color="steelblue", ax=ax)
    ax.set_title("Total Profit by Category")
    ax.set_xlabel("")
    ax.set_ylabel("Profit")
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    path = CHART_DIR / "profit_by_category.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    chart_paths.append(path)

    # 5. Sales vs profit relationship
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.scatterplot(data=data, x="Sales", y="Profit", hue="Category", alpha=0.75, ax=ax)
    ax.set_title("Order Sales vs Profit")
    fig.tight_layout()
    path = CHART_DIR / "sales_vs_profit.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    chart_paths.append(path)

    return chart_paths


def build_analysis(data: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], list[str]]:
    """Create summary tables and plain-English insights."""
    total_sales = float(data["Sales"].sum())
    total_profit = float(data["Profit"].sum())
    total_orders = int(data["Order_ID"].nunique())
    total_units = int(data["Quantity"].sum())
    overall_margin = (total_profit / total_sales * 100) if total_sales else 0.0

    kpis = pd.DataFrame({
        "Metric": ["Total Sales", "Total Profit", "Profit Margin (%)", "Unique Orders", "Units Sold"],
        "Value": [round(total_sales, 2), round(total_profit, 2), round(overall_margin, 2), total_orders, total_units],
    })

    product_summary = data.groupby("Product", as_index=False).agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Units_Sold=("Quantity", "sum"),
        Orders=("Order_ID", "nunique"),
    ).sort_values("Total_Sales", ascending=False)

    category_summary = data.groupby("Category", as_index=False).agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Average_Profit_Margin_Pct=("Profit_Margin_%", "mean"),
    ).sort_values("Total_Profit", ascending=False)

    region_summary = data.groupby("Region", as_index=False).agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Orders=("Order_ID", "nunique"),
    ).sort_values("Total_Sales", ascending=False)

    monthly_summary = data.groupby("Month", as_index=False).agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Orders=("Order_ID", "nunique"),
    ).sort_values("Month")

    segment_summary = data.groupby("Segment", as_index=False).agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Orders=("Order_ID", "nunique"),
    ).sort_values("Total_Sales", ascending=False)

    top_product = product_summary.iloc[0]
    top_region = region_summary.iloc[0]
    top_category_profit = category_summary.sort_values("Total_Profit", ascending=False).iloc[0]
    best_month = monthly_summary.loc[monthly_summary["Total_Sales"].idxmax()]

    insights = [
        f"Total sales were {total_sales:,.2f} across {total_orders:,} unique orders.",
        f"Total profit was {total_profit:,.2f} with an overall profit margin of {overall_margin:.2f}%.",
        f"{top_product['Product']} was the top product by sales ({top_product['Total_Sales']:,.2f}).",
        f"{top_region['Region']} was the leading region by sales ({top_region['Total_Sales']:,.2f}).",
        f"{top_category_profit['Category']} generated the highest total profit ({top_category_profit['Total_Profit']:,.2f}).",
        f"{best_month['Month']} was the strongest month by sales ({best_month['Total_Sales']:,.2f}).",
    ]
    summaries = {
        "KPI Summary": kpis,
        "Product Analysis": product_summary,
        "Category Analysis": category_summary,
        "Region Analysis": region_summary,
        "Monthly Analysis": monthly_summary,
        "Segment Analysis": segment_summary,
    }
    return kpis, summaries, insights


def save_excel_report(data: pd.DataFrame, summaries: dict[str, pd.DataFrame], cleaning: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cleaning_df = pd.DataFrame({"Cleaning Check": list(cleaning.keys()), "Result": list(cleaning.values())})
    with pd.ExcelWriter(REPORT_FILE, engine="openpyxl") as writer:
        data.to_excel(writer, sheet_name="Cleaned Data", index=False)
        for sheet_name, table in summaries.items():
            table.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        cleaning_df.to_excel(writer, sheet_name="Data Quality", index=False)


def main() -> None:
    print("\n" + "=" * 56)
    print("                 SALESVISION")
    print("          Sales Data Analysis Project")
    print("=" * 56)

    data, cleaning = load_and_clean_data(DATA_FILE)
    kpis, summaries, insights = build_analysis(data)
    charts = create_charts(data)
    save_excel_report(data, summaries, cleaning)

    print("\nDATA QUALITY")
    for key, value in cleaning.items():
        print(f"  {key}: {value}")

    print("\nKEY PERFORMANCE INDICATORS")
    print(kpis.to_string(index=False))

    print("\nTOP PRODUCTS BY SALES")
    print(summaries["Product Analysis"].head(5).to_string(index=False))

    print("\nBUSINESS INSIGHTS")
    for number, insight in enumerate(insights, start=1):
        print(f"  {number}. {insight}")

    print("\nFILES CREATED")
    print(f"  Excel report: {REPORT_FILE.relative_to(PROJECT_DIR)}")
    for chart in charts:
        print(f"  Chart: {chart.relative_to(PROJECT_DIR)}")

    print("\nProject completed successfully!")
    print("Tip: Open outputs/charts to view your charts and outputs/sales_analysis.xlsx for the report.\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("\nProject could not finish. Details:")
        print(error)
        raise
