"""Test CSV data loading and querying with large datasets."""

import pytest
import csv
import os
from pathlib import Path
from jetq import Queryable


@pytest.fixture
def large_csv_file(tmp_path):
    """Create a CSV file with 10,000 entries for testing."""
    csv_path = tmp_path / "large_dataset.csv"
    
    # Create CSV with 10,000 rows
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'email', 'value', 'category'])
        writer.writeheader()
        
        for i in range(1, 100001):
            writer.writerow({
                'id': i,
                'name': f'User_{i}',
                'email': f'user{i}@example.com',
                'value': i * 10,
                'category': f'Category_{i % 5}'
            })
    
    return csv_path


def load_csv_as_list_of_dicts(csv_path):
    """Load CSV file into a list of dictionaries."""
    rows = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            row['id'] = int(row['id'])
            row['value'] = int(row['value'])
            rows.append(row)
    return rows


def test_select_10_items_from_row_400(large_csv_file):
    """Test selecting 10 items starting from row 400 using Queryable."""
    # Load the CSV
    data = load_csv_as_list_of_dicts(large_csv_file)
    
    # Use Queryable to skip 399 rows (0-indexed) and take 10
    result = (Queryable(data)
              .skip(399)
              .take(10)
              .to_list())
    
    # Verify we got exactly 10 items
    assert len(result) == 10
    
    # Verify the first item is row 400 (id=400, since id starts at 1)
    assert result[0]['id'] == 400
    assert result[0]['name'] == 'User_400'
    
    # Verify the last item is row 409
    assert result[9]['id'] == 409
    assert result[9]['name'] == 'User_409'
    
    # Verify all items are consecutive
    for i, row in enumerate(result):
        assert row['id'] == 400 + i


def test_select_10_items_with_filtering(large_csv_file):
    """Test selecting 10 items with filtering from large dataset."""
    data = load_csv_as_list_of_dicts(large_csv_file)
    
    # Filter for category 0 and take first 10
    result = (Queryable(data)
              .where(lambda x: x['category'] == 'Category_0')
              .take(10)
              .to_list())
    
    assert len(result) == 10
    assert all(row['category'] == 'Category_0' for row in result)


def test_select_10_items_with_projection(large_csv_file):
    """Test selecting 10 items with projection from large dataset."""
    data = load_csv_as_list_of_dicts(large_csv_file)
    
    # Skip 399, take 10, and project to only id and name
    result = (Queryable(data)
              .skip(399)
              .take(10)
              .select(lambda x: {'id': x['id'], 'name': x['name']})
              .to_list())
    
    assert len(result) == 10
    assert all('id' in row and 'name' in row for row in result)
    assert all('email' not in row and 'value' not in row for row in result)


def test_select_10_items_with_ordering(large_csv_file):
    """Test selecting 10 items ordered by value from large dataset."""
    data = load_csv_as_list_of_dicts(large_csv_file)
    
    # Order by value descending, take 10
    ordered = (Queryable(data)
               .order_by_descending(lambda x: x['value'])
               .to_list())
    result = (Queryable(ordered)
              .take(10)
              .to_list())
    
    assert len(result) == 10
    # The highest values should be first
    assert result[0]['value'] == 1000000  # 10000 * 10
    assert result[1]['value'] == 999990   # 9999 * 10
    
    # Verify descending order
    for i in range(len(result) - 1):
        assert result[i]['value'] >= result[i + 1]['value']


def test_skip_and_take_pagination(large_csv_file):
    """Test pagination pattern with skip and take."""
    data = load_csv_as_list_of_dicts(large_csv_file)
    page_size = 10
    page_number = 40  # Get page 40
    
    result = (Queryable(data)
              .skip((page_number - 1) * page_size)
              .take(page_size)
              .to_list())
    
    assert len(result) == page_size
    # Page 40 should contain items 391-400 (0-indexed)
    assert result[0]['id'] == 391
    assert result[-1]['id'] == 400


def test_complex_query_on_large_dataset(large_csv_file):
    """Test complex query combining multiple operations."""
    data = load_csv_as_list_of_dicts(large_csv_file)
    
    # Find rows with value > 4000, order by id desc, skip 5, take 10, project id and value
    ordered = (Queryable(data)
               .where(lambda x: x['value'] > 4000)
               .order_by_descending(lambda x: x['id'])
               .to_list())
    result = (Queryable(ordered)
              .skip(5)
              .take(10)
              .select(lambda x: {'id': x['id'], 'value': x['value']})
              .to_list())
    
    assert len(result) == 10
    assert all(row['value'] > 4000 for row in result)
    # Should be ordered descending
    for i in range(len(result) - 1):
        assert result[i]['id'] >= result[i + 1]['id']


def test_aggregation_on_large_dataset(large_csv_file):
    """Test aggregation operations on large dataset."""
    data = load_csv_as_list_of_dicts(large_csv_file)
    
    # Count total entries
    total_count = Queryable(data).count()
    assert total_count == 100000
    
    # Count entries with value > 50000
    high_value_count = (Queryable(data)
                        .where(lambda x: x['value'] > 500000)
                        .count())
    assert high_value_count == 50000  # Half of 10000
    
    # Verify sum of a subset
    subset_sum = (Queryable(data)
                  .where(lambda x: x['id'] <= 100)
                  .select(lambda x: x['value'])
                  .sum())
    # Sum of values for id 1-100: (1*10 + 2*10 + ... + 100*10) = 10 * (1+2+...+100) = 10 * 5050
    assert subset_sum == 50500


def test_performance_skip_take_from_middle(large_csv_file):
    """Test performance of skip/take from the middle of large dataset."""
    data = load_csv_as_list_of_dicts(large_csv_file)
    
    # Skip to row 5000 and take 10
    result = (Queryable(data)
              .skip(4999)
              .take(10)
              .to_list())
    
    assert len(result) == 10
    assert result[0]['id'] == 5000
    assert result[-1]['id'] == 5009


def test_distinct_on_large_dataset(large_csv_file):
    """Test distinct operation on large dataset."""
    data = load_csv_as_list_of_dicts(large_csv_file)
    
    # Get distinct categories
    categories = (Queryable(data)
                  .select(lambda x: x['category'])
                  .distinct()
                  .to_list())
    
    assert len(categories) == 5  # 5 categories (0-4)
    assert set(categories) == {'Category_0', 'Category_1', 'Category_2', 'Category_3', 'Category_4'}


def test_any_all_on_large_dataset(large_csv_file):
    """Test any and all predicates on large dataset."""
    data = load_csv_as_list_of_dicts(large_csv_file)
    
    # Check if any row has value > 99000
    has_high_value = Queryable(data).any(lambda x: x['value'] > 99000)
    assert has_high_value
    
    # Check if all rows have value > 0
    all_positive = Queryable(data).all(lambda x: x['value'] > 0)
    assert all_positive
    
    # Check if all rows have value > 50000 (should be False)
    all_high = Queryable(data).all(lambda x: x['value'] > 50000)
    assert not all_high
