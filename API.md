# jetq API Documentation

## Overview

jetq (Python LINQ) is a comprehensive implementation of .NET's Language Integrated Query (LINQ) in Python. It provides a fluent, chainable API for querying and transforming data collections.

## Core Classes

### Queryable[T]

The main class for building and executing LINQ queries. All query operators are methods on this class.

```python
from jetq import Queryable

# Create a queryable from any iterable
query = Queryable([1, 2, 3, 4, 5])
```

## Query Operators

### Filtering Operators

#### where(predicate)
Filters elements based on a predicate function.

```python
# Keep only even numbers
result = Queryable([1, 2, 3, 4, 5]).where(lambda x: x % 2 == 0).to_list()
# Result: [2, 4]
```

#### distinct(key_selector=None)
Removes duplicate elements from the sequence.

```python
result = Queryable([1, 1, 2, 2, 3]).distinct().to_list()
# Result: [1, 2, 3]

# Remove duplicates based on a key
data = [{'id': 1, 'name': 'A'}, {'id': 1, 'name': 'B'}, {'id': 2, 'name': 'C'}]
result = Queryable(data).distinct(lambda x: x['id']).to_list()
```

#### skip(count)
Skips the first N elements.

```python
result = Queryable([1, 2, 3, 4, 5]).skip(2).to_list()
# Result: [3, 4, 5]
```

#### take(count)
Takes only the first N elements.

```python
result = Queryable([1, 2, 3, 4, 5]).take(3).to_list()
# Result: [1, 2, 3]
```

#### skip_while(predicate)
Skips elements while the predicate is true.

```python
result = Queryable([1, 2, 3, 4, 5]).skip_while(lambda x: x < 3).to_list()
# Result: [3, 4, 5]
```

#### take_while(predicate)
Takes elements while the predicate is true.

```python
result = Queryable([1, 2, 3, 4, 5]).take_while(lambda x: x < 4).to_list()
# Result: [1, 2, 3]
```

### Projection Operators

#### select(selector)
Projects each element to a new form.

```python
# Square each number
result = Queryable([1, 2, 3]).select(lambda x: x ** 2).to_list()
# Result: [1, 4, 9]

# Project to different type
people = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
result = Queryable(people).select(lambda p: p['name']).to_list()
# Result: ['Alice', 'Bob']
```

#### select_many(selector)
Projects each element to an iterable and flattens the results.

```python
data = [[1, 2], [3, 4], [5, 6]]
result = Queryable(data).select_many(lambda x: x).to_list()
# Result: [1, 2, 3, 4, 5, 6]
```

#### cast(target_type)
Casts each element to a target type.

```python
result = Queryable(['1', '2', '3']).cast(int).to_list()
# Result: [1, 2, 3]
```

### Ordering Operators

#### order_by(key_selector)
Sorts elements in ascending order.

```python
result = Queryable([3, 1, 4, 1, 5]).order_by(lambda x: x).to_list()
# Result: [1, 1, 3, 4, 5]

# Sort objects by a property
people = [{'name': 'Charlie', 'age': 30}, {'name': 'Alice', 'age': 25}]
result = Queryable(people).order_by(lambda x: x['age']).to_list()
```

#### order_by_descending(key_selector)
Sorts elements in descending order.

```python
result = Queryable([3, 1, 4, 1, 5]).order_by_descending(lambda x: x).to_list()
# Result: [5, 4, 3, 1, 1]
```

#### then_by(key_selector) / then_by_descending(key_selector)
Specifies a secondary sort on an OrderedQueryable.

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

#### reverse()
Reverses the order of elements.

```python
result = Queryable([1, 2, 3]).reverse().to_list()
# Result: [3, 2, 1]
```

### Grouping Operators

#### group_by(key_selector)
Groups elements by a key.

```python
data = [
    {'category': 'A', 'value': 1},
    {'category': 'B', 'value': 2},
    {'category': 'A', 'value': 3}
]
result = Queryable(data).group_by(lambda x: x['category']).to_list()
# Result: [GroupingResult('A', [...]), GroupingResult('B', [...])]

# Access grouped data
for group in result:
    print(f"Key: {group.key}")
    for item in group:
        print(f"  {item}")
```

### Join Operators

#### join(inner, outer_key_selector, inner_key_selector, result_selector)
Performs an inner join between two sequences.

