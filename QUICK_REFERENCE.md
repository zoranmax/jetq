# jetq Quick Reference

## Installation

```bash
pip install jetq
```

## Import

```python
from jetq import Queryable
```

## Basic Syntax

```python
result = Queryable(data_source) \
    .operator1(lambda x: condition) \
    .operator2(lambda x: transform) \
    .to_list()
```

## Common Operators

### Filtering
```python
.where(lambda x: x > 5)           # Filter
.distinct()                        # Remove duplicates
.skip(3)                          # Skip first 3
.take(5)                          # Take first 5
```

### Transformation
```python
.select(lambda x: x * 2)          # Transform
.select_many(lambda x: x.items)   # Flatten
.cast(int)                        # Type cast
```

### Sorting
```python
.order_by(lambda x: x)            # Ascending
.order_by_descending(lambda x: x) # Descending
.reverse()                        # Reverse
```

### Grouping & Joining
```python
.group_by(lambda x: x['key'])     # Group by key
.join(other, outer_key, inner_key, result)  # Inner join
.group_join(other, outer_key, inner_key, result)  # Left join
```

### Aggregation
```python
.count()                          # Count all
.count(lambda x: x > 5)           # Count conditional
.sum()                            # Sum values
.average()                        # Average
.min()                            # Minimum
.max()                            # Maximum
.aggregate(func, initial_value)   # Custom aggregate
```

### Set Operations
```python
.union(other)                     # Union
.intersect(other)                 # Intersection
.except_(other)                   # Difference
```

### Element Access
```python
.first()                          # First element
.last()                           # Last element
.single()                         # Single element
.element_at(index)                # Element at index
.first_or_default(default=None)   # First or default
```

### Checking
```python
.any()                            # Any element exists
.any(lambda x: x > 5)             # Any match condition
.all(lambda x: x > 0)             # All match condition
.contains(value)                  # Contains value
```

### Conversion
```python
.to_list()                        # To list
.to_set()                         # To set
.to_dict(lambda x: x['id'])       # To dict
.to_tuple()                       # To tuple
```

## Examples

### Simple Filter and Map
```python
numbers = Queryable([1, 2, 3, 4, 5])
result = numbers.where(lambda x: x > 2).select(lambda x: x * 2).to_list()
# [6, 8, 10]
```

### Grouping and Aggregation
```python
data = [
    {'category': 'A', 'value': 10},
    {'category': 'B', 'value': 20},
    {'category': 'A', 'value': 15}
]

result = Queryable(data) \
    .group_by(lambda x: x['category']) \
    .select(lambda g: {
        'category': g.key,
        'total': Queryable(g).sum(lambda x: x['value'])
    }) \
    .to_list()
```

### Sorting with Multiple Keys
```python
people = [
    {'name': 'Alice', 'age': 30},
    {'name': 'Bob', 'age': 25},
    {'name': 'Charlie', 'age': 25}
]

result = Queryable(people) \
    .order_by(lambda x: x['age']) \
    .then_by(lambda x: x['name']) \
    .to_list()
```

### Joining Data
```python
customers = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
orders = [{'cid': 1, 'product': 'Widget'}, {'cid': 2, 'product': 'Gadget'}]

result = Queryable(customers).join(
    orders,
    lambda c: c['id'],
    lambda o: o['cid'],
    lambda c, o: f"{c['name']} bought {o['product']}"
).to_list()
```

### Complex Chained Query
```python
result = Queryable(range(1, 21)) \
    .where(lambda x: x % 2 == 0) \
    .select(lambda x: x ** 2) \
    .where(lambda x: x > 50) \
    .order_by_descending(lambda x: x) \
    .take(5) \
    .to_list()
# [400, 324, 256, 196, 144]
```

## Key Concepts

### Deferred Execution
Queries are not executed until you call a terminal operator:
```python
query = Queryable([1, 2, 3]).where(lambda x: x > 1)  # Not executed
result = query.to_list()  # Executed here
```

### Method Chaining
All operators return Queryable instances for fluent chaining:
```python
Queryable(data).filter(...).map(...).sort(...).take(...).to_list()
```

### Type Safety
Full type hints for IDE support:
```python
from typing import List
from jetq import Queryable

numbers: Queryable[int] = Queryable([1, 2, 3])
result: List[int] = numbers.where(lambda x: x > 1).to_list()
```

## Differences from C# LINQ

| C# | Python (jetq) |
|----|----------------|
| `.Where()` | `.where()` |
| `.Select()` | `.select()` |
| `.OrderBy()` | `.order_by()` |
| `.GroupBy()` | `.group_by()` |
| `.Except()` | `.except_()` |
| `.FirstOrDefault()` | `.first_or_default()` |

## Tips & Tricks

### Using Multiple Grouping Keys
```python
result = Queryable(data) \
    .group_by(lambda x: (x['dept'], x['year'])) \
    .to_list()
```

### Nested Queries
```python
result = Queryable(groups) \
    .select(lambda g: {
        'key': g.key,
        'avg': Queryable(g).average(lambda x: x['value'])
    }) \
    .to_list()
```

### Conditional Aggregation
```python
by_dept = Queryable(employees).group_by(lambda x: x['dept']).to_list()
result = [
    {
        'dept': g.key,
        'high_earners': Queryable(g).count(lambda x: x['salary'] > 100000)
    }
    for g in by_dept
]
```

### Set Operations
```python
# Combine multiple filters
set_a = Queryable(data).where(lambda x: x > 5).distinct().to_set()
set_b = Queryable(data).where(lambda x: x < 10).distinct().to_set()

# Union, intersect, except
union = Queryable(set_a).union(set_b).to_list()
common = Queryable(set_a).intersect(set_b).to_list()
diff = Queryable(set_a).except_(set_b).to_list()
```

## Documentation

- **Full API**: See `API.md`
- **Examples**: See `examples.py`
- **Testing**: See `test_queryable.py`
- **Contributing**: See `CONTRIBUTING.md`

## Getting Help

1. Check `API.md` for detailed operator documentation
2. Review `examples.py` for usage patterns
3. Look at test cases in `test_queryable.py` for more examples
4. Open an issue on GitHub for bugs or feature requests
