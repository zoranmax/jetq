# Expression Tree Support for Remote Queries

## Overview

Expression trees enable jetq to translate LINQ queries into remote query languages (SQL, OData, REST APIs, etc.) instead of fetching all data and filtering in Python.

## The Problem

Without expression trees, when you write:
```python
Queryable(posts).where(lambda p: p["userId"] == 1).to_list()
```

If `posts` comes from a REST API or database, jetq must:
1. Fetch **ALL** data from the remote source
2. Filter it in Python memory

This is inefficient for large remote datasets.

## The Solution: Expression Trees

With expression trees, jetq can:
1. **Parse** the lambda function into an AST (Abstract Syntax Tree)
2. **Translate** the AST into the remote query language
3. **Execute** the translated query on the remote server
4. **Return** only the filtered results

### Example with REST API

```python
from jetq.rest_provider import RestQueryable

# Create a queryable directly
posts = RestQueryable("https://jsonplaceholder.typicode.com", "posts")

# This translates to: GET /posts?userId=1
result = posts.where(lambda p: p['userId'] == 1).to_list()
```

**Before (no expression trees):**
- Downloads all 100 posts
- Filters in Python
- Total data transferred: ~50KB

**After (with expression trees):**
- Translates to `?userId=1` query parameter
- Server filters and returns only 10 posts
- Total data transferred: ~5KB

## Architecture

### 1. Expression Classes (`jetq/expressions.py`)

Defines AST node types:
```python
class Expression(ABC):
    """Base class for all expression nodes"""
    
class BinaryExpression(Expression):
    """Represents: left op right"""
    # Example: x > 5
    
class MemberExpression(Expression):
    """Represents: obj.field or obj['key']"""
    # Example: p['userId']
    
class ConstantExpression(Expression):
    """Represents: literal values"""
    # Example: 1, "hello", True
```

### 2. Lambda Parser (`jetq/expression_parser.py`)

Converts Python lambdas to expression trees:
```python
from jetq.expression_parser import parse_lambda

expr = parse_lambda(lambda x: x['userId'] == 1)
print(expr)
# Output: Lambda([x], Binary(equal, Member(x['userId']), Constant(1)))
```

### 3. Expression Visitor (`jetq/expressions.py`)

Base class for translating expressions:
```python
class ExpressionVisitor(ABC):
    def visit_equal(self, expression: BinaryExpression):
        # Translate equality to SQL: field = value
        # Or OData: field eq value
        # Or REST: ?field=value
```

### 4. Query Providers

Implement specific translation logic:

#### REST Query Provider (`jetq/rest_provider.py`)
```python
class RestQueryProvider:
    def execute_query(self, query_expr):
        # Translate filters to query parameters
        # Build URL: /resource?field=value
        # Execute HTTP GET request
```

#### OData Query Provider (example)
```python
class ODataQueryProvider:
    def translate_filter(self, expr):
        # x > 5 -> "$filter=x gt 5"
        # x == "test" -> "$filter=x eq 'test'"
```

#### SQL Query Provider (example)
```python
class SqlQueryProvider:
    def translate_filter(self, expr):
        # x > 5 -> "WHERE x > 5"
        # x == 1 and y == 2 -> "WHERE x = 1 AND y = 2"
```

## Implementation Steps

### Phase 1: Core Expression Tree Support
- [x] Create expression classes
- [x] Implement lambda parser using Python AST
- [x] Create expression visitor base class
- [ ] Add comprehensive unit tests
- [ ] Handle edge cases (closures, method calls, etc.)

### Phase 2: Query Provider Infrastructure
- [x] Create REST query provider example
- [ ] Extend Queryable to support expression-based providers
- [ ] Implement query composition (combine multiple where clauses)
- [ ] Add support for select(), order_by(), etc.

### Phase 3: Specific Provider Implementations
- [ ] **OData Provider** - Microsoft OData protocol
- [ ] **SQL Provider** - Generate SQL queries (SQLAlchemy integration)
- [ ] **GraphQL Provider** - Translate to GraphQL queries
- [ ] **Elasticsearch Provider** - Generate ES query DSL

### Phase 4: Advanced Features
- [ ] **Query optimization** - Combine multiple filters before execution
- [ ] **Caching** - Cache expression tree parsing results
- [ ] **Async support** - Async query execution for remote providers
- [ ] **Type inference** - Better type safety for remote queries

## Usage Examples

### Example 1: Basic REST Query
```python
from jetq.rest_provider import RestQueryable

users = RestQueryable("https://api.example.com", "users")

# Single filter
active_users = users.where(lambda u: u['active'] == True).to_list()
# Translates to: GET /users?active=true

# Multiple filters with AND
admin_users = users.where(lambda u: u['role'] == 'admin' and u['active'] == True).to_list()
# Translates to: GET /users?role=admin&active=true

# Pagination
first_10 = users.skip(0).take(10).to_list()
# Translates to: GET /users?_start=0&_limit=10
```

### Example 2: Complex Query with Chaining
```python
result = (users
    .where(lambda u: u['age'] > 18)
    .where(lambda u: u['country'] == 'USA')
    .order_by(lambda u: u['name'])
    .skip(20)
    .take(10)
    .to_list())

# Translates to: GET /users?age_gt=18&country=USA&_sort=name&_order=asc&_start=20&_limit=10
```

