"""Unit tests for jetq."""

import unittest
from jetq import Queryable, GroupingResult


class TestFiltering(unittest.TestCase):
    """Test filtering operators."""
    
    def setUp(self):
        """Set up test data."""
        self.numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.query = Queryable(self.numbers)
    
    def test_where(self):
        """Test where operator."""
        result = self.query.where(lambda x: x > 5).to_list()
        self.assertEqual(result, [6, 7, 8, 9, 10])
    
    def test_distinct(self):
        """Test distinct operator."""
        duplicates = [1, 2, 2, 3, 3, 3, 4]
        result = Queryable(duplicates).distinct().to_list()
        self.assertEqual(result, [1, 2, 3, 4])
    
    def test_skip(self):
        """Test skip operator."""
        result = self.query.skip(3).to_list()
        self.assertEqual(result, [4, 5, 6, 7, 8, 9, 10])
    
    def test_take(self):
        """Test take operator."""
        result = self.query.take(5).to_list()
        self.assertEqual(result, [1, 2, 3, 4, 5])
    
    def test_skip_while(self):
        """Test skip_while operator."""
        result = self.query.skip_while(lambda x: x < 5).to_list()
        self.assertEqual(result, [5, 6, 7, 8, 9, 10])
    
    def test_take_while(self):
        """Test take_while operator."""
        result = self.query.take_while(lambda x: x < 5).to_list()
        self.assertEqual(result, [1, 2, 3, 4])


class TestProjection(unittest.TestCase):
    """Test projection operators."""
    
    def setUp(self):
        """Set up test data."""
        self.numbers = [1, 2, 3, 4, 5]
        self.query = Queryable(self.numbers)
    
    def test_select(self):
        """Test select operator."""
        result = self.query.select(lambda x: x * 2).to_list()
        self.assertEqual(result, [2, 4, 6, 8, 10])
    
    def test_select_many(self):
        """Test select_many operator."""
        data = [[1, 2], [3, 4], [5, 6]]
        result = Queryable(data).select_many(lambda x: x).to_list()
        self.assertEqual(result, [1, 2, 3, 4, 5, 6])
    
    def test_chained_select(self):
        """Test chaining select operators."""
        result = self.query.select(lambda x: x * 2).select(lambda x: x + 1).to_list()
        self.assertEqual(result, [3, 5, 7, 9, 11])


class TestOrdering(unittest.TestCase):
    """Test ordering operators."""
    
    def setUp(self):
        """Set up test data."""
        self.numbers = [5, 2, 8, 1, 9, 3]
        self.query = Queryable(self.numbers)
    
    def test_order_by(self):
        """Test order_by operator."""
        result = self.query.order_by(lambda x: x).to_list()
        self.assertEqual(result, [1, 2, 3, 5, 8, 9])
    
    def test_order_by_descending(self):
        """Test order_by_descending operator."""
        result = self.query.order_by_descending(lambda x: x).to_list()
        self.assertEqual(result, [9, 8, 5, 3, 2, 1])
    
    def test_then_by(self):
        """Test then_by for secondary sort."""
        data = [
            {'name': 'Charlie', 'age': 30},
            {'name': 'Alice', 'age': 25},
            {'name': 'Bob', 'age': 25},
        ]
        result = Queryable(data).order_by(lambda x: x['age']).then_by(lambda x: x['name']).to_list()
        self.assertEqual(result[0]['name'], 'Alice')
        self.assertEqual(result[1]['name'], 'Bob')
        self.assertEqual(result[2]['name'], 'Charlie')
    
    def test_reverse(self):
        """Test reverse operator."""
        result = self.query.reverse().to_list()
        self.assertEqual(result, [3, 9, 1, 8, 2, 5])


class TestGrouping(unittest.TestCase):
    """Test grouping operators."""
    
    def test_group_by(self):
        """Test group_by operator."""
        data = [
            {'category': 'A', 'value': 1},
            {'category': 'B', 'value': 2},
            {'category': 'A', 'value': 3},
        ]
        result = Queryable(data).group_by(lambda x: x['category']).to_list()
        self.assertEqual(len(result), 2)
        
        # Check that grouping worked
        group_a = next(g for g in result if g.key == 'A')
        self.assertEqual(len(group_a), 2)
        self.assertEqual([item['value'] for item in group_a], [1, 3])