```python
customers = [
    {'id': 1, 'name': 'Alice'},
    {'id': 2, 'name': 'Bob'}
]
orders = [
    {'customer_id': 1, 'product': 'Widget'},
    {'customer_id': 2, 'product': 'Gadget'}
]

result = Queryable(customers).join(
    orders,
    lambda c: c['id'],
    lambda o: o['customer_id'],
    lambda c, o: {'customer': c['name'], 'product': o['product']}
).to_list()
```

#### group_join(inner, outer_key_selector, inner_key_selector, result_selector)
Performs a group join (left join with grouped results).

```python
result = Queryable(customers).group_join(
    orders,
    lambda c: c['id'],
    lambda o: o['customer_id'],
    lambda c, os: {
        'customer': c['name'],
        'order_count': len(os),
        'products': [o['product'] for o in os]
    }
).to_list()
```

### Aggregation Operators

#### count(predicate=None)
Counts the number of elements.

```python
count = Queryable([1, 2, 3, 4, 5]).count()
# Result: 5

# Count with condition
count = Queryable([1, 2, 3, 4, 5]).count(lambda x: x > 3)
# Result: 2
```

#### sum(selector=None)
Sums elements or a projection of elements.

```python
total = Queryable([1, 2, 3, 4, 5]).sum()
# Result: 15

# Sum with selector
products = [{'price': 10}, {'price': 20}]
total = Queryable(products).sum(lambda x: x['price'])
# Result: 30
```

#### average(selector=None)
Calculates the average value.

```python
avg = Queryable([1, 2, 3, 4, 5]).average()
# Result: 3.0

# Average with selector
products = [{'price': 10}, {'price': 20}, {'price': 30}]
avg = Queryable(products).average(lambda x: x['price'])
# Result: 20.0
```

#### min(selector=None) / max(selector=None)
Finds the minimum or maximum element.

```python
min_val = Queryable([5, 2, 8, 1, 9]).min()
# Result: 1

max_val = Queryable([5, 2, 8, 1, 9]).max()
# Result: 9

# With selector
people = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
youngest = Queryable(people).min(lambda x: x['age'])
# Result: {'name': 'Bob', 'age': 25}
```

#### aggregate(func, seed=None)
Applies an accumulator function over the sequence.

```python
# Sum using aggregate
result = Queryable([1, 2, 3, 4, 5]).aggregate(lambda acc, x: acc + x, 0)
# Result: 15

# Build a string
result = Queryable(['a', 'b', 'c']).aggregate(
    lambda acc, x: acc + x,
    ''
)
# Result: 'abc'
```

### Set Operations

#### union(other)
Produces the union of two sequences.

```python
result = Queryable([1, 2, 3]).union([3, 4, 5]).to_list()
# Result: [1, 2, 3, 4, 5] (order may vary)
```

#### intersect(other)
Produces the intersection of two sequences.

```python
result = Queryable([1, 2, 3, 4]).intersect([3, 4, 5, 6]).to_list()
# Result: [3, 4] (order may vary)
```

#### except_(other)
Produces the difference of two sequences.

```python
result = Queryable([1, 2, 3, 4]).except_([3, 4, 5, 6]).to_list()
# Result: [1, 2]
```

### Element Access

#### first(predicate=None)
Gets the first element.

```python
result = Queryable([1, 2, 3]).first()
# Result: 1

# With predicate
result = Queryable([1, 2, 3, 4, 5]).first(lambda x: x > 3)
# Result: 4
```

#### first_or_default(predicate=None, default=None)
Gets the first element or a default value.

```python
result = Queryable([1, 2, 3]).first_or_default(default=0)
# Result: 1

result = Queryable([]).first_or_default(default=0)
# Result: 0
```

#### last(predicate=None) / last_or_default(...)
Gets the last element.

```python
result = Queryable([1, 2, 3]).last()
# Result: 3

result = Queryable([1, 2, 3, 4, 5]).last(lambda x: x < 4)
# Result: 3
```

#### single(predicate=None) / single_or_default(...)
Gets the single element. Throws if zero or more than one element.

```python
result = Queryable([42]).single()
# Result: 42

# Throws ValueError if more than one element
Queryable([1, 2]).single()  # Raises ValueError
```

#### element_at(index) / element_at_or_default(index, default=None)
Gets the element at a specific index.

```python
result = Queryable([10, 20, 30]).element_at(1)
# Result: 20

result = Queryable([10, 20, 30]).element_at_or_default(10, 0)
# Result: 0
```

### Quantifiers

#### any(predicate=None)
Checks if any element matches.

```python
result = Queryable([1, 2, 3]).any()
# Result: True

result = Queryable([1, 2, 3]).any(lambda x: x > 2)
# Result: True

result = Queryable([1, 2, 3]).any(lambda x: x > 10)
# Result: False
```