### Example 3: SQL Query Provider (Future)
```python
from jetq.sql_provider import SqlQueryProvider

provider = SqlQueryProvider("postgresql://localhost/mydb")
products = provider.create_query("products")

# This generates and executes:
# SELECT * FROM products WHERE price > 100 AND category = 'electronics' ORDER BY price
result = (products
    .where(lambda p: p.price > 100)
    .where(lambda p: p.category == 'electronics')
    .order_by(lambda p: p.price)
    .to_list())
```

## Limitations & Challenges

### Current Limitations

1. **Lambda Scope**: Only works with parseable lambdas
   ```python
   # ✅ Works - simple lambda
   .where(lambda x: x['id'] > 5)
   
   # ❌ Won't work - references external variable
   min_id = 5
   .where(lambda x: x['id'] > min_id)  # Need closure support
   ```

2. **Complex Expressions**: Some Python features can't be translated
   ```python
   # ❌ Can't translate arbitrary method calls
   .where(lambda x: x['name'].startswith('A'))
   
   # ✅ Basic operators work
   .where(lambda x: x['name'] == 'Alice')
   ```

3. **Provider-Specific**: Each provider needs its own translator
   - REST APIs have different conventions
   - SQL dialects differ
   - NoSQL databases have unique query languages

### Solutions

1. **Closure Support**: Capture variable values during parsing
   ```python
   min_id = 5
   expr = parse_lambda(lambda x: x['id'] > min_id)
   # Resolve min_id to Constant(5) in the expression tree
   ```

2. **Fallback to Local Execution**: If translation fails, execute in Python
   ```python
   try:
       # Try remote execution
       result = provider.execute_query(expr)
   except TranslationError:
       # Fall back to in-memory filtering
       result = fetch_all().where(lambda x: ...)
   ```

3. **Standard Query Model**: Create intermediate representation
   ```python
   # Parse to generic model
   generic_query = parse_to_generic(lambda x: x > 5)
   
   # Each provider translates from generic model
   sql = SqlTranslator().translate(generic_query)
   odata = ODataTranslator().translate(generic_query)
   ```

## Testing Strategy

### Unit Tests
```python
def test_parse_simple_equality():
    expr = parse_lambda(lambda x: x['id'] == 1)
    assert isinstance(expr.body, BinaryExpression)
    assert expr.body.expression_type == ExpressionType.EQUAL

def test_rest_provider_translation():
    provider = RestQueryProvider("https://api.test")
    query = provider.create_query("users").where(lambda u: u['id'] == 1)
    
    # Verify URL generation
    url = provider._build_url(query)
    assert url == "https://api.test/users?id=1"
```

### Integration Tests
```python
def test_rest_provider_real_api():
    """Test with real JSONPlaceholder API"""
    provider = RestQueryProvider("https://jsonplaceholder.typicode.com")
    posts = provider.create_query("posts")
    
    result = posts.where(lambda p: p['userId'] == 1).to_list()
    assert len(result) == 10
    assert all(p['userId'] == 1 for p in result)
```

## Performance Considerations

### Benefits
- **Reduced data transfer**: Filter on server, not client
- **Lower memory usage**: Don't load entire dataset
- **Faster queries**: Use server-side indexing
- **Scalability**: Handle datasets larger than memory

### Costs
- **Parsing overhead**: AST parsing adds small latency (~1ms)
- **Translation complexity**: More code to maintain
- **Limited expressiveness**: Can't translate all Python features

### Optimization Strategies
1. **Cache parsed expressions**: Same lambda = same tree
2. **Batch operations**: Combine multiple where() into one filter
3. **Lazy execution**: Only execute when enumerating
4. **Query hints**: Allow manual query string specification

## Contributing

To add a new query provider:

1. **Extend ExpressionVisitor** to translate expressions:
   ```python
   class MyProviderTranslator(ExpressionVisitor):
       def visit_equal(self, expr):
           # Translate to your query language
   ```

2. **Create QueryProvider class**:
   ```python
   class MyQueryProvider:
       def execute_query(self, query_expr):
           # Execute the query
   ```

3. **Add tests**:
   ```python
   def test_my_provider():
       provider = MyQueryProvider(...)
       # Test translation and execution
   ```

4. **Document limitations**: What expressions can/can't be translated

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

## Resources

- **Python AST module**: https://docs.python.org/3/library/ast.html
- **C# LINQ Expression Trees**: https://docs.microsoft.com/en-us/dotnet/csharp/expression-trees
- **OData Query Protocol**: https://www.odata.org/documentation/
- **SQLAlchemy Core**: https://docs.sqlalchemy.org/en/stable/core/

## Future Work

- [ ] Support for SELECT projection (translate select() to field selection)
- [ ] Support for JOIN operations (translate join() to remote joins)
- [ ] Support for GROUP BY aggregation (translate group_by() to remote aggregation)
- [ ] Async/await support for remote queries
- [ ] Query plan visualization and debugging
- [ ] Performance monitoring and query statistics
- [ ] Connection pooling for database providers
- [ ] Retry logic and error handling for remote failures
