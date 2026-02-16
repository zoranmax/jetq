"""Tests for REST API query provider with expression trees."""

import json
from unittest.mock import MagicMock, patch

import pytest

from jetq.expression_parser import parse_lambda
from jetq.rest_provider import RestQueryProvider, RestQueryTranslator


class TestRestQueryTranslator:
    """Test REST query translation."""

    def setup_method(self):
        """Set up translator for each test."""
        self.translator = RestQueryTranslator()

    def test_translate_simple_equality(self):
        """Test translating x['userId'] == 1."""
        expr = parse_lambda(lambda x: x["userId"] == 1)
        params = self.translator.translate_filter(expr.body)

        assert params == {"userId": "1"}

    def test_translate_string_equality(self):
        """Test translating x['name'] == 'Alice'."""
        expr = parse_lambda(lambda x: x["name"] == "Alice")
        params = self.translator.translate_filter(expr.body)

        assert params == {"name": "Alice"}

    def test_translate_and_condition(self):
        """Test translating x['userId'] == 1 and x['active'] == True."""
        expr = parse_lambda(lambda x: x["userId"] == 1 and x["active"] == True)  # noqa: E712
        params = self.translator.translate_filter(expr.body)

        assert "userId" in params
        assert "active" in params
        assert params["userId"] == "1"
        assert params["active"] == "True"


class TestRestQueryProvider:
    """Test REST query provider."""

    def test_create_query(self):
        """Test creating a query."""
        provider = RestQueryProvider("https://api.example.com")
        query = provider.create_query("users")

        assert query is not None
        assert query._query_expr.base_url == "https://api.example.com"
        assert query._query_expr.resource_path == "users"

    @patch("urllib.request.urlopen")
    def test_execute_simple_query(self, mock_urlopen):
        """Test executing a simple query with filter."""
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            [{"id": 1, "userId": 1, "title": "Test Post"}]
        ).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        # Create provider and query
        provider = RestQueryProvider("https://api.example.com")
        query = provider.create_query("posts")

        # Execute query with filter
        result = query.where(lambda p: p["userId"] == 1).to_list()

        # Verify results
        assert len(result) == 1
        assert result[0]["userId"] == 1

        # Verify URL was called with query parameters
        called_url = mock_urlopen.call_args[0][0]
        assert "api.example.com/posts" in called_url
        assert "userId=1" in called_url

    @patch("urllib.request.urlopen")
    def test_execute_with_pagination(self, mock_urlopen):
        """Test executing a query with skip and take."""
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([{"id": 1}, {"id": 2}]).encode(
            "utf-8"
        )
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        # Create provider and query
        provider = RestQueryProvider("https://api.example.com")
        query = provider.create_query("users")

        # Execute query with pagination
        result = query.skip(10).take(5).to_list()

        # Verify URL was called with pagination parameters
        called_url = mock_urlopen.call_args[0][0]
        assert "_start=10" in called_url
        assert "_limit=5" in called_url
        assert result == [{"id": 1}, {"id": 2}]


class TestRestQueryableChaining:
    """Test chaining operations on REST queryable."""

    def test_chain_multiple_where(self):
        """Test chaining multiple where clauses."""
        provider = RestQueryProvider("https://api.example.com")
        query = provider.create_query("posts")

        # Chain where clauses
        result_query = query.where(lambda p: p["userId"] == 1).where(
            lambda p: p["published"]
        )

        # Verify both filters are in the query expression
        assert len(result_query._query_expr.filters) == 2

    def test_chain_where_and_pagination(self):
        """Test chaining where, skip, and take."""
        provider = RestQueryProvider("https://api.example.com")
        query = provider.create_query("posts")

        # Chain operations
        result_query = query.where(lambda p: p["userId"] == 1).skip(5).take(10)

        # Verify query expression has all operations
        assert len(result_query._query_expr.filters) == 1
        assert result_query._query_expr.skip_count == 5
        assert result_query._query_expr.take_count == 10


# Integration test with real API (will be skipped in CI if network unavailable)
@pytest.mark.integration
def test_real_jsonplaceholder_api():
    """Test with real JSONPlaceholder API."""
    try:
        provider = RestQueryProvider("https://jsonplaceholder.typicode.com")
        posts = provider.create_query("posts")

        # Test simple filter
        result = posts.where(lambda p: p["userId"] == 1).to_list()

        assert len(result) > 0
        assert all(p["userId"] == 1 for p in result)
        print(f"Successfully fetched {len(result)} posts for userId=1")
    except Exception as e:
        pytest.skip(f"Network test skipped: {e}")


@pytest.mark.integration
def test_real_api_with_pagination():
    """Test pagination with real API."""
    try:
        provider = RestQueryProvider("https://jsonplaceholder.typicode.com")
        posts = provider.create_query("posts")

        # Test pagination
        result = posts.skip(0).take(5).to_list()

        assert len(result) == 5
        print(f"Successfully fetched {len(result)} posts with pagination")
    except Exception as e:
        pytest.skip(f"Network test skipped: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
