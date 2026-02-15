"""Unit tests for jetq."""

import pytest

from jetq import Queryable


class TestFiltering:
    """Test filtering operators."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.query = Queryable(self.numbers)

    def test_where(self):
        """Test where operator."""
        result = self.query.where(lambda x: x > 5).to_list()
        assert result == [6, 7, 8, 9, 10]

    def test_distinct(self):
        """Test distinct operator."""
        duplicates = [1, 2, 2, 3, 3, 3, 4]
        result = Queryable(duplicates).distinct().to_list()
        assert result == [1, 2, 3, 4]

    def test_skip(self):
        """Test skip operator."""
        result = self.query.skip(3).to_list()
        assert result == [4, 5, 6, 7, 8, 9, 10]

    def test_take(self):
        """Test take operator."""
        result = self.query.take(5).to_list()
        assert result == [1, 2, 3, 4, 5]

    def test_skip_while(self):
        """Test skip_while operator."""
        result = self.query.skip_while(lambda x: x < 5).to_list()
        assert result == [5, 6, 7, 8, 9, 10]

    def test_take_while(self):
        """Test take_while operator."""
        result = self.query.take_while(lambda x: x < 5).to_list()
        assert result == [1, 2, 3, 4]


class TestProjection:
    """Test projection operators."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.numbers = [1, 2, 3, 4, 5]
        self.query = Queryable(self.numbers)

    def test_select(self):
        """Test select operator."""
        result = self.query.select(lambda x: x * 2).to_list()
        assert result == [2, 4, 6, 8, 10]

    def test_select_many(self):
        """Test select_many operator."""
        data = [[1, 2], [3, 4], [5, 6]]
        result = Queryable(data).select_many(lambda x: x).to_list()
        assert result == [1, 2, 3, 4, 5, 6]

    def test_chained_select(self):
        """Test chaining select operators."""
        result = self.query.select(lambda x: x * 2).select(lambda x: x + 1).to_list()
        assert result == [3, 5, 7, 9, 11]

    def test_cast(self):
        """Test cast operator."""
        strings = ["1", "2", "3", "4", "5"]
        result = Queryable(strings).cast(int).to_list()
        assert result == [1, 2, 3, 4, 5]
        assert all(isinstance(x, int) for x in result)


