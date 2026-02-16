"""Examples of querying CSV files with jetq using expression trees.

This module demonstrates how to use jetq's CSV query provider to efficiently
query CSV files without loading the entire file into memory.
"""

import csv
import tempfile
from pathlib import Path

from jetq import from_csv


def create_sample_csv():
    """Create a sample CSV file for examples."""
    temp_dir = Path(tempfile.mkdtemp())
    csv_path = temp_dir / "employees.csv"

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id", "name", "department", "age", "salary"]
        )
        writer.writeheader()
        writer.writerows(
            [
                {
                    "id": "1",
                    "name": "Alice Johnson",
                    "department": "Engineering",
                    "age": "30",
                    "salary": "85000",
                },
                {
                    "id": "2",
                    "name": "Bob Smith",
                    "department": "Sales",
                    "age": "25",
                    "salary": "65000",
                },
                {
                    "id": "3",
                    "name": "Charlie Davis",
                    "department": "Engineering",
                    "age": "35",
                    "salary": "95000",
                },
                {
                    "id": "4",
                    "name": "Diana Wilson",
                    "department": "Marketing",
                    "age": "28",
                    "salary": "72000",
                },
                {
                    "id": "5",
                    "name": "Eve Brown",
                    "department": "Engineering",
                    "age": "32",
                    "salary": "88000",
                },
                {
                    "id": "6",
                    "name": "Frank Miller",
                    "department": "Sales",
                    "age": "45",
                    "salary": "78000",
                },
                {
                    "id": "7",
                    "name": "Grace Lee",
                    "department": "Marketing",
                    "age": "29",
                    "salary": "75000",
                },
                {
                    "id": "8",
                    "name": "Henry Taylor",
                    "department": "Engineering",
                    "age": "38",
                    "salary": "98000",
                },
                {
                    "id": "9",
                    "name": "Iris Anderson",
                    "department": "Sales",
                    "age": "26",
                    "salary": "68000",
                },
                {
                    "id": "10",
                    "name": "Jack Thomas",
                    "department": "Engineering",
                    "age": "41",
                    "salary": "105000",
                },
            ]
        )

    return csv_path


def example_1_basic_filtering():
    """Example 1: Basic filtering with where clause."""
    print("=" * 60)
    print("Example 1: Basic Filtering")
    print("=" * 60)

    csv_path = create_sample_csv()

    # Find all engineers
    engineers = (
        from_csv(csv_path).where(lambda e: e["department"] == "Engineering").to_list()
    )

    print(f"\nEngineers ({len(engineers)} found):")
    for emp in engineers:
        print(f"  - {emp['name']} (Age: {emp['age']}, Salary: ${emp['salary']})")

    csv_path.unlink()


def example_2_numeric_filtering():
    """Example 2: Filtering with numeric comparisons."""
    print("\n" + "=" * 60)
    print("Example 2: Numeric Filtering")
    print("=" * 60)

    csv_path = create_sample_csv()

    # Find high earners using type converters
    high_earners = (
        from_csv(csv_path, type_converters={"age": int, "salary": float})
        .where(lambda e: e["salary"] > 85000)
        .to_list()
    )

    print(f"\nHigh Earners (Salary > $85,000) - {len(high_earners)} found:")
    for emp in high_earners:
        print(f"  - {emp['name']}: ${emp['salary']:,.0f}")

    csv_path.unlink()


def example_3_complex_filtering():
    """Example 3: Complex filtering with AND/OR conditions."""
    print("\n" + "=" * 60)
    print("Example 3: Complex Filtering")
    print("=" * 60)

    csv_path = create_sample_csv()

    # Find experienced engineers or sales people
    results = (
        from_csv(csv_path, type_converters={"age": int})
        .where(
            lambda e: (
                (e["department"] == "Engineering" and e["age"] > 35)
                or e["department"] == "Sales"
            )
        )
        .to_list()
    )

    print(f"\nExperienced Engineers (Age > 35) OR Sales People - {len(results)} found:")
    for emp in results:
        print(f"  - {emp['name']}: {emp['department']} (Age: {emp['age']})")

    csv_path.unlink()


def example_4_chained_queries():
    """Example 4: Chaining multiple query operations."""
    print("\n" + "=" * 60)
    print("Example 4: Chained Query Operations")
    print("=" * 60)

    csv_path = create_sample_csv()

    # Chain multiple operations
    results = (
        from_csv(csv_path, type_converters={"age": int, "salary": float})
        .where(lambda e: e["age"] >= 28)
        .where(lambda e: e["salary"] > 70000)
        .skip(1)  # Skip the first match
        .take(3)  # Take only 3 results
        .to_list()
    )

    print("\nEmployees (Age >= 28, Salary > $70k, Skip 1, Take 3):")
    for emp in results:
        print(f"  - {emp['name']}: Age {emp['age']}, ${emp['salary']:,.0f}")

    csv_path.unlink()


def example_5_projection():
    """Example 5: Projecting/transforming results with select."""
    print("\n" + "=" * 60)
    print("Example 5: Projection with Select")
    print("=" * 60)

    csv_path = create_sample_csv()

    # Project to a simplified format
    summary = (
        from_csv(csv_path, type_converters={"age": int, "salary": float})
        .where(lambda e: e["department"] == "Engineering")
        .select(
            lambda e: {
                "employee": e["name"],
                "info": f"{e['age']} years, ${e['salary']:,.0f}",
            }
        )
        .to_list()
    )

    print("\nEngineering Department Summary:")
    for item in summary:
        print(f"  - {item['employee']}: {item['info']}")

    csv_path.unlink()


