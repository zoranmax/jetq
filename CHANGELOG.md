# CHANGELOG

All notable changes to PLINQ will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-02-07

### Added

#### Core Features
- Initial implementation of Queryable class with full fluent API
- Support for method chaining and deferred execution
- Type hints for better IDE support and type checking

#### Filtering Operators
- `where()` - Filter elements based on predicate
- `distinct()` - Remove duplicate elements
- `skip()` - Skip first N elements
- `take()` - Take first N elements
- `skip_while()` - Skip while predicate is true
- `take_while()` - Take while predicate is true

#### Projection Operators
- `select()` - Project each element to new form
- `select_many()` - Flatten nested collections
- `cast()` - Cast elements to target type

#### Ordering Operators
- `order_by()` - Sort ascending
- `order_by_descending()` - Sort descending
- `then_by()` - Secondary sort ascending
- `then_by_descending()` - Secondary sort descending
- `reverse()` - Reverse order of elements

#### Grouping Operators
- `group_by()` - Group elements by key

#### Join Operators
- `join()` - Inner join two sequences
- `group_join()` - Left join with grouped results

#### Aggregation Operators
- `count()` - Count elements with optional predicate
- `sum()` - Sum elements or projection
- `average()` - Calculate average value
- `min()` / `max()` - Find minimum or maximum element
- `aggregate()` - Custom accumulator function

#### Set Operations
- `union()` - Combine two sequences
- `intersect()` - Find common elements
- `except_()` - Find difference between sequences

#### Element Access
- `first()` / `first_or_default()` - Get first element
- `last()` / `last_or_default()` - Get last element
- `single()` / `single_or_default()` - Get single element
- `element_at()` / `element_at_or_default()` - Get element at index

#### Quantifiers
- `any()` - Check if any element matches
- `all()` - Check if all elements match
- `contains()` - Check if sequence contains value

#### Conversion
- `to_list()` - Convert to list
- `to_set()` - Convert to set
- `to_dict()` - Convert to dictionary
- `to_dict_by_key_value()` - Convert to dictionary with transformed values
- `to_tuple()` - Convert to tuple

### Project Structure
- Core queryable implementation in `plinq/queryable.py`
- Type definitions in `plinq/types.py`
- Query provider in `plinq/query_provider.py`
- Comprehensive unit tests in `tests.py`
- Extensive examples in `examples.py`
- Full API documentation in `API.md`

### Documentation
- Comprehensive README.md with quick start guide
- Full API documentation with examples for each operator
- Contributing guide for potential contributors
- Code examples demonstrating all major features

## Future Roadmap

### Version 0.2.0
- Expression tree support for LINQ providers
- LINQ to SQL provider
- Performance optimizations
- Async/await support

### Version 0.3.0
- LINQ to REST provider
- Additional utility operators
- Better error messages
- Performance benchmarks

### Version 1.0.0
- Full parity with C# LINQ operators
- Production-ready stability
- Comprehensive documentation
- Wide adoption

## Known Limitations

1. No expression tree support yet (affects LINQ providers)
2. Limited LINQ provider implementations
3. Some operators require materializing sequences in memory
4. No async/await support yet

## Migration Guide

### From C# LINQ

| C# LINQ | PLINQ |
|---------|-------|
| `Where()` | `where()` |
| `Select()` | `select()` |
| `SelectMany()` | `select_many()` |
| `OrderBy()` | `order_by()` |
| `OrderByDescending()` | `order_by_descending()` |
| `GroupBy()` | `group_by()` |
| `Join()` | `join()` |
| `GroupJoin()` | `group_join()` |
| `Count()` | `count()` |
| `Sum()` | `sum()` |
| `Average()` | `average()` |
| `Min()` | `min()` |
| `Max()` | `max()` |
| `Aggregate()` | `aggregate()` |
| `Union()` | `union()` |
| `Intersect()` | `intersect()` |
| `Except()` | `except_()` |
| `First()` | `first()` |
| `FirstOrDefault()` | `first_or_default()` |
| `Last()` | `last()` |
| `LastOrDefault()` | `last_or_default()` |
| `Single()` | `single()` |
| `SingleOrDefault()` | `single_or_default()` |
| `ElementAt()` | `element_at()` |
| `Any()` | `any()` |
| `All()` | `all()` |
| `Contains()` | `contains()` |
| `ToList()` | `to_list()` |
| `ToArray()` | `to_list()` |
| `ToDictionary()` | `to_dict()` |

## Contributors

- Initial implementation: PLINQ Contributors

## License

PLINQ is released under the MIT License.