class TestOrdering:
    """Test ordering operators."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.numbers = [5, 2, 8, 1, 9, 3]
        self.query = Queryable(self.numbers)

    def test_order_by(self):
        """Test order_by operator."""
        result = self.query.order_by(lambda x: x).to_list()
        assert result == [1, 2, 3, 5, 8, 9]

    def test_order_by_descending(self):
        """Test order_by_descending operator."""
        result = self.query.order_by_descending(lambda x: x).to_list()
        assert result == [9, 8, 5, 3, 2, 1]

    def test_then_by(self):
        """Test then_by for secondary sort."""
        data = [
            {"name": "Charlie", "age": 30},
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 25},
        ]
        result = (
            Queryable(data)
            .order_by(lambda x: x["age"])
            .then_by(lambda x: x["name"])
            .to_list()
        )
        assert result[0]["name"] == "Alice"
        assert result[1]["name"] == "Bob"
        assert result[2]["name"] == "Charlie"

    def test_then_by_descending(self):
        """Test then_by_descending for secondary descending sort."""
        data = [
            {"name": "Charlie", "age": 30},
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 25},
        ]
        result = (
            Queryable(data)
            .order_by(lambda x: x["age"])
            .then_by_descending(lambda x: x["name"])
            .to_list()
        )
        assert result[0]["name"] == "Bob"
        assert result[1]["name"] == "Alice"
        assert result[2]["name"] == "Charlie"

    def test_reverse(self):
        """Test reverse operator."""
        result = self.query.reverse().to_list()
        assert result == [3, 9, 1, 8, 2, 5]


class TestOrderedQueryable:
    """Test OrderedQueryable delegated methods."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.numbers = [5, 2, 8, 1, 9, 3]
        self.query = Queryable(self.numbers)

    def test_ordered_where(self):
        """Test where on OrderedQueryable."""
        result = self.query.order_by(lambda x: x).where(lambda x: x > 3).to_list()
        assert result == [5, 8, 9]

    def test_ordered_select(self):
        """Test select on OrderedQueryable."""
        result = self.query.order_by(lambda x: x).select(lambda x: x * 2).to_list()
        assert result == [2, 4, 6, 10, 16, 18]

    def test_ordered_to_dict(self):
        """Test to_dict on OrderedQueryable."""
        data = [
            {"id": 3, "name": "Charlie"},
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        result = Queryable(data).order_by(lambda x: x["id"]).to_dict(lambda x: x["id"])
        assert len(result) == 3
        assert result[1]["name"] == "Alice"

    def test_ordered_count(self):
        """Test count on OrderedQueryable."""
        ordered = self.query.order_by(lambda x: x)
        assert ordered.count() == 6
        assert ordered.count(lambda x: x > 5) == 2


class TestGrouping:
    """Test grouping operators."""

    def test_group_by(self):
        """Test group_by operator."""
        data = [
            {"category": "A", "value": 1},
            {"category": "B", "value": 2},
            {"category": "A", "value": 3},
        ]
        result = Queryable(data).group_by(lambda x: x["category"]).to_list()
        assert len(result) == 2

        # Check that grouping worked
        group_a = next(g for g in result if g.key == "A")
        assert len(group_a) == 2
        assert [item["value"] for item in group_a] == [1, 3]


class TestAggregation:
    """Test aggregation operators."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.numbers = [1, 2, 3, 4, 5]
        self.query = Queryable(self.numbers)

    def test_count(self):
        """Test count operator."""
        assert self.query.count() == 5
        assert self.query.count(lambda x: x > 3) == 2

    def test_sum(self):
        """Test sum operator."""
        assert self.query.sum() == 15

    def test_average(self):
        """Test average operator."""
        assert self.query.average() == 3.0

    def test_min(self):
        """Test min operator."""
        assert self.query.min() == 1

    def test_max(self):
        """Test max operator."""
        assert self.query.max() == 5

    def test_aggregate(self):
        """Test aggregate operator."""
        result = self.query.aggregate(lambda acc, x: acc + x, 0)
        assert result == 15


class TestSetOperations:
    """Test set operations."""

    def test_union(self):
        """Test union operator."""
        a = Queryable([1, 2, 3])
        b = [3, 4, 5]
        result = a.union(b).to_list()
        assert sorted(result) == [1, 2, 3, 4, 5]

    def test_intersect(self):
        """Test intersect operator."""
        a = Queryable([1, 2, 3, 4])
        b = [3, 4, 5, 6]
        result = a.intersect(b).to_list()
        assert sorted(result) == [3, 4]

    def test_except(self):
        """Test except_ operator."""
        a = Queryable([1, 2, 3, 4])
        b = [3, 4, 5, 6]
        result = a.except_(b).to_list()
        assert sorted(result) == [1, 2]


class TestElementAccess:
    """Test element access operators."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.numbers = [1, 2, 3, 4, 5]
        self.query = Queryable(self.numbers)

    def test_first(self):
        """Test first operator."""
        assert self.query.first() == 1
        assert self.query.first(lambda x: x > 3) == 4

    def test_first_or_default(self):
        """Test first_or_default operator."""
        assert self.query.first_or_default(default=0) == 1
        assert self.query.first_or_default(lambda x: x > 10, default=0) == 0

    def test_last(self):
        """Test last operator."""
        assert self.query.last() == 5
        assert self.query.last(lambda x: x < 3) == 2

    def test_last_or_default(self):
        """Test last_or_default operator."""
        assert self.query.last_or_default(default=0) == 5
        assert self.query.last_or_default(lambda x: x > 10, default=0) == 0

    def test_single(self):
        """Test single operator."""
        single_query = Queryable([42])
        assert single_query.single() == 42
        assert self.query.single(lambda x: x == 3) == 3

    def test_single_or_default(self):
        """Test single_or_default operator."""
        single_query = Queryable([42])
        assert single_query.single_or_default() == 42
        assert self.query.single_or_default(lambda x: x == 3) == 3
        assert self.query.single_or_default(lambda x: x > 100, 0) == 0
        empty_query = Queryable([])
        assert empty_query.single_or_default(default=99) == 99

    def test_element_at(self):
        """Test element_at operator."""
        assert self.query.element_at(0) == 1
        assert self.query.element_at(4) == 5

    def test_element_at_or_default(self):
        """Test element_at_or_default operator."""
        assert self.query.element_at_or_default(0, 0) == 1
        assert self.query.element_at_or_default(10, 0) == 0


class TestQuantifiers:
    """Test quantifier operators."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.numbers = [1, 2, 3, 4, 5]
        self.query = Queryable(self.numbers)

    def test_any(self):
        """Test any operator."""
        assert self.query.any()
        assert self.query.any(lambda x: x > 4)
        assert not self.query.any(lambda x: x > 10)

    def test_all(self):
        """Test all operator."""
        assert self.query.all(lambda x: x > 0)
        assert not self.query.all(lambda x: x > 3)

    def test_contains(self):
        """Test contains operator."""
        assert self.query.contains(3)
        assert not self.query.contains(10)


class TestConversion:
    """Test conversion operators."""

    def test_to_list(self):
        """Test to_list conversion."""
        result = Queryable([1, 2, 3]).to_list()
        assert isinstance(result, list)
        assert result == [1, 2, 3]

    def test_to_set(self):
        """Test to_set conversion."""
        result = Queryable([1, 2, 2, 3, 3, 3]).to_set()
        assert isinstance(result, set)
        assert result == {1, 2, 3}

    def test_to_dict(self):
        """Test to_dict conversion."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        result = Queryable(data).to_dict(lambda x: x["id"])
        assert len(result) == 2
        assert result[1]["name"] == "Alice"
        assert result[2]["name"] == "Bob"

    def test_to_dict_by_key_value(self):
        """Test to_dict_by_key_value conversion."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"},
        ]
        result = Queryable(data).to_dict_by_key_value(
            lambda x: x["id"], lambda x: x["name"]
        )
        assert len(result) == 3
        assert result[1] == "Alice"
        assert result[2] == "Bob"
        assert result[3] == "Charlie"

    def test_to_tuple(self):
        """Test to_tuple conversion."""
        result = Queryable([1, 2, 3]).to_tuple()
        assert isinstance(result, tuple)
        assert result == (1, 2, 3)


class TestJoins:
    """Test join operators."""

    def test_join(self):
        """Test join operator."""
        customers = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        orders = [
            {"customer_id": 1, "product": "Widget"},
            {"customer_id": 2, "product": "Gadget"},
            {"customer_id": 1, "product": "Doohickey"},
        ]

        result = (
            Queryable(customers)
            .join(
                orders,
                lambda c: c["id"],
                lambda o: o["customer_id"],
                lambda c, o: {"name": c["name"], "product": o["product"]},
            )
            .to_list()
        )

        assert len(result) == 3
        assert result[0]["name"] == "Alice"
        assert result[0]["product"] == "Widget"

    def test_group_join(self):
        """Test group_join operator."""
        customers = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        orders = [
            {"customer_id": 1, "product": "Widget"},
            {"customer_id": 1, "product": "Doohickey"},
            {"customer_id": 2, "product": "Gadget"},
        ]

        result = (
            Queryable(customers)
            .group_join(
                orders,
                lambda c: c["id"],
                lambda o: o["customer_id"],
                lambda c, os: {"name": c["name"], "orders": [o["product"] for o in os]},
            )
            .to_list()
        )

        assert len(result) == 2
        assert result[0]["name"] == "Alice"
        assert len(result[0]["orders"]) == 2
        assert "Widget" in result[0]["orders"]


class TestComplexQueries:
    """Test complex query scenarios."""

    def test_chained_query(self):
        """Test complex chained query."""
        result = (
            Queryable(range(1, 11))
            .where(lambda x: x % 2 == 0)
            .select(lambda x: x * 2)
            .order_by_descending(lambda x: x)
            .to_list()
        )

        assert result == [20, 16, 12, 8, 4]

    def test_deferred_execution(self):
        """Test that queries are deferred until enumeration."""
        query = Queryable(range(1, 6)).where(lambda x: x > 2)
        # Query not executed yet
        result = query.to_list()
        # Now it's executed
        assert result == [3, 4, 5]

    def test_fluent_complex_query(self):
        """Test complex fluent query with multiple operators."""
        data = [
            {"dept": "Sales", "salary": 50000},
            {"dept": "Engineering", "salary": 80000},
            {"dept": "Sales", "salary": 55000},
            {"dept": "Engineering", "salary": 85000},
        ]

        result = (
            Queryable(data)
            .group_by(lambda x: x["dept"])
            .select(
                lambda g: {
                    "dept": g.key,
                    "avg_salary": Queryable(g).select(lambda x: x["salary"]).average(),
                }
            )
            .to_list()
        )

        assert len(result) == 2

        engineering = next(r for r in result if r["dept"] == "Engineering")
        assert engineering["avg_salary"] == pytest.approx(82500)
