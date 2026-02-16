#!/usr/bin/env python3
"""Simple CSV query example that demonstrates working functionality."""

import csv
import tempfile
from pathlib import Path

from jetq import from_csv

# Create a sample CSV file
temp_dir = Path(tempfile.mkdtemp())
csv_path = temp_dir / "employees.csv"

print("Creating sample employees.csv...")
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "department", "age", "salary"])
    writer.writeheader()
    writer.writerows(
        [
            {
                "name": "Alice",
                "department": "Engineering",
                "age": "30",
                "salary": "85000",
            },
            {"name": "Bob", "department": "Sales", "age": "25", "salary": "65000"},
            {
                "name": "Charlie",
                "department": "Engineering",
                "age": "35",
                "salary": "95000",
            },
            {
                "name": "Diana",
                "department": "Marketing",
                "age": "28",
                "salary": "72000",
            },
            {
                "name": "Eve",
                "department": "Engineering",
                "age": "32",
                "salary": "88000",
            },
        ]
    )

print(f"CSV file created at: {csv_path}\n")

# Example 1: Filter by department
print("=" * 60)
print("Example 1: Find all engineers")
print("=" * 60)
engineers = (
    from_csv(csv_path).where(lambda e: e["department"] == "Engineering").to_list()
)
print(f"Found {len(engineers)} engineers:")
for emp in engineers:
    print(f"  - {emp['name']} (Age: {emp['age']})")

# Example 2: Filter by age with type conversion
print("\n" + "=" * 60)
print("Example 2: Find employees over 30")
print("=" * 60)
query = from_csv(csv_path, type_converters={"age": int})
over_30 = query.where(lambda e: e["age"] > 30).to_list()
print(f"Found {len(over_30)} employees over 30:")
for emp in over_30:
    print(f"  - {emp['name']}: {emp['age']} years old")

# Example 3: Combine with logical AND
print("\n" + "=" * 60)
print("Example 3: Engineers over 30")
print("=" * 60)
query = from_csv(csv_path, type_converters={"age": int})
senior_engineers = query.where(
    lambda e: e["age"] > 30 and e["department"] == "Engineering"
).to_list()
print(f"Found {len(senior_engineers)} senior engineers:")
for emp in senior_engineers:
    print(f"  - {emp['name']}: {emp['age']} years old")

# Example 4: Projection with select
print("\n" + "=" * 60)
print("Example 4: Get just names")
print("=" * 60)
names = from_csv(csv_path).select(lambda e: e["name"]).to_list()
print(f"All employee names: {', '.join(names)}")

# Example 5: Pagination
print("\n" + "=" * 60)
print("Example 5: Skip 2, take 2")
print("=" * 60)
page = from_csv(csv_path).skip(2).take(2).to_list()
print("Page results:")
for emp in page:
    print(f"  - {emp['name']}")

# Example 6: First match
print("\n" + "=" * 60)
print("Example 6: First employee in Marketing")
print("=" * 60)
first_marketer = (
    from_csv(csv_path).where(lambda e: e["department"] == "Marketing").first()
)
if first_marketer:
    print(f"First marketer: {first_marketer['name']}")

# Example 7: Count
print("\n" + "=" * 60)
print("Example 7: Count engineers")
print("=" * 60)
eng_count = from_csv(csv_path).where(lambda e: e["department"] == "Engineering").count()
print(f"Number of engineers: {eng_count}")

print("\n" + "=" * 60)
print("All examples completed successfully! ✓")
print("=" * 60)

# Cleanup
csv_path.unlink()