class TestAggregation(unittest.TestCase):
    """Test aggregation operators."""
    
    def setUp(self):
        """Set up test data."""
        self.numbers = [1, 2, 3, 4, 5]
        self.query = Queryable(self.numbers)
    
    def test_count(self):
        """Test count operator."""
        self.assertEqual(self.query.count(), 5)
        self.assertEqual(self.query.count(lambda x: x > 3), 2)
    
    def test_sum(self):
        """Test sum operator."""
        self.assertEqual(self.query.sum(), 15)
    
    def test_average(self):
        """Test average operator."""
        self.assertEqual(self.query.average(), 3.0)
    
    def test_min(self):
        """Test min operator."""
        self.assertEqual(self.query.min(), 1)
    
    def test_max(self):
        """Test max operator."""
        self.assertEqual(self.query.max(), 5)
    
    def test_aggregate(self):
        """Test aggregate operator."""
        result = self.query.aggregate(lambda acc, x: acc + x, 0)
        self.assertEqual(result, 15)


class TestSetOperations(unittest.TestCase):
    """Test set operations."""
    
    def test_union(self):
        """Test union operator."""
        a = Queryable([1, 2, 3])
        b = [3, 4, 5]
        result = a.union(b).to_list()
        self.assertEqual(sorted(result), [1, 2, 3, 4, 5])
    
    def test_intersect(self):
        """Test intersect operator."""
        a = Queryable([1, 2, 3, 4])
        b = [3, 4, 5, 6]
        result = a.intersect(b).to_list()
        self.assertEqual(sorted(result), [3, 4])
    
    def test_except(self):
        """Test except_ operator."""
        a = Queryable([1, 2, 3, 4])
        b = [3, 4, 5, 6]
        result = a.except_(b).to_list()
        self.assertEqual(sorted(result), [1, 2])


class TestElementAccess(unittest.TestCase):
    """Test element access operators."""
    
    def setUp(self):
        """Set up test data."""
        self.numbers = [1, 2, 3, 4, 5]
        self.query = Queryable(self.numbers)
    
    def test_first(self):
        """Test first operator."""
        self.assertEqual(self.query.first(), 1)
        self.assertEqual(self.query.first(lambda x: x > 3), 4)
    
    def test_first_or_default(self):
        """Test first_or_default operator."""
        self.assertEqual(self.query.first_or_default(default=0), 1)
        self.assertEqual(self.query.first_or_default(lambda x: x > 10, default=0), 0)
    
    def test_last(self):
        """Test last operator."""
        self.assertEqual(self.query.last(), 5)
        self.assertEqual(self.query.last(lambda x: x < 3), 2)
    
    def test_last_or_default(self):
        """Test last_or_default operator."""
        self.assertEqual(self.query.last_or_default(default=0), 5)
        self.assertEqual(self.query.last_or_default(lambda x: x > 10, default=0), 0)
    
    def test_single(self):
        """Test single operator."""
        single_query = Queryable([42])
        self.assertEqual(single_query.single(), 42)
        self.assertEqual(self.query.single(lambda x: x == 3), 3)
    
    def test_element_at(self):
        """Test element_at operator."""
        self.assertEqual(self.query.element_at(0), 1)
        self.assertEqual(self.query.element_at(4), 5)
    
    def test_element_at_or_default(self):
        """Test element_at_or_default operator."""
        self.assertEqual(self.query.element_at_or_default(0, 0), 1)
        self.assertEqual(self.query.element_at_or_default(10, 0), 0)


class TestQuantifiers(unittest.TestCase):
    """Test quantifier operators."""
    
    def setUp(self):
        """Set up test data."""
        self.numbers = [1, 2, 3, 4, 5]
        self.query = Queryable(self.numbers)
    
    def test_any(self):
        """Test any operator."""
        self.assertTrue(self.query.any())
        self.assertTrue(self.query.any(lambda x: x > 4))
        self.assertFalse(self.query.any(lambda x: x > 10))
    
    def test_all(self):
        """Test all operator."""
        self.assertTrue(self.query.all(lambda x: x > 0))
        self.assertFalse(self.query.all(lambda x: x > 3))
    
    def test_contains(self):
        """Test contains operator."""
        self.assertTrue(self.query.contains(3))
        self.assertFalse(self.query.contains(10))


