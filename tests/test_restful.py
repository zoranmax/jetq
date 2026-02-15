"""Integration tests querying real RESTful services online."""

import json
import urllib.error
import urllib.request
from typing import Any

import pytest

from jetq import Queryable


def fetch_json(url: str) -> Any:
    """Fetch JSON from a URL."""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as e:
        pytest.skip(f"Unable to reach {url}: {e}")


def test_json_placeholder_posts_filtering():
    """Test filtering posts from JSONPlaceholder API."""
    url = "https://jsonplaceholder.typicode.com/posts"
    posts = fetch_json(url)

    # Query for posts by userId 1
    result = Queryable(posts).where(lambda p: p["userId"] == 1).to_list()

    assert len(result) > 0
    assert all(p["userId"] == 1 for p in result)


def test_json_placeholder_posts_projection():
    """Test projecting post data from JSONPlaceholder API."""
    url = "https://jsonplaceholder.typicode.com/posts"
    posts = fetch_json(url)

    # Project only titles from all posts
    titles = Queryable(posts).select(lambda p: p["title"]).to_list()

    assert len(titles) == len(posts)
    assert all(isinstance(t, str) for t in titles)


def test_json_placeholder_posts_ordering():
    """Test ordering posts by ID."""
    url = "https://jsonplaceholder.typicode.com/posts"
    posts = fetch_json(url)

    # Order posts by ID descending
    ordered = Queryable(posts).order_by_descending(lambda p: p["id"]).to_list()

    assert ordered[0]["id"] == max(p["id"] for p in posts)
    assert ordered[-1]["id"] == min(p["id"] for p in posts)


def test_json_placeholder_posts_grouping():
    """Test grouping posts by userId."""
    url = "https://jsonplaceholder.typicode.com/posts"
    posts = fetch_json(url)

    # Group posts by userId
    grouped = Queryable(posts).group_by(lambda p: p["userId"]).to_list()

    assert len(grouped) > 0
    for group in grouped:
        assert all(p["userId"] == group.key for p in group.elements)


def test_json_placeholder_posts_complex_query():
    """Test complex query with filtering, ordering, and projection."""
    url = "https://jsonplaceholder.typicode.com/posts"
    posts = fetch_json(url)

    # Get titles of posts from userId 1-3, ordered by ID descending, limited to 5
    result = (
        Queryable(posts)
        .where(lambda p: 1 <= p["userId"] <= 3)
        .order_by_descending(lambda p: p["id"])
        .to_list()
    )
    result = (
        Queryable(result)
        .take(5)
        .select(lambda p: {"userId": p["userId"], "title": p["title"]})
        .to_list()
    )

    assert len(result) <= 5
    assert all(1 <= item["userId"] <= 3 for item in result)


def test_json_placeholder_users_filtering():
    """Test filtering users from JSONPlaceholder API."""
    url = "https://jsonplaceholder.typicode.com/users"
    users = fetch_json(url)

    # Find users from the USA (if available)
    result = (
        Queryable(users)
        .where(lambda u: u.get("address", {}).get("country") is not None)
        .to_list()
    )

    assert isinstance(result, list)


def test_json_placeholder_users_select_many():
    """Test select_many with users and their posts."""
    users_url = "https://jsonplaceholder.typicode.com/users"
    posts_url = "https://jsonplaceholder.typicode.com/posts"

    users = fetch_json(users_url)
    posts = fetch_json(posts_url)

    # Create user post mapping
    user_posts = [
        {"user": u, "posts": [p for p in posts if p["userId"] == u["id"]]}
        for u in users
    ]

    # Flatten posts from all users
    all_posts = Queryable(user_posts).select_many(lambda up: up["posts"]).to_list()

    assert len(all_posts) == len(posts)


def test_json_placeholder_comments_distinct():
    """Test distinct operation on comments."""
    url = "https://jsonplaceholder.typicode.com/comments"
    comments = fetch_json(url)

    # Get distinct email addresses
    emails = Queryable(comments).select(lambda c: c["email"]).distinct().to_list()

    assert len(emails) == len({c["email"] for c in comments})


def test_json_placeholder_comments_aggregation():
    """Test aggregation operations on comments."""
    url = "https://jsonplaceholder.typicode.com/comments"
    comments = fetch_json(url)

    # Count comments per postId
    post_ids = Queryable(comments).select(lambda c: c["postId"]).distinct().to_list()

    assert len(post_ids) > 0

    # Verify each postId has comments
    for post_id in post_ids[:5]:
        count = (
            Queryable(comments).where(lambda c, pid=post_id: c["postId"] == pid).count()
        )
        assert count > 0