#### all(predicate)
Checks if all elements match.

```python
result = Queryable([1, 2, 3]).all(lambda x: x > 0)
# Result: True

result = Queryable([1, 2, 3]).all(lambda x: x > 2)
# Result: False
```

#### contains(value, key_selector=None)
Checks if the sequence contains a value.

```python
result = Queryable([1, 2, 3]).contains(2)
# Result: True

result = Queryable([1, 2, 3]).contains(10)
# Result: False
```

### Conversion Operators

#### to_list()
Converts the queryable to a list.

```python
result = Queryable(range(5)).to_list()
# Result: [0, 1, 2, 3, 4]
```

#### to_set()
Converts the queryable to a set (removes duplicates).

```python
result = Queryable([1, 1, 2, 2, 3]).to_set()
# Result: {1, 2, 3}
```

#### to_dict(key_selector) / to_dict_by_key_value(key_selector, value_selector)
Converts the queryable to a dictionary.

```python
data = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
result = Queryable(data).to_dict(lambda x: x['id'])
# Result: {1: {'id': 1, 'name': 'Alice'}, 2: {'id': 2, 'name': 'Bob'}}

result = Queryable(data).to_dict_by_key_value(
    lambda x: x['id'],
    lambda x: x['name']
)
# Result: {1: 'Alice', 2: 'Bob'}
```

#### to_tuple()
Converts the queryable to a tuple.

```python
result = Queryable([1, 2, 3]).to_tuple()
# Result: (1, 2, 3)
```

## Key Concepts

### Deferred Execution

Queries are not executed until you enumerate the results. This allows for efficient composition:

```python
# Query is not executed yet
query = Queryable([1, 2, 3, 4, 5]) \
    .where(lambda x: x > 2) \
    .select(lambda x: x * 2)

# Query is executed here
result = query.to_list()  # [6, 8, 10]
```

### Method Chaining

Most operators return a new Queryable, allowing for fluent method chaining:

```python
result = Queryable(data) \
    .where(lambda x: x['age'] > 25) \
    .select(lambda x: x['name']) \
    .order_by(lambda x: x) \
    .distinct() \
    .to_list()
```

### Type Hints

jetq includes full type hints for better IDE support:

```python
from jetq import Queryable

numbers: Queryable[int] = Queryable([1, 2, 3])
result: list[int] = numbers.where(lambda x: x > 1).to_list()
```

## Performance Considerations

1. **Lazy Evaluation**: Queries are evaluated lazily, so intermediate results aren't materialized until needed.
2. **Streaming**: Most operations can work on infinite or very large iterables without loading everything into memory.
3. **Distinctness**: Operations like `distinct()` and set operations require materializing the sequence into memory.
4. **Ordering**: Sort operations require materializing the sequence.

## Differences from C# LINQ

- Method names use `snake_case` instead of `PascalCase` (e.g., `where` instead of `Where`)
- Use `except_` instead of `Except` to avoid Python keyword conflict
- No expression trees or IQueryProvider implementations for remote data sources yet
- Use standard Python predicates and selectors (lambdas) instead of expression trees

## Examples

### Example 1: Filter, Transform, and Count

```python
result = Queryable(range(1, 11)) \
    .where(lambda x: x % 2 == 0) \
    .select(lambda x: x * x) \
    .count()
# Result: 5 (counts 4, 16, 36, 64, 100)
```

### Example 2: Group and Aggregate

```python
data = [
    {'dept': 'Sales', 'salary': 50000},
    {'dept': 'Engineering', 'salary': 80000},
    {'dept': 'Sales', 'salary': 55000},
]

result = Queryable(data) \
    .group_by(lambda x: x['dept']) \
    .select(lambda g: {
        'department': g.key,
        'avg_salary': Queryable(g).average(lambda x: x['salary'])
    }) \
    .to_list()
```

### Example 3: Complex Join Query

```python
customers = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
orders = [
    {'customer_id': 1, 'product': 'Widget', 'price': 10},
    {'customer_id': 1, 'product': 'Gadget', 'price': 20},
    {'customer_id': 2, 'product': 'Widget', 'price': 10},
]

result = Queryable(customers).group_join(
    orders,
    lambda c: c['id'],
    lambda o: o['customer_id'],
    lambda c, os: {
        'customer': c['name'],
        'total_spent': sum(o['price'] for o in os)
    }
).to_list()
```

## Contributing

To contribute to jetq, please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

jetq is released under the MIT License. See LICENSE file for details.
