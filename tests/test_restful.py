"""Integration tests querying real RESTful services online."""

import unittest
import json
from typing import Any, List
import urllib.request
import urllib.error

from jetq import Queryable


class RestfulServiceTests(unittest.TestCase):
    """Test jetq queries against real REST APIs."""
    
    @staticmethod
    def fetch_json(url: str) -> Any:
        """Fetch JSON from a URL."""
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.URLError as e:
            raise unittest.SkipTest(f"Unable to reach {url}: {e}")
    
    def test_json_placeholder_posts_filtering(self):
        """Test filtering posts from JSONPlaceholder API."""
        url = "https://jsonplaceholder.typicode.com/posts"
        posts = self.fetch_json(url)
        
        # Query for posts by userId 1
        result = (Queryable(posts)
                  .where(lambda p: p['userId'] == 1)
                  .to_list())
        
        self.assertGreater(len(result), 0)
        self.assertTrue(all(p['userId'] == 1 for p in result))
    
    def test_json_placeholder_posts_projection(self):
        """Test projecting post data from JSONPlaceholder API."""
        url = "https://jsonplaceholder.typicode.com/posts"
        posts = self.fetch_json(url)
        
        # Project only titles from all posts
        titles = (Queryable(posts)
                  .select(lambda p: p['title'])
                  .to_list())
        
        self.assertEqual(len(titles), len(posts))
        self.assertTrue(all(isinstance(t, str) for t in titles))
    
    def test_json_placeholder_posts_ordering(self):
        """Test ordering posts by ID."""
        url = "https://jsonplaceholder.typicode.com/posts"
        posts = self.fetch_json(url)
        
        # Order posts by ID descending
        ordered = (Queryable(posts)
                   .order_by_descending(lambda p: p['id'])
                   .to_list())
        
        self.assertEqual(ordered[0]['id'], max(p['id'] for p in posts))
        self.assertEqual(ordered[-1]['id'], min(p['id'] for p in posts))
    
    def test_json_placeholder_posts_grouping(self):
        """Test grouping posts by userId."""
        url = "https://jsonplaceholder.typicode.com/posts"
        posts = self.fetch_json(url)
        
        # Group posts by userId
        grouped = (Queryable(posts)
                   .group_by(lambda p: p['userId'])
                   .to_list())
        
        self.assertGreater(len(grouped), 0)
        for group in grouped:
            self.assertTrue(all(p['userId'] == group.key for p in group.elements))
    
    def test_json_placeholder_posts_complex_query(self):
        """Test complex query with filtering, ordering, and projection."""
        url = "https://jsonplaceholder.typicode.com/posts"
        posts = self.fetch_json(url)
        
        # Get titles of posts from userId 1-3, ordered by ID descending, limited to 5
        result = (Queryable(posts)
                  .where(lambda p: 1 <= p['userId'] <= 3)
                  .order_by_descending(lambda p: p['id'])
                  .to_list())
        result = (Queryable(result)
                  .take(5)
                  .select(lambda p: {'userId': p['userId'], 'title': p['title']})
                  .to_list())
        
        self.assertLessEqual(len(result), 5)
        self.assertTrue(all(1 <= item['userId'] <= 3 for item in result))
    
    def test_json_placeholder_users_filtering(self):
        """Test filtering users from JSONPlaceholder API."""
        url = "https://jsonplaceholder.typicode.com/users"
        users = self.fetch_json(url)
        
        # Find users from the USA (if available)
        result = (Queryable(users)
                  .where(lambda u: u.get('address', {}).get('country') is not None)
                  .to_list())
        
        self.assertIsInstance(result, list)
    
    def test_json_placeholder_users_select_many(self):
        """Test select_many with users and their posts."""
        users_url = "https://jsonplaceholder.typicode.com/users"
        posts_url = "https://jsonplaceholder.typicode.com/posts"
        
        users = self.fetch_json(users_url)
        posts = self.fetch_json(posts_url)
        
        # Create user post mapping
        user_posts = [{'user': u, 'posts': [p for p in posts if p['userId'] == u['id']]}
                      for u in users]
        
        # Flatten posts from all users
        all_posts = (Queryable(user_posts)
                     .select_many(lambda up: up['posts'])
                     .to_list())
        
        self.assertEqual(len(all_posts), len(posts))
    
    def test_json_placeholder_comments_distinct(self):
        """Test distinct operation on comments."""
        url = "https://jsonplaceholder.typicode.com/comments"
        comments = self.fetch_json(url)
        
        # Get distinct email addresses
        emails = (Queryable(comments)
                  .select(lambda c: c['email'])
                  .distinct()
                  .to_list())
        
        self.assertEqual(len(emails), len(set(e for c in comments for e in [c['email']])))
    
    def test_json_placeholder_comments_aggregation(self):
        """Test aggregation operations on comments."""
        url = "https://jsonplaceholder.typicode.com/comments"
        comments = self.fetch_json(url)
        
        # Count comments per postId
        post_ids = (Queryable(comments)
                    .select(lambda c: c['postId'])
                    .distinct()
                    .to_list())
        
        self.assertGreater(len(post_ids), 0)
        
        # Verify each postId has comments
        for post_id in post_ids[:5]:
            count = (Queryable(comments)
                     .where(lambda c: c['postId'] == post_id)
                     .count())
            self.assertGreater(count, 0)
    
    def test_json_placeholder_comments_skip_take(self):
        """Test skip and take pagination on comments."""
        url = "https://jsonplaceholder.typicode.com/comments"
        comments = self.fetch_json(url)
        
        # Get page 2 with 10 items per page
        page_size = 10
        page_number = 2
        
        result = (Queryable(comments)
                  .skip((page_number - 1) * page_size)
                  .take(page_size)
                  .to_list())
        
        self.assertLessEqual(len(result), page_size)
    
    def test_open_weather_data(self):
        """Test querying weather data from OpenWeatherMap-like API."""
        # Using a free weather API alternative
        url = "https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&current=temperature_2m,relative_humidity_2m"
        try:
            data = self.fetch_json(url)
            current = data.get('current', {})
            
            # Verify we got weather data
            self.assertIsNotNone(current.get('temperature_2m'))
            self.assertIsNotNone(current.get('relative_humidity_2m'))
        except unittest.SkipTest:
            self.skipTest("Weather API unavailable")
    
    def test_github_users_query(self):
        """Test querying GitHub users API."""
        url = "https://api.github.com/users?per_page=30"
        users = self.fetch_json(url)
        
        # Filter users with valid avatars
        result = (Queryable(users)
                  .where(lambda u: u.get('avatar_url') is not None)
                  .to_list())
        
        self.assertGreater(len(result), 0)
        self.assertTrue(all('avatar_url' in u for u in result))
    
    def test_multiple_api_combinations(self):
        """Test combining data from multiple API calls."""
        posts_url = "https://jsonplaceholder.typicode.com/posts"
        users_url = "https://jsonplaceholder.typicode.com/users"
        
        posts = self.fetch_json(posts_url)
        users = self.fetch_json(users_url)
        
        # Find posts and their authors
        user_map = {u['id']: u['name'] for u in users}
        
        result = (Queryable(posts)
                  .where(lambda p: p['userId'] in user_map)
                  .select(lambda p: {
                      'postId': p['id'],
                      'title': p['title'],
                      'author': user_map.get(p['userId'], 'Unknown'),
                      'userId': p['userId']
                  })
                  .order_by(lambda p: p['author'])
                  .to_list())
        
        self.assertGreater(len(result), 0)
        self.assertTrue(all('author' in item and item['author'] != 'Unknown' for item in result))
    
    def test_json_placeholder_todos(self):
        """Test querying todos from JSONPlaceholder."""
        url = "https://jsonplaceholder.typicode.com/todos"
        todos = self.fetch_json(url)
        
        # Get completed todos for userId 1
        result = (Queryable(todos)
                  .where(lambda t: t['userId'] == 1 and t['completed'])
                  .to_list())
        
        self.assertTrue(all(t['userId'] == 1 and t['completed'] for t in result))
    
    def test_json_placeholder_todos_statistics(self):
        """Test statistical queries on todos."""
        url = "https://jsonplaceholder.typicode.com/todos"
        todos = self.fetch_json(url)
        
        # Count completed vs incomplete todos per user
        completed_count = (Queryable(todos)
                          .where(lambda t: t['completed'])
                          .count())
        
        incomplete_count = (Queryable(todos)
                           .where(lambda t: not t['completed'])
                           .count())
        
        self.assertEqual(completed_count + incomplete_count, len(todos))
        self.assertGreater(completed_count, 0)
        self.assertGreater(incomplete_count, 0)
    
    def test_variant_skip_while(self):
        """Test skip_while variant on API data."""
        url = "https://jsonplaceholder.typicode.com/posts"
        posts = self.fetch_json(url)
        
        # Skip posts while ID is less than 5
        result = (Queryable(posts)
                  .skip_while(lambda p: p['id'] < 5)
                  .to_list())
        
        self.assertTrue(all(p['id'] >= 5 for p in result))
    
    def test_variant_take_while(self):
        """Test take_while variant on API data."""
        url = "https://jsonplaceholder.typicode.com/posts"
        posts = self.fetch_json(url)
        
        # Take posts while ID is less than 6
        result = (Queryable(posts)
                  .take_while(lambda p: p['id'] < 6)
                  .to_list())
        
        self.assertTrue(all(p['id'] < 6 for p in result))
    
    def test_variant_first(self):
        """Test first variant on API data."""
        url = "https://jsonplaceholder.typicode.com/posts"
        posts = self.fetch_json(url)
        
        # Get first post
        first_post = (Queryable(posts)
                      .first())
        
        self.assertEqual(first_post['id'], 1)
    
    def test_variant_last(self):
        """Test last variant on API data."""
        url = "https://jsonplaceholder.typicode.com/posts"
        posts = self.fetch_json(url)
        
        # Get last post
        last_post = (Queryable(posts)
                     .last())
        
        self.assertEqual(last_post['id'], len(posts))
    
    def test_variant_any(self):
        """Test any variant on API data."""
        url = "https://jsonplaceholder.typicode.com/posts"
        posts = self.fetch_json(url)
        
        # Check if any post has userId 5
        has_user_5 = (Queryable(posts)
                      .any(lambda p: p['userId'] == 5))
        
        self.assertTrue(has_user_5)
    
    def test_variant_all(self):
        """Test all variant on API data."""
        url = "https://jsonplaceholder.typicode.com/posts"
        posts = self.fetch_json(url)
        
        # Check if all posts have an id
        all_have_id = (Queryable(posts)
                       .all(lambda p: 'id' in p))
        
        self.assertTrue(all_have_id)


if __name__ == '__main__':
    unittest.main()
