#!/usr/bin/env python3
"""Quick validation script for jetq."""

import sys

sys.path.insert(0, ".")

from jetq import Queryable

print("Testing jetq Implementation")
print("=" * 60)

# Test 1: Basic filtering
print("\n1. Testing basic filtering...")
numbers = Queryable([1, 2, 3, 4, 5])
result = numbers.where(lambda x: x > 2).to_list()
assert result == [3, 4, 5], f"Expected [3, 4, 5], got {result}"
print("✓ Filtering works")

# Test 2: Projection
print("2. Testing projection...")
result = Queryable([1, 2, 3]).select(lambda x: x * 2).to_list()
assert result == [2, 4, 6], f"Expected [2, 4, 6], got {result}"
print("✓ Projection works")

# Test 3: Ordering
print("3. Testing ordering...")
result = Queryable([3, 1, 4, 1, 5]).order_by(lambda x: x).to_list()
assert result == [1, 1, 3, 4, 5], f"Expected [1, 1, 3, 4, 5], got {result}"
print("✓ Ordering works")

# Test 4: Aggregation
print("4. Testing aggregation...")
result = Queryable([1, 2, 3, 4, 5]).sum()
assert result == 15, f"Expected 15, got {result}"
result = Queryable([1, 2, 3, 4, 5]).average()
assert result == 3.0, f"Expected 3.0, got {result}"
print("✓ Aggregation works")

# Test 5: Grouping
print("5. Testing grouping...")
data = [
    {"category": "A", "value": 1},
    {"category": "B", "value": 2},
    {"category": "A", "value": 3},
]
result = Queryable(data).group_by(lambda x: x["category"]).to_list()
assert len(result) == 2, f"Expected 2 groups, got {len(result)}"
print("✓ Grouping works")

# Test 6: Set operations
print("6. Testing set operations...")
a = Queryable([1, 2, 3])
b = [3, 4, 5]
result = a.intersect(b).to_list()
assert sorted(result) == [3], f"Expected [3], got {sorted(result)}"
print("✓ Set operations work")

# Test 7: Joining
print("7. Testing joins...")
customers = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]
orders = [
    {"customer_id": 1, "product": "Widget"},
    {"customer_id": 2, "product": "Gadget"},
]
result = (
    Queryable(customers)
    .join(
        orders,
        lambda c: c["id"],
        lambda o: o["customer_id"],
        lambda c, o: f"{c['name']} ordered {o['product']}",
    )
    .to_list()
)
assert len(result) == 2, f"Expected 2 results, got {len(result)}"
print("✓ Joins work")

# Test 8: Complex query
print("8. Testing complex chained query...")
result = (
    Queryable(range(1, 11))
    .where(lambda x: x % 2 == 0)
    .select(lambda x: x * 2)
    .order_by_descending(lambda x: x)
    .to_list()
)
assert result == [20, 16, 12, 8, 4], f"Expected [20, 16, 12, 8, 4], got {result}"
print("✓ Complex queries work")

print("\n" + "=" * 60)
print("All tests passed! ✓")
print("=" * 60)
print("\njetq is working correctly!")
