import csv
import json
from pathlib import Path
from datetime import datetime


def read_csv_files(data_dir: str) -> list[dict]:
    """
    Reads all CSV files from a directory using pathlib.glob().

    Args:
        data_dir: Path to the directory containing CSV files.

    Returns:
        List of row dicts from all CSV files combined.
        Returns empty list if no CSV files are found.
    """
    data_path = Path(data_dir)
    all_rows  = []
    csv_files = sorted(data_path.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in '{data_dir}'.")
        return []

    for file in csv_files:
        with open(file, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows   = list(reader)
            all_rows.extend(rows)
            print(f"Read {len(rows)} rows from {file.name}")

    return all_rows


def remove_duplicates(rows: list[dict]) -> list[dict]:
    """
    Removes duplicate rows where all fields match.

    Args:
        rows: List of row dicts to deduplicate.

    Returns:
        List of unique row dicts.
    """
    seen   = set()
    unique = []

    for row in rows:
        key = (
            row.get("date"),
            row.get("product"),
            row.get("qty"),
            row.get("price"),
        )
        if key not in seen:
            seen.add(key)
            unique.append(row)

    print(f"Removed {len(rows) - len(unique)} duplicate row(s).")
    return unique


def calculate_revenue(rows: list[dict]) -> dict[str, float]:
    """
    Computes total revenue per product.
    Revenue = qty * price for each row.

    Args:
        rows: List of unique row dicts.

    Returns:
        Dict mapping product name to total revenue.
    """
    revenue: dict[str, float] = {}

    for row in rows:
        product = row.get("product", "Unknown")
        qty     = int(row.get("qty", 0))
        price   = float(row.get("price", 0))
        revenue[product] = revenue.get(product, 0.0) + (qty * price)

    return revenue


def export_merged_csv(rows: list[dict], output_path: str) -> None:
    """
    Exports all unique rows sorted by date to a CSV file.

    Args:
        rows: List of unique row dicts.
        output_path: Path to write the merged CSV file.
    """
    if not rows:
        print("No rows to export.")
        return

    sorted_rows = sorted(rows, key=lambda r: r.get("date", ""))
    fieldnames  = ["date", "product", "qty", "price"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)

    print(f"Exported {len(sorted_rows)} rows to '{output_path}'.")


def export_revenue_json(
    revenue:         dict[str, float],
    files_processed: int,
    total_rows:      int,
    output_path:     str,
) -> None:
    """
    Exports revenue totals and metadata to a JSON file.

    Args:
        revenue: Dict of product -> total revenue.
        files_processed: Number of CSV files that were read.
        total_rows: Total unique rows after deduplication.
        output_path: Path to write the JSON file.
    """
    total_revenue = round(sum(revenue.values()), 2)

    summary = {
        "metadata": {
            "files_processed": files_processed,
            "total_rows":      total_rows,
            "total_revenue":   total_revenue,
            "generated_at":    datetime.now().isoformat(timespec="seconds"),
        },
        "revenue_by_product": {
            product: round(amount, 2)
            for product, amount in sorted(revenue.items())
        },
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Exported revenue summary to '{output_path}'.")
    print(f"Total revenue: {total_revenue:,.2f}")


def main() -> None:
    """
    Runs the full data merging and reporting pipeline.
    """
    data_dir   = Path("data")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    print("=" * 50)
    print("SALES DATA MERGER")
    print("=" * 50)

    print("\nReading CSV files...")
    all_rows = read_csv_files(data_dir)
    if not all_rows:
        return

    files_processed = len(sorted(data_dir.glob("*.csv")))

    print("\nRemoving duplicates...")
    unique_rows = remove_duplicates(all_rows)

    print("\nCalculating revenue...")
    revenue = calculate_revenue(unique_rows)
    for product, amount in sorted(revenue.items()):
        print(f"  {product}: {amount:,.2f}")

    print("\nExporting merged CSV...")
    export_merged_csv(unique_rows, output_dir / "merged_sales.csv")

    print("\nExporting revenue summary JSON...")
    export_revenue_json(
        revenue,
        files_processed,
        len(unique_rows),
        output_dir / "revenue_summary.json",
    )

    print("\nPipeline complete.")
    print("=" * 50)


if __name__ == "__main__":
    main()
