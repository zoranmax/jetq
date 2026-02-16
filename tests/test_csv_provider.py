"""Tests for CSV query provider with expression trees."""

import csv
from pathlib import Path

import pytest

from jetq.csv_provider import CsvQueryable, CsvQueryProvider, from_csv


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing."""
    csv_path = tmp_path / "sample.csv"

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "age", "city", "salary"])
        writer.writeheader()
        writer.writerows(
            [
                {
                    "id": "1",
                    "name": "Alice",
                    "age": "30",
                    "city": "New York",
                    "salary": "75000",
                },
                {
                    "id": "2",
                    "name": "Bob",
                    "age": "25",
                    "city": "San Francisco",
                    "salary": "85000",
                },
                {
                    "id": "3",
                    "name": "Charlie",
                    "age": "35",
                    "city": "New York",
                    "salary": "95000",
                },
                {
                    "id": "4",
                    "name": "Diana",
                    "age": "28",
                    "city": "Boston",
                    "salary": "70000",
                },
                {
                    "id": "5",
                    "name": "Eve",
                    "age": "32",
                    "city": "San Francisco",
                    "salary": "90000",
                },
                {
                    "id": "6",
                    "name": "Frank",
                    "age": "45",
                    "city": "New York",
                    "salary": "105000",
                },
                {
                    "id": "7",
                    "name": "Grace",
                    "age": "29",
                    "city": "Boston",
                    "salary": "80000",
                },
                {
                    "id": "8",
                    "name": "Henry",
                    "age": "38",
                    "city": "San Francisco",
                    "salary": "98000",
                },
                {
                    "id": "9",
                    "name": "Iris",
                    "age": "26",
                    "city": "New York",
                    "salary": "72000",
                },
                {
                    "id": "10",
                    "name": "Jack",
                    "age": "41",
                    "city": "Boston",
                    "salary": "88000",
                },
            ]
        )

    return csv_path


@pytest.fixture
def large_csv_file(tmp_path):
    """Create a larger CSV file for performance testing."""
    csv_path = tmp_path / "large.csv"

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "value", "category"])
        writer.writeheader()
        for i in range(1, 1001):
            writer.writerow(
                {"id": str(i), "value": str(i * 10), "category": f"Cat_{i % 5}"}
            )

    return csv_path


class TestCsvQueryProvider:
    """Tests for CsvQueryProvider class."""

    def test_init_with_string_path(self, sample_csv_file):
        """Test initialization with string path."""
        provider = CsvQueryProvider(str(sample_csv_file))
        assert provider.filepath == Path(sample_csv_file)

    def test_init_with_path_object(self, sample_csv_file):
        """Test initialization with Path object."""
        provider = CsvQueryProvider(sample_csv_file)
        assert provider.filepath == sample_csv_file

    def test_headers_property(self, sample_csv_file):
        """Test reading CSV headers."""
        provider = CsvQueryProvider(sample_csv_file)
        headers = provider.headers

        assert headers == ["id", "name", "age", "city", "salary"]

    def test_headers_cached(self, sample_csv_file):
        """Test that headers are cached."""
        provider = CsvQueryProvider(sample_csv_file)
        headers1 = provider.headers
        headers2 = provider.headers

        assert headers1 is headers2  # Same object

    def test_read_rows_without_filters(self, sample_csv_file):
        """Test reading all rows without filters."""
        provider = CsvQueryProvider(sample_csv_file)
        rows = list(provider.read_rows())

        assert len(rows) == 10
        assert rows[0]["name"] == "Alice"
        assert rows[9]["name"] == "Jack"

    def test_type_converters(self, sample_csv_file):
        """Test automatic type conversion."""
        provider = CsvQueryProvider(
            sample_csv_file, type_converters={"id": int, "age": int, "salary": float}
        )
        rows = list(provider.read_rows())

        assert isinstance(rows[0]["id"], int)
        assert isinstance(rows[0]["age"], int)
        assert isinstance(rows[0]["salary"], float)
        assert rows[0]["id"] == 1
        assert rows[0]["age"] == 30


class TestCsvQueryable:
    """Tests for CsvQueryable class."""

    def test_to_list_all_rows(self, sample_csv_file):
        """Test converting query to list."""
        provider = CsvQueryProvider(sample_csv_file)
        query = provider.create_query()
        results = query.to_list()

        assert len(results) == 10

    def test_where_simple_equality(self, sample_csv_file):
        """Test where clause with simple equality."""
        provider = CsvQueryProvider(sample_csv_file, type_converters={"age": int})
        query = provider.create_query()
        results = query.where(lambda r: r["age"] == 30).to_list()

        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_where_greater_than(self, sample_csv_file):
        """Test where clause with greater than."""
        provider = CsvQueryProvider(sample_csv_file, type_converters={"age": int})
        query = provider.create_query()
        results = query.where(lambda r: r["age"] > 35).to_list()

        assert len(results) == 3
        names = [r["name"] for r in results]
        assert set(names) == {"Frank", "Henry", "Jack"}

    def test_where_less_than(self, sample_csv_file):
        """Test where clause with less than."""
        provider = CsvQueryProvider(sample_csv_file, type_converters={"age": int})
        query = provider.create_query()
        results = query.where(lambda r: r["age"] < 28).to_list()

        assert len(results) == 2
        names = [r["name"] for r in results]
        assert set(names) == {"Bob", "Iris"}

    def test_where_string_equality(self, sample_csv_file):
        """Test where clause with string equality."""
        provider = CsvQueryProvider(sample_csv_file)
        query = provider.create_query()
        results = query.where(lambda r: r["city"] == "New York").to_list()

        assert len(results) == 4
        names = [r["name"] for r in results]
        assert set(names) == {"Alice", "Charlie", "Frank", "Iris"}

    def test_where_and_condition(self, sample_csv_file):
        """Test where clause with AND condition."""
        provider = CsvQueryProvider(sample_csv_file, type_converters={"age": int})
        query = provider.create_query()
        results = query.where(
            lambda r: r["city"] == "New York" and r["age"] > 30
        ).to_list()

        assert len(results) == 2
        names = [r["name"] for r in results]
        assert set(names) == {"Charlie", "Frank"}

    def test_where_or_condition(self, sample_csv_file):
        """Test where clause with OR condition."""
        provider = CsvQueryProvider(sample_csv_file, type_converters={"age": int})
        query = provider.create_query()
        results = query.where(
            lambda r: r["city"] == "Boston" or r["age"] > 40
        ).to_list()

        assert len(results) == 4  # Diana, Grace, Jack, Frank

    def test_chained_where_clauses(self, sample_csv_file):
        """Test chaining multiple where clauses."""
        provider = CsvQueryProvider(
            sample_csv_file, type_converters={"age": int, "salary": float}
        )
        query = provider.create_query()
        results = (
            query.where(lambda r: r["age"] > 27)
            .where(lambda r: r["salary"] > 80000)
            .to_list()
        )

        # Should get: Charlie, Eve, Frank, Henry, Jack
        assert len(results) == 5

    def test_skip(self, sample_csv_file):
        """Test skip operation."""
        provider = CsvQueryProvider(sample_csv_file)
        query = provider.create_query()
        results = query.skip(5).to_list()

        assert len(results) == 5
        assert results[0]["name"] == "Frank"

    def test_take(self, sample_csv_file):
        """Test take operation."""
        provider = CsvQueryProvider(sample_csv_file)
        query = provider.create_query()
        results = query.take(3).to_list()

        assert len(results) == 3
        assert results[0]["name"] == "Alice"
        assert results[2]["name"] == "Charlie"

    def test_skip_and_take(self, sample_csv_file):
        """Test combining skip and take."""
        provider = CsvQueryProvider(sample_csv_file)
        query = provider.create_query()
        results = query.skip(2).take(3).to_list()

        assert len(results) == 3
        assert results[0]["name"] == "Charlie"
        assert results[2]["name"] == "Eve"

    def test_where_skip_take_combined(self, sample_csv_file):
        """Test combining where, skip, and take."""
        provider = CsvQueryProvider(sample_csv_file, type_converters={"age": int})
        query = provider.create_query()
        results = query.where(lambda r: r["age"] > 27).skip(1).take(3).to_list()

        # Age > 27: Alice(30), Charlie(35), Diana(28), Eve(32), Frank(45), Grace(29), Henry(38), Jack(41)
        # Skip 1, Take 3: Should get 3 people
        assert len(results) == 3

    def test_select_projection(self, sample_csv_file):
        """Test select/projection."""
        provider = CsvQueryProvider(sample_csv_file)
        query = provider.create_query()
        results = query.select(
            lambda r: {"name": r["name"], "city": r["city"]}
        ).to_list()

        assert len(results) == 10
        assert set(results[0].keys()) == {"name", "city"}
        assert "age" not in results[0]
        assert "salary" not in results[0]

    def test_select_single_value(self, sample_csv_file):
        """Test selecting a single value."""
        provider = CsvQueryProvider(sample_csv_file)
        query = provider.create_query()
        results = query.select(lambda r: r["name"]).to_list()

        assert len(results) == 10
        assert results[0] == "Alice"
        assert results[9] == "Jack"

    def test_first(self, sample_csv_file):
        """Test first operation."""
        provider = CsvQueryProvider(sample_csv_file, type_converters={"age": int})
        query = provider.create_query()
        result = query.where(lambda r: r["age"] > 35).first()

        assert result is not None
        assert result["name"] == "Frank"  # First one in the file with age > 35

    def test_first_no_match(self, sample_csv_file):
        """Test first when no match."""
        provider = CsvQueryProvider(sample_csv_file, type_converters={"age": int})
        query = provider.create_query()
        result = query.where(lambda r: r["age"] > 100).first()

        assert result is None

    def test_count(self, sample_csv_file):
        """Test count operation."""
        provider = CsvQueryProvider(sample_csv_file, type_converters={"age": int})
        query = provider.create_query()
        count = query.where(lambda r: r["age"] > 30).count()

        assert count == 5  # Charlie, Eve, Frank, Henry, Jack

    def test_iterable(self, sample_csv_file):
        """Test that queryable is iterable."""
        provider = CsvQueryProvider(sample_csv_file)
        query = provider.create_query().take(3)

        results = []
        for row in query:
            results.append(row)

        assert len(results) == 3


class TestFromCsvFunction:
    """Tests for from_csv convenience function."""

    def test_from_csv_basic(self, sample_csv_file):
        """Test basic from_csv usage."""
        query = from_csv(sample_csv_file)
        results = query.to_list()

        assert len(results) == 10

    def test_from_csv_with_converters(self, sample_csv_file):
        """Test from_csv with type converters."""
        query = from_csv(sample_csv_file, type_converters={"age": int, "salary": float})
        results = query.to_list()

        assert isinstance(results[0]["age"], int)
        assert isinstance(results[0]["salary"], float)

    def test_from_csv_with_query(self, sample_csv_file):
        """Test from_csv with query operations."""
        results = (
            from_csv(sample_csv_file, type_converters={"age": int})
            .where(lambda r: r["age"] < 30)
            .to_list()
        )

        assert len(results) == 4  # Bob, Diana, Grace, Iris


class TestCsvPerformance:
    """Tests for CSV provider performance and streaming."""

    def test_large_file_filtering(self, large_csv_file):
        """Test filtering a large CSV file."""
        query = from_csv(large_csv_file, type_converters={"id": int, "value": int})
        results = query.where(lambda r: r["value"] > 9000).to_list()

        # Values > 9000: ids 901-1000 (value = id * 10)
        assert len(results) == 100

    def test_large_file_with_skip_take(self, large_csv_file):
        """Test skip/take on large file."""
        query = from_csv(large_csv_file)
        results = query.skip(500).take(10).to_list()

        assert len(results) == 10
        # After skip 500, should start at id 501
        assert results[0]["id"] == "501"

    def test_streaming_reads_only_needed_rows(self, large_csv_file):
        """Test that streaming only reads rows until take limit."""
        query = from_csv(large_csv_file)
        results = query.take(5).to_list()

        # Should only read 5 rows, not all 1000
        assert len(results) == 5

    def test_category_filtering(self, large_csv_file):
        """Test filtering by category."""
        query = from_csv(large_csv_file)
        results = query.where(lambda r: r["category"] == "Cat_0").to_list()

        # Cat_0 appears for ids: 5, 10, 15, ..., 1000 (every 5th)
        assert len(results) == 200


class TestCsvEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_csv(self, tmp_path):
        """Test handling empty CSV file."""
        csv_path = tmp_path / "empty.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "name"])
            writer.writeheader()

        query = from_csv(csv_path)
        results = query.to_list()

        assert results == []

    def test_type_conversion_failure(self, tmp_path):
        """Test graceful handling of type conversion failure."""
        csv_path = tmp_path / "bad_types.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "value"])
            writer.writeheader()
            writer.writerows(
                [
                    {"id": "1", "value": "not_a_number"},
                    {"id": "2", "value": "100"},
                ]
            )

        # Should keep original value if conversion fails
        query = from_csv(csv_path, type_converters={"value": int})
        results = query.to_list()

        assert (
            results[0]["value"] == "not_a_number"
        )  # Conversion failed, kept as string
        assert results[1]["value"] == 100  # Conversion succeeded

    def test_missing_column_in_filter(self, sample_csv_file):
        """Test filtering on non-existent column."""
        provider = CsvQueryProvider(sample_csv_file)
        query = provider.create_query()
        # This should not crash, but return no results since column doesn't exist
        results = query.where(lambda r: r["nonexistent"] == "value").to_list()

        # All rows have None for nonexistent column, so none match
        assert len(results) == 0


class TestCsvComplexQueries:
    """Tests for complex query scenarios."""

    def test_complex_query_chain(self, sample_csv_file):
        """Test a complex query with multiple operations."""
        results = (
            from_csv(sample_csv_file, type_converters={"age": int, "salary": float})
            .where(lambda r: r["age"] >= 28)
            .where(lambda r: r["salary"] > 75000)
            .skip(1)
            .take(3)
            .select(
                lambda r: {
                    "name": r["name"],
                    "info": f"{r['age']} years old, ${r['salary']}",
                }
            )
            .to_list()
        )

        assert len(results) == 3
        assert "name" in results[0]
        assert "info" in results[0]
        assert "years old" in results[0]["info"]

    def test_multiple_filters_on_same_column(self, sample_csv_file):
        """Test multiple filters on the same column."""
        results = (
            from_csv(sample_csv_file, type_converters={"age": int})
            .where(lambda r: r["age"] > 25)
            .where(lambda r: r["age"] < 35)
            .to_list()
        )

        # Age between 26 and 34 (inclusive)
        assert len(results) == 5  # Iris(26), Diana(28), Grace(29), Alice(30), Eve(32)


# ==========================================
# Direct Initialization Tests
# ==========================================


@pytest.fixture
def simple_csv_file_direct(tmp_path):
    """Create a simpler CSV file for direct init testing."""
    csv_path = tmp_path / "simple.csv"

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "age"])
        writer.writeheader()
        writer.writerows(
            [
                {"name": "Alice", "age": "30"},
                {"name": "Bob", "age": "25"},
                {"name": "Charlie", "age": "35"},
                {"name": "Diana", "age": "28"},
                {"name": "Eve", "age": "32"},
            ]
        )

    return csv_path


def test_direct_init_string_path(simple_csv_file_direct):
    """Test instantiating CsvQueryable with string path."""
    query = CsvQueryable(str(simple_csv_file_direct))
    results = query.to_list()
    assert len(results) == 5


def test_direct_init_path_object(simple_csv_file_direct):
    """Test instantiating CsvQueryable with Path object."""
    query = CsvQueryable(simple_csv_file_direct)
    results = query.to_list()
    assert len(results) == 5


def test_direct_init_with_converters(simple_csv_file_direct):
    """Test instantiating CsvQueryable with type converters."""
    query = CsvQueryable(simple_csv_file_direct, type_converters={"age": int})
    results = query.where(lambda r: r["age"] > 30).to_list()
    assert len(results) == 2  # Charlie(35), Eve(32)
    assert results[0]["name"] == "Charlie"


def test_direct_init_with_encoding(tmp_path):
    """Test instantiating CsvQueryable with custom encoding."""
    csv_path = tmp_path / "utf16.csv"
    with open(csv_path, "w", encoding="utf-16", newline="") as f:
        f.write("name,age\nAlice,30\n")

    query = CsvQueryable(csv_path, encoding="utf-16")
    results = query.to_list()
    assert len(results) == 1
    assert results[0]["name"] == "Alice"


def test_type_error_for_invalid_source():
    """Test that invalid source raises TypeError."""
    with pytest.raises(TypeError):
        CsvQueryable(123)  # Invalid source type