class TestConversion(unittest.TestCase):
    """Test conversion operators."""
    
    def test_to_list(self):
        """Test to_list conversion."""
        result = Queryable([1, 2, 3]).to_list()
        self.assertIsInstance(result, list)
        self.assertEqual(result, [1, 2, 3])
    
    def test_to_set(self):
        """Test to_set conversion."""
        result = Queryable([1, 2, 2, 3, 3, 3]).to_set()
        self.assertIsInstance(result, set)
        self.assertEqual(result, {1, 2, 3})
    
    def test_to_dict(self):
        """Test to_dict conversion."""
        data = [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'},
        ]
        result = Queryable(data).to_dict(lambda x: x['id'])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]['name'], 'Alice')
        self.assertEqual(result[2]['name'], 'Bob')
    
    def test_to_tuple(self):
        """Test to_tuple conversion."""
        result = Queryable([1, 2, 3]).to_tuple()
        self.assertIsInstance(result, tuple)
        self.assertEqual(result, (1, 2, 3))


class TestJoins(unittest.TestCase):
    """Test join operators."""
    
    def test_join(self):
        """Test join operator."""
        customers = [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'},
        ]
        orders = [
            {'customer_id': 1, 'product': 'Widget'},
            {'customer_id': 2, 'product': 'Gadget'},
            {'customer_id': 1, 'product': 'Doohickey'},
        ]
        
        result = Queryable(customers).join(
            orders,
            lambda c: c['id'],
            lambda o: o['customer_id'],
            lambda c, o: {'name': c['name'], 'product': o['product']}
        ).to_list()
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['name'], 'Alice')
        self.assertEqual(result[0]['product'], 'Widget')
    
    def test_group_join(self):
        """Test group_join operator."""
        customers = [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'},
        ]
        orders = [
            {'customer_id': 1, 'product': 'Widget'},
            {'customer_id': 1, 'product': 'Doohickey'},
            {'customer_id': 2, 'product': 'Gadget'},
        ]
        
        result = Queryable(customers).group_join(
            orders,
            lambda c: c['id'],
            lambda o: o['customer_id'],
            lambda c, os: {'name': c['name'], 'orders': [o['product'] for o in os]}
        ).to_list()
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Alice')
        self.assertEqual(len(result[0]['orders']), 2)
        self.assertIn('Widget', result[0]['orders'])


class TestComplexQueries(unittest.TestCase):
    """Test complex query scenarios."""
    
    def test_chained_query(self):
        """Test complex chained query."""
        result = Queryable(range(1, 11)) \
            .where(lambda x: x % 2 == 0) \
            .select(lambda x: x * 2) \
            .order_by_descending(lambda x: x) \
            .to_list()
        
        self.assertEqual(result, [20, 16, 12, 8, 4])
    
    def test_deferred_execution(self):
        """Test that queries are deferred until enumeration."""
        query = Queryable(range(1, 6)).where(lambda x: x > 2)
        # Query not executed yet
        result = query.to_list()
        # Now it's executed
        self.assertEqual(result, [3, 4, 5])
    
    def test_fluent_complex_query(self):
        """Test complex fluent query with multiple operators."""
        data = [
            {'dept': 'Sales', 'salary': 50000},
            {'dept': 'Engineering', 'salary': 80000},
            {'dept': 'Sales', 'salary': 55000},
            {'dept': 'Engineering', 'salary': 85000},
        ]
        
        result = Queryable(data) \
            .group_by(lambda x: x['dept']) \
            .select(lambda g: {
                'dept': g.key,
                'avg_salary': Queryable(g).select(lambda x: x['salary']).average()
            }) \
            .to_list()
        
        self.assertEqual(len(result), 2)
        
        engineering = next(r for r in result if r['dept'] == 'Engineering')
        self.assertAlmostEqual(engineering['avg_salary'], 82500)


if __name__ == '__main__':
    unittest.main()
