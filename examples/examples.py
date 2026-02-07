"""Example usage of jetq."""

from jetq import Queryable


def example_basic_filtering():
    """Example: Basic filtering with where."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Filtering")
    print("=" * 60)
    
    numbers = Queryable([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    
    # Filter for numbers greater than 5
    result = numbers.where(lambda x: x > 5).to_list()
    print(f"Numbers > 5: {result}")
    
    # Filter for even numbers
    result = numbers.where(lambda x: x % 2 == 0).to_list()
    print(f"Even numbers: {result}")
    print()


def example_projection():
    """Example: Transform data with select."""
    print("=" * 60)
    print("EXAMPLE 2: Projection with Select")
    print("=" * 60)
    
    numbers = Queryable([1, 2, 3, 4, 5])
    
    # Square each number
    result = numbers.select(lambda x: x ** 2).to_list()
    print(f"Numbers squared: {result}")
    
    # Project complex objects
    people = [
        {'name': 'Alice', 'age': 30},
        {'name': 'Bob', 'age': 25},
        {'name': 'Charlie', 'age': 35},
    ]
    
    result = Queryable(people).select(lambda p: f"{p['name']} is {p['age']}").to_list()
    print(f"People descriptions: {result}")
    print()


def example_ordering():
    """Example: Sort data with order_by."""
    print("=" * 60)
    print("EXAMPLE 3: Ordering")
    print("=" * 60)
    
    people = [
        {'name': 'Charlie', 'age': 30},
        {'name': 'Alice', 'age': 25},
        {'name': 'Bob', 'age': 25},
    ]
    
    # Sort by age, then by name
    result = Queryable(people) \
        .order_by(lambda x: x['age']) \
        .then_by(lambda x: x['name']) \
        .to_list()
    
    print("Sorted by age, then name:")
    for person in result:
        print(f"  {person['name']}: {person['age']}")
    
    # Sort by salary (descending)
    employees = [
        {'name': 'Alice', 'salary': 50000},
        {'name': 'Bob', 'salary': 75000},
        {'name': 'Charlie', 'salary': 60000},
    ]
    
    result = Queryable(employees).order_by_descending(lambda x: x['salary']).to_list()
    print("\nSorted by salary (highest first):")
    for emp in result:
        print(f"  {emp['name']}: ${emp['salary']}")
    print()


def example_grouping():
    """Example: Group data with group_by."""
    print("=" * 60)
    print("EXAMPLE 4: Grouping")
    print("=" * 60)
    
    sales = [
        {'region': 'North', 'amount': 1000},
        {'region': 'South', 'amount': 1500},
        {'region': 'North', 'amount': 1200},
        {'region': 'East', 'amount': 800},
        {'region': 'South', 'amount': 900},
    ]
    
    # Group by region
    grouped = Queryable(sales).group_by(lambda x: x['region']).to_list()
    
    print("Sales by region:")
    for group in grouped:
        total = sum(item['amount'] for item in group)
        count = len(group)
        print(f"  {group.key}: {count} sales, total: ${total}")
    print()


def example_aggregation():
    """Example: Aggregate data."""
    print("=" * 60)
    print("EXAMPLE 5: Aggregation")
    print("=" * 60)
    
    numbers = Queryable([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    
    print(f"Count: {numbers.count()}")
    print(f"Sum: {numbers.sum()}")
    print(f"Average: {numbers.average()}")
    print(f"Min: {numbers.min()}")
    print(f"Max: {numbers.max()}")
    
    # Count with predicate
    even_count = numbers.count(lambda x: x % 2 == 0)
    print(f"Even numbers: {even_count}")
    
    # Sum with selector
    products = [
        {'name': 'Widget', 'price': 10},
        {'name': 'Gadget', 'price': 20},
        {'name': 'Doohickey', 'price': 15},
    ]
    
    total = Queryable(products).sum(lambda x: x['price'])
    print(f"Total product price: ${total}")
    print()


def example_set_operations():
    """Example: Set operations (union, intersect, except)."""
    print("=" * 60)
    print("EXAMPLE 6: Set Operations")
    print("=" * 60)
    
    a = Queryable([1, 2, 3, 4, 5])
    b = [4, 5, 6, 7, 8]
    
    union_result = a.union(b).to_list()
    print(f"Union: {sorted(union_result)}")
    
    intersect_result = a.intersect(b).to_list()
    print(f"Intersect: {sorted(intersect_result)}")
    
    except_result = a.except_(b).to_list()
    print(f"Except (a - b): {sorted(except_result)}")
    print()


def example_joins():
    """Example: Join operations."""
    print("=" * 60)
    print("EXAMPLE 7: Joins")
    print("=" * 60)
    
    customers = [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'},
        {'id': 3, 'name': 'Charlie'},
    ]
    
    orders = [
        {'customer_id': 1, 'product': 'Widget'},
        {'customer_id': 2, 'product': 'Gadget'},
        {'customer_id': 1, 'product': 'Doohickey'},
        {'customer_id': 2, 'product': 'Widget'},
    ]
    
    # Inner join
    result = Queryable(customers).join(
        orders,
        lambda c: c['id'],
        lambda o: o['customer_id'],
        lambda c, o: f"{c['name']} ordered {o['product']}"
    ).to_list()
    
    print("Customer orders (inner join):")
    for item in result:
        print(f"  {item}")
    
    # Group join
    result = Queryable(customers).group_join(
        orders,
        lambda c: c['id'],
        lambda o: o['customer_id'],
        lambda c, os: {
            'name': c['name'],
            'order_count': len(os),
            'products': [o['product'] for o in os]
        }
    ).to_list()
    
    print("\nCustomer order summary (group join):")
    for item in result:
        print(f"  {item['name']}: {item['order_count']} orders")
        for product in item['products']:
            print(f"    - {product}")
    print()


def example_element_access():
    """Example: Element access operations."""
    print("=" * 60)
    print("EXAMPLE 8: Element Access")
    print("=" * 60)
    
    numbers = Queryable([1, 2, 3, 4, 5])
    
    print(f"First: {numbers.first()}")
    print(f"Last: {numbers.last()}")
    print(f"Element at index 2: {numbers.element_at(2)}")
    
    # With predicates
    result = numbers.first(lambda x: x > 3)
    print(f"First number > 3: {result}")
    
    result = numbers.last(lambda x: x < 4)
    print(f"Last number < 4: {result}")
    
    # Single element
    result = numbers.single(lambda x: x == 3)
    print(f"Single element where x == 3: {result}")
    print()


def example_quantifiers():
    """Example: Quantifier operations (any, all, contains)."""
    print("=" * 60)
    print("EXAMPLE 9: Quantifiers")
    print("=" * 60)
    
    numbers = Queryable([1, 2, 3, 4, 5])
    
    print(f"Any element > 3: {numbers.any(lambda x: x > 3)}")
    print(f"All elements > 0: {numbers.all(lambda x: x > 0)}")
    print(f"All elements > 3: {numbers.all(lambda x: x > 3)}")
    print(f"Contains 3: {numbers.contains(3)}")
    print(f"Contains 10: {numbers.contains(10)}")
    print()


def example_complex_query():
    """Example: Complex chained query."""
    print("=" * 60)
    print("EXAMPLE 10: Complex Chained Query")
    print("=" * 60)
    
    data = [
        {'department': 'Sales', 'name': 'Alice', 'salary': 50000},
        {'department': 'Engineering', 'name': 'Bob', 'salary': 80000},
        {'department': 'Sales', 'name': 'Charlie', 'salary': 55000},
        {'department': 'Engineering', 'name': 'Diana', 'salary': 85000},
        {'department': 'HR', 'name': 'Eve', 'salary': 45000},
    ]
    
    # Complex query: Get departments with average salary > 50k, sorted by average salary
    result = Queryable(data) \
        .group_by(lambda x: x['department']) \
        .select(lambda g: {
            'department': g.key,
            'count': len(g),
            'avg_salary': Queryable(g).select(lambda x: x['salary']).average(),
            'employees': [x['name'] for x in g]
        }) \
        .where(lambda x: x['avg_salary'] > 50000) \
        .order_by(lambda x: -x['avg_salary']) \
        .to_list()
    
    print("Departments with average salary > $50,000:")
    for dept in result:
        print(f"  {dept['department']}: ${dept['avg_salary']:,.0f} average")
        print(f"    Employees: {', '.join(dept['employees'])}")
    print()


if __name__ == '__main__':
    example_basic_filtering()
    example_projection()
    example_ordering()
    example_grouping()
    example_aggregation()
    example_set_operations()
    example_joins()
    example_element_access()
    example_quantifiers()
    example_complex_query()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
