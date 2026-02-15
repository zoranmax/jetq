# Contributing to jetq

Thank you for your interest in contributing to jetq! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions with other contributors and users.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip or another package manager
- Git

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/jetq.git
cd jetq
```

2. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
pip install -e .
```

## Development Process

### Running Tests

```bash
# Run all tests
pytest ./tests 

# Run with coverage
pytest ./tests --cov=jetq

# Run specific test
pytest ./tests/tests.py::TestFiltering::test_where
```

### Code Style

We follow PEP 8 conventions. Use the following tools:

```bash
# Format code and sort imports
ruff format jetq/
ruff check --fix --select I jetq/

# Lint code
ruff check jetq/

# Type checking
mypy jetq/
```

### Documentation

- Add docstrings to all public functions and classes
- Update API.md for new operators
- Include examples in docstrings
- Update README.md if adding significant features

## Making Changes

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### Implementing New Operators

1. Add the operator method to the `Queryable` class in `jetq/queryable.py`
2. Write comprehensive docstring with examples
3. Add unit tests in `tests.py`
4. Update `API.md` documentation
5. Add usage example in `examples.py` if appropriate

### Example Operator Implementation

```python
def your_new_operator(self, parameter: str) -> 'Queryable[T]':
    """Short description of what this operator does.
    
    Args:
        parameter: Description of parameter.
    
    Returns:
        A new Queryable with transformed elements.
        
    Example:
        >>> result = Queryable([1, 2, 3]).your_new_operator('param').to_list()
        >>> result
        [...]
    """
    def operator_generator():
        for item in self:
            # Implementation here
            yield processed_item
    
    return Queryable(operator_generator())
```

### Example Test Implementation

```python
class TestYourOperator(unittest.TestCase):
    """Test your_new_operator."""
    
    def test_basic_usage(self):
        """Test basic functionality."""
        result = Queryable([...]).your_new_operator('param').to_list()
        self.assertEqual(result, [...])
    
    def test_edge_case(self):
        """Test edge case."""
        # Test implementation
        pass
```

## Commit Guidelines

- Write clear, descriptive commit messages
- Use present tense ("Add feature" not "Added feature")
- Keep commits focused on single changes
- Format: `type: description`

Examples:
```
feat: Add except_ operator for set difference
fix: Handle empty sequences in grouping
docs: Update API documentation
test: Add tests for complex chained queries
```

## Pull Request Process

1. Ensure all tests pass locally (for all python versions)
2. Update documentation as needed
3. Add or update tests for new functionality
4. Fill out the PR template completely
5. Link any related issues
6. Request review from maintainers

### PR Checklist

- [ ] Tests pass locally (`pytest ./tests`)
- [ ] Code follows style guidelines (`task format`, `task lint`)
- [ ] Documentation is updated
- [ ] Examples are provided
- [ ] Commit messages are clear
- [ ] No new warnings in type checking

## Areas for Contribution

### High Priority

- [ ] Expression tree support for remote queries
- [ ] Additional LINQ providers (SQL, REST, etc.)
- [ ] Performance optimizations
- [ ] More comprehensive error handling

### Medium Priority

- [ ] Additional utility operators
- [ ] Better error messages
- [ ] Performance benchmarks
- [ ] Integration tests

### Low Priority

- [ ] Code style improvements
- [ ] Documentation improvements
- [ ] Example additions
- [ ] Comment clarifications

## Reporting Issues

When reporting a bug:

1. Use clear, descriptive title
2. Describe exact reproduction steps
3. Provide minimal code example
4. Include Python version and environment
5. Include error message and traceback if applicable

## Asking Questions

For questions:

1. Check existing documentation and examples
2. Search existing issues
3. Ask in a new issue with "question:" prefix
4. Join our community discussions

## Code Review

All submissions require review. We look for:

- Correctness and robustness
- Code style and readability
- Test coverage
- Documentation quality
- Performance impact

## License

By contributing to jetq, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- CHANGELOG.md

## Questions?

Feel free to open an issue or contact the maintainers. Thank you for contributing!
