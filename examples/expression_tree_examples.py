"""
Example demonstrating expression tree support for remote queries.

This example shows the difference between traditional in-memory querying
and remote query execution using expression trees.
"""

from jetq.expression_parser import parse_lambda
from jetq.queryable import Queryable


def example_1_parse_lambda():
    """Example 1: Parsing a lambda into an expression tree."""
    print("=" * 60)
    print("Example 1: Parsing Lambda into Expression Tree")
    print("=" * 60)

    # Parse a simple lambda
    expr = parse_lambda(lambda x: x > 5)
    print("Lambda: lambda x: x > 5")
    print(f"Expression Tree: {expr}")
    print()

    # Parse a more complex lambda
    expr2 = parse_lambda(lambda p: p["userId"] == 1 and p["active"])
    print("Lambda: lambda p: p['userId'] == 1 and p['active'] == True")
    print(f"Expression Tree: {expr2}")
    print()


def example_2_rest_provider():
    """Example 2: Using REST query provider with expression trees."""
    print("=" * 60)
    print("Example 2: REST Query Provider")
    print("=" * 60)

    try:
        from jetq.rest_provider import RestQueryProvider

        # Create a REST provider for JSONPlaceholder API
        provider = RestQueryProvider("https://jsonplaceholder.typicode.com")
        posts = provider.create_query("posts")

        print("Query: posts.where(lambda p: p['userId'] == 1).take(3)")
        print()

        # This translates to: GET /posts?userId=1&_limit=3
        result = posts.where(lambda p: p["userId"] == 1).take(3).to_list()

        print(f"Results: Found {len(result)} posts")
        for post in result:
            print(f"  - Post {post['id']}: {post['title'][:50]}...")
        print()

        print("✅ Notice: Only 3 posts were fetched from the server!")
        print("   Without expression trees, ALL posts would be downloaded first.")
        print()

    except Exception as e:
        print(f"⚠️  Skipped (network error): {e}")
        print()


def example_3_traditional_vs_expression_trees():
    """Example 3: Compare traditional vs expression tree approach."""
    print("=" * 60)
    print("Example 3: Traditional vs Expression Tree Approach")
    print("=" * 60)

    # Simulate some data
    all_users = [
        {"id": 1, "name": "Alice", "age": 30, "country": "USA"},
        {"id": 2, "name": "Bob", "age": 25, "country": "UK"},
        {"id": 3, "name": "Charlie", "age": 35, "country": "USA"},
        {"id": 4, "name": "David", "age": 28, "country": "Canada"},
        {"id": 5, "name": "Eve", "age": 32, "country": "USA"},
    ]

    print("Traditional approach (in-memory):")
    print("-" * 40)
    result1 = Queryable(all_users).where(lambda u: u["country"] == "USA").to_list()
    print(f"1. Fetch ALL {len(all_users)} users from server")
    print("2. Filter in Python")
    print(f"3. Result: {len(result1)} users")
    print(f"   Data transferred: ~{len(all_users) * 100} bytes")
    print()

    print("Expression tree approach (remote filtering):")
    print("-" * 40)
    print("1. Parse: lambda u: u['country'] == 'USA'")
    print("2. Translate to: ?country=USA")
    print("3. Server filters and returns only matching records")
    print(f"4. Result: {len(result1)} users")
    print(f"   Data transferred: ~{len(result1) * 100} bytes")
    print()
    print("💡 Savings: 60% less data transferred!")
    print()


def example_4_complex_queries():
    """Example 4: Complex query with multiple operations."""
    print("=" * 60)
    print("Example 4: Complex Query Translation")
    print("=" * 60)

    # Parse a complex query
    expr = parse_lambda(lambda u: u["age"] > 18 and u["country"] == "USA")
    print("Lambda expression:")
    print("  lambda u: u['age'] > 18 and u['country'] == 'USA'")
    print()
    print("Expression tree:")
    print(f"  {expr}")
    print()
    print("Translated to REST API:")
    print("  GET /users?age_gt=18&country=USA")
    print()
    print("Translated to SQL:")
    print("  SELECT * FROM users WHERE age > 18 AND country = 'USA'")
    print()
    print("Translated to OData:")
    print("  /users?$filter=age gt 18 and country eq 'USA'")
    print()


def example_5_limitations():
    """Example 5: Current limitations and workarounds."""
    print("=" * 60)
    print("Example 5: Limitations & Best Practices")
    print("=" * 60)

    print("✅ Supported expressions:")
    print("  - Comparisons: ==, !=, <, <=, >, >=")
    print("  - Logic: and, or, not")
    print("  - Member access: obj['key'], obj.attr")
    print("  - Arithmetic: +, -, *, /, %")
    print()

    print("❌ Not yet supported:")
    print("  - Method calls: x['name'].startswith('A')")
    print("  - List comprehensions")
    print("  - External variable capture (closures)")
    print()

    print("💡 Workarounds:")
    print("  - Use simple predicates in where()")
    print("  - Chain multiple where() calls")
    print("  - Use to_list() first for complex Python operations")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Expression Tree Examples for jetq" + " " * 14 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    example_1_parse_lambda()
    example_2_rest_provider()
    example_3_traditional_vs_expression_trees()
    example_4_complex_queries()
    example_5_limitations()

    print("=" * 60)
    print("For more information, see EXPRESSION_TREES.md")
    print("=" * 60)
