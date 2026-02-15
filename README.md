# jetq - Python LINQ

A Python implementation of .NET's Language Integrated Query (LINQ), providing a functional, fluent API for querying and manipulating collections.

## Overview

jetq brings the power and elegance of C# LINQ to Python, allowing you to write expressive, chainable queries over any iterable collection.

### Key Features

- **Fluent API**: Method chaining for readable, composable queries
- **Deferred Execution**: Lazy evaluation for better performance
- **Rich Operators**: 50+ query operators covering filtering, projection, aggregation, and more
- **Type-Safe**: Full type hints for IDE support and type checking
- **Provider Architecture**: Extensible design supporting different data sources

## Installation

```bash
pip install jetq
```

## Quick Start

```python
from jetq import Queryable

# Basic filtering and projection
numbers = Queryable([1, 2, 3, 4, 5])
result = numbers.where(lambda x: x > 2).select(lambda x: x * 2).to_list()
# Output: [6, 8, 10]

# Grouping and aggregation
data = Queryable([
    {'name': 'Alice', 'age': 30},
    {'name': 'Bob', 'age': 25},
    {'name': 'Charlie', 'age': 30}
])
grouped = data.group_by(lambda x: x['age']).to_list()

# Ordering
sorted_data = numbers.order_by(lambda x: -x).to_list()
# Output: [5, 4, 3, 2, 1]
```

## Core Concepts

### Queryable vs Enumerable

- **Queryable**: Works with any iterable, supports custom query providers
- **Enumerable**: In-memory extension methods for simple queries

### Deferred Execution

Queries are not executed until you enumerate the results:

```python
query = Queryable([1, 2, 3]).where(lambda x: x > 1)  # Not executed yet
result = query.to_list()  # Executed here
```

## Supported Operators

### Filtering
- `where()` - Filter elements based on predicate
- `distinct()` - Remove duplicates
- `skip()` - Skip first N elements
- `take()` - Take first N elements

### Projection
- `select()` - Project each element
- `select_many()` - Flatten nested collections

### Ordering
- `order_by()` - Sort ascending
- `order_by_descending()` - Sort descending
- `then_by()` - Secondary sort
- `then_by_descending()` - Secondary sort descending

### Grouping & Joining
- `group_by()` - Group elements by key
- `join()` - Inner join
- `group_join()` - Left join with grouped results

### Aggregation
- `count()` - Count elements
- `sum()` - Sum values
- `average()` - Average value
- `min()` - Minimum value
- `max()` - Maximum value
- `aggregate()` - Custom aggregation

### Set Operations
- `union()` - Combine sequences
- `intersect()` - Common elements
- `except_()` - Difference

### Element Access
- `first()` - First element
- `first_or_default()` - First or default
- `last()` - Last element
- `single()` - Single element (throws if != 1)
- `element_at()` - Element at index

### Quantifiers
- `any()` - Check if any element matches
- `all()` - Check if all elements match
- `contains()` - Check if contains element

### Conversion
- `to_list()` - Convert to list
- `to_dict()` - Convert to dictionary
- `to_set()` - Convert to set


## Contributing

Contributions are welcome! Areas for improvement:
- Additional query operators
- Performance optimizations
- Custom provider implementations
- More comprehensive tests

## License

MIT License - See LICENSE file for details