def test_json_placeholder_comments_skip_take():
    """Test skip and take pagination on comments."""
    url = "https://jsonplaceholder.typicode.com/comments"
    comments = fetch_json(url)

    # Get page 2 with 10 items per page
    page_size = 10
    page_number = 2

    result = (
        Queryable(comments)
        .skip((page_number - 1) * page_size)
        .take(page_size)
        .to_list()
    )

    assert len(result) <= page_size


def test_open_weather_data():
    """Test querying weather data from OpenWeatherMap-like API."""
    # Using a free weather API alternative
    url = (
        "https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&"
        "current=temperature_2m,relative_humidity_2m"
    )
    try:
        data = fetch_json(url)
        current = data.get("current", {})

        # Verify we got weather data
        assert current.get("temperature_2m") is not None
        assert current.get("relative_humidity_2m") is not None
    except pytest.skip.Exception:
        pytest.skip("Weather API unavailable")


def test_github_users_query():
    """Test querying GitHub users API."""
    url = "https://api.github.com/users?per_page=30"
    users = fetch_json(url)

    # Filter users with valid avatars
    result = Queryable(users).where(lambda u: u.get("avatar_url") is not None).to_list()

    assert len(result) > 0
    assert all("avatar_url" in u for u in result)


def test_multiple_api_combinations():
    """Test combining data from multiple API calls."""
    posts_url = "https://jsonplaceholder.typicode.com/posts"
    users_url = "https://jsonplaceholder.typicode.com/users"

    posts = fetch_json(posts_url)
    users = fetch_json(users_url)

    # Find posts and their authors
    user_map = {u["id"]: u["name"] for u in users}

    result = (
        Queryable(posts)
        .where(lambda p: p["userId"] in user_map)
        .select(
            lambda p: {
                "postId": p["id"],
                "title": p["title"],
                "author": user_map.get(p["userId"], "Unknown"),
                "userId": p["userId"],
            }
        )
        .order_by(lambda p: p["author"])
        .to_list()
    )

    assert len(result) > 0
    assert all("author" in item and item["author"] != "Unknown" for item in result)


def test_json_placeholder_todos():
    """Test querying todos from JSONPlaceholder."""
    url = "https://jsonplaceholder.typicode.com/todos"
    todos = fetch_json(url)

    # Get completed todos for userId 1
    result = (
        Queryable(todos).where(lambda t: t["userId"] == 1 and t["completed"]).to_list()
    )

    assert all(t["userId"] == 1 and t["completed"] for t in result)


def test_json_placeholder_todos_statistics():
    """Test statistical queries on todos."""
    url = "https://jsonplaceholder.typicode.com/todos"
    todos = fetch_json(url)

    # Count completed vs incomplete todos per user
    completed_count = Queryable(todos).where(lambda t: t["completed"]).count()

    incomplete_count = Queryable(todos).where(lambda t: not t["completed"]).count()

    assert completed_count + incomplete_count == len(todos)
    assert completed_count > 0
    assert incomplete_count > 0


def test_variant_skip_while():
    """Test skip_while variant on API data."""
    url = "https://jsonplaceholder.typicode.com/posts"
    posts = fetch_json(url)

    # Skip posts while ID is less than 5
    result = Queryable(posts).skip_while(lambda p: p["id"] < 5).to_list()

    assert all(p["id"] >= 5 for p in result)


def test_variant_take_while():
    """Test take_while variant on API data."""
    url = "https://jsonplaceholder.typicode.com/posts"
    posts = fetch_json(url)

    # Take posts while ID is less than 6
    result = Queryable(posts).take_while(lambda p: p["id"] < 6).to_list()

    assert all(p["id"] < 6 for p in result)


def test_variant_first():
    """Test first variant on API data."""
    url = "https://jsonplaceholder.typicode.com/posts"
    posts = fetch_json(url)

    # Get first post
    first_post = Queryable(posts).first()

    assert first_post["id"] == 1


def test_variant_last():
    """Test last variant on API data."""
    url = "https://jsonplaceholder.typicode.com/posts"
    posts = fetch_json(url)

    # Get last post
    last_post = Queryable(posts).last()

    assert last_post["id"] == len(posts)


def test_variant_any():
    """Test any variant on API data."""
    url = "https://jsonplaceholder.typicode.com/posts"
    posts = fetch_json(url)

    # Check if any post has userId 5
    has_user_5 = Queryable(posts).any(lambda p: p["userId"] == 5)

    assert has_user_5


def test_variant_all():
    """Test all variant on API data."""
    url = "https://jsonplaceholder.typicode.com/posts"
    posts = fetch_json(url)

    # Check if all posts have an id
    all_have_id = Queryable(posts).all(lambda p: "id" in p)

    assert all_have_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