def example_6_pagination():
    """Example 6: Implementing pagination."""
    print("\n" + "=" * 60)
    print("Example 6: Pagination")
    print("=" * 60)

    csv_path = create_sample_csv()

    page_size = 3
    page_number = 2  # Get page 2 (0-indexed)

    page_results = (
        from_csv(csv_path, type_converters={"salary": float})
        .skip(page_number * page_size)
        .take(page_size)
        .select(lambda e: f"{e['name']} - {e['department']}")
        .to_list()
    )

    print(
        f"\nPage {page_number + 1} (Items {page_number * page_size + 1}-{(page_number + 1) * page_size}):"
    )
    for i, item in enumerate(page_results, start=1):
        print(f"  {i}. {item}")

    csv_path.unlink()


def example_7_first_and_count():
    """Example 7: Using first() and count() methods."""
    print("\n" + "=" * 60)
    print("Example 7: First and Count Operations")
    print("=" * 60)

    csv_path = create_sample_csv()

    query = from_csv(csv_path, type_converters={"age": int, "salary": float})

    # Find the first person over 35
    first_senior = query.where(lambda e: e["age"] > 35).first()
    print(
        f"\nFirst employee over 35: {first_senior['name']} (Age: {first_senior['age']})"
    )

    # Count engineers
    engineer_count = query.where(lambda e: e["department"] == "Engineering").count()
    print(f"Total engineers: {engineer_count}")

    # Count high earners
    high_earner_count = query.where(lambda e: e["salary"] > 80000).count()
    print(f"Employees earning > $80k: {high_earner_count}")

    csv_path.unlink()


def example_8_streaming_large_files():
    """Example 8: Efficiently querying large CSV files."""
    print("\n" + "=" * 60)
    print("Example 8: Streaming Large Files")
    print("=" * 60)

    # Create a larger CSV file
    temp_dir = Path(tempfile.mkdtemp())
    csv_path = temp_dir / "large_data.csv"

    print("\nCreating large CSV with 10,000 rows...")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "value", "category"])
        writer.writeheader()
        for i in range(1, 10001):
            writer.writerow(
                {"id": str(i), "value": str(i * 100), "category": f"Cat_{i % 10}"}
            )

    print("Querying large file (streaming - never loads all rows into memory)...")

    # The CSV provider streams rows, so this only processes matching rows
    results = (
        from_csv(csv_path, type_converters={"value": int})
        .where(lambda r: r["category"] == "Cat_5")
        .where(lambda r: r["value"] > 500000)
        .take(5)
        .to_list()
    )

    print(f"\nFound {len(results)} results (stopped after finding 5):")
    for row in results:
        print(
            f"  - ID: {row['id']}, Value: {row['value']}, Category: {row['category']}"
        )

    print("\n✓ Query completed efficiently without loading 10,000 rows into memory!")

    csv_path.unlink()


def example_9_comparison_traditional_vs_expression_trees():
    """Example 9: Compare traditional vs expression tree approach."""
    print("\n" + "=" * 60)
    print("Example 9: Traditional vs Expression Trees")
    print("=" * 60)

    csv_path = create_sample_csv()

    print("\n--- Traditional Approach (Load All, Then Filter) ---")
    print("Code:")
    print("  rows = []")
    print("  with open(csv_path) as f:")
    print("      reader = csv.DictReader(f)")
    print("      for row in reader:")
    print("          row['age'] = int(row['age'])")
    print("          rows.append(row)")
    print(
        "  result = [r for r in rows if r['age'] > 30 and r['department'] == 'Engineering']"
    )
    print("\nIssues:")
    print("  × Loads ALL 10 rows into memory")
    print("  × Manual type conversion for each row")
    print("  × More verbose code")

    print("\n--- Expression Tree Approach (Filter While Reading) ---")
    print("Code:")
    print("  result = (")
    print("      from_csv(csv_path, type_converters={'age': int})")
    print("      .where(lambda e: e['age'] > 30 and e['department'] == 'Engineering')")
    print("      .to_list()")
    print("  )")
    print("\nBenefits:")
    print("  ✓ Only loads matching rows into memory")
    print("  ✓ Automatic type conversion")
    print("  ✓ LINQ-style fluent API")
    print("  ✓ Expression trees allow query optimization")

    # Actually run the query
    result = (
        from_csv(csv_path, type_converters={"age": int})
        .where(lambda e: e["age"] > 30 and e["department"] == "Engineering")
        .to_list()
    )

    print(f"\nResult: Found {len(result)} matching employees")
    for emp in result:
        print(f"  - {emp['name']}: Age {emp['age']}")

    csv_path.unlink()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("CSV Query Examples with Expression Trees")
    print("jetq - Python LINQ for CSV Files")
    print("=" * 60)

    example_1_basic_filtering()
    example_2_numeric_filtering()
    example_3_complex_filtering()
    example_4_chained_queries()
    example_5_projection()
    example_6_pagination()
    example_7_first_and_count()
    example_8_streaming_large_files()
    example_9_comparison_traditional_vs_expression_trees()

    print("\n" + "=" * 60)
    print("All examples completed successfully! ✓")
    print("=" * 60)


if __name__ == "__main__":
    main()
