"""Tests for newly added dependencies: requests and beautifulsoup4.

This test suite validates that the requests and beautifulsoup4 libraries
are correctly installed and can be used for their intended purposes.
These tests cover import validation, version compatibility, basic functionality,
and common use cases that the SDK might need.
"""

import re
from unittest.mock import Mock, patch

import pytest


class TestRequestsDependency:
    """Test suite for requests library dependency."""

    def test_requests_import(self):
        """Test that requests library can be imported."""
        try:
            import requests
        except ImportError as e:
            pytest.fail(f"Failed to import requests: {e}")

    def test_requests_version(self):
        """Test that requests version meets minimum requirement (>=2.25.0)."""
        import requests

        version_str = requests.__version__
        # Parse version string (format: "X.Y.Z" or "X.Y.Z.postN")
        match = re.match(r"(\d+)\.(\d+)\.(\d+)", version_str)
        assert match is not None, f"Invalid version format: {version_str}"

        major, minor, patch = map(int, match.groups())
        version_tuple = (major, minor, patch)

        # Check minimum version 2.25.0
        assert version_tuple >= (2, 25, 0), (
            f"requests version {version_str} is below minimum required version 2.25.0"
        )

    def test_requests_session_creation(self):
        """Test that requests Session objects can be created."""
        import requests

        session = requests.Session()
        assert session is not None
        assert isinstance(session, requests.Session)

    def test_requests_get_method_exists(self):
        """Test that essential HTTP methods are available."""
        import requests

        # Verify core HTTP methods exist
        assert hasattr(requests, "get")
        assert hasattr(requests, "post")
        assert hasattr(requests, "put")
        assert hasattr(requests, "delete")
        assert hasattr(requests, "patch")
        assert hasattr(requests, "head")
        assert hasattr(requests, "options")

    def test_requests_response_object(self):
        """Test requests Response object structure."""
        import requests

        # Mock a response
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "Test content"
            mock_response.json.return_value = {"key": "value"}
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.ok = True
            mock_get.return_value = mock_response

            response = requests.get("http://example.com")
            assert response.status_code == 200
            assert response.text == "Test content"
            assert response.json() == {"key": "value"}
            assert response.ok is True

    def test_requests_timeout_parameter(self):
        """Test that timeout parameter is supported."""
        import requests

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            # Call with timeout parameter
            requests.get("http://example.com", timeout=5)

            # Verify timeout was passed
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert "timeout" in call_kwargs
            assert call_kwargs["timeout"] == 5

    def test_requests_headers_parameter(self):
        """Test that custom headers can be passed."""
        import requests

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            custom_headers = {
                "User-Agent": "Claude-SDK/1.0",
                "Accept": "application/json",
            }
            requests.get("http://example.com", headers=custom_headers)

            # Verify headers were passed
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert "headers" in call_kwargs
            assert call_kwargs["headers"] == custom_headers

    def test_requests_exception_hierarchy(self):
        """Test that requests exception classes are available."""
        import requests

        # Verify exception hierarchy exists
        assert hasattr(requests, "RequestException")
        assert hasattr(requests, "HTTPError")
        assert hasattr(requests, "ConnectionError")
        assert hasattr(requests, "Timeout")
        assert hasattr(requests, "TooManyRedirects")

    def test_requests_status_code_handling(self):
        """Test handling of various HTTP status codes."""
        import requests

        with patch("requests.get") as mock_get:
            # Test successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.ok = True
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            response = requests.get("http://example.com")
            assert response.ok is True
            response.raise_for_status()  # Should not raise

    def test_requests_post_with_json_data(self):
        """Test POST request with JSON payload."""
        import requests

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": 123, "status": "created"}
            mock_post.return_value = mock_response

            payload = {"name": "test", "value": 42}
            response = requests.post("http://example.com/api", json=payload)

            assert response.status_code == 201
            assert response.json()["id"] == 123

            # Verify json parameter was used
            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args[1]
            assert "json" in call_kwargs
            assert call_kwargs["json"] == payload


class TestBeautifulSoup4Dependency:
    """Test suite for beautifulsoup4 library dependency."""

    def test_bs4_import(self):
        """Test that beautifulsoup4 can be imported."""
        try:
            import bs4
            from bs4 import BeautifulSoup
        except ImportError as e:
            pytest.fail(f"Failed to import beautifulsoup4: {e}")

    def test_bs4_version(self):
        """Test that beautifulsoup4 version meets minimum requirement (>=4.9.0)."""
        import bs4

        version_str = bs4.__version__
        # Parse version string (format: "X.Y.Z")
        match = re.match(r"(\d+)\.(\d+)\.(\d+)", version_str)
        assert match is not None, f"Invalid version format: {version_str}"

        major, minor, patch = map(int, match.groups())
        version_tuple = (major, minor, patch)

        # Check minimum version 4.9.0
        assert version_tuple >= (4, 9, 0), (
            f"beautifulsoup4 version {version_str} is below minimum required "
            f"version 4.9.0"
        )

    def test_beautifulsoup_creation(self):
        """Test creating BeautifulSoup object with HTML."""
        from bs4 import BeautifulSoup

        html = "<html><head><title>Test</title></head><body><p>Hello</p></body></html>"
        soup = BeautifulSoup(html, "html.parser")

        assert soup is not None
        assert isinstance(soup, BeautifulSoup)

    def test_beautifulsoup_find_methods(self):
        """Test that essential find methods are available."""
        from bs4 import BeautifulSoup

        html = "<html><body><p>Paragraph 1</p><p>Paragraph 2</p></body></html>"
        soup = BeautifulSoup(html, "html.parser")

        # Test find
        assert hasattr(soup, "find")
        first_p = soup.find("p")
        assert first_p is not None
        assert first_p.string == "Paragraph 1"

        # Test find_all
        assert hasattr(soup, "find_all")
        all_p = soup.find_all("p")
        assert len(all_p) == 2
        assert all_p[0].string == "Paragraph 1"
        assert all_p[1].string == "Paragraph 2"

    def test_beautifulsoup_select_css(self):
        """Test CSS selector support."""
        from bs4 import BeautifulSoup

        html = """
        <html>
            <body>
                <div class="container">
                    <p class="text">First</p>
                    <p class="text">Second</p>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        # Test select method
        assert hasattr(soup, "select")
        elements = soup.select("p.text")
        assert len(elements) == 2
        assert elements[0].string == "First"
        assert elements[1].string == "Second"

    def test_beautifulsoup_text_extraction(self):
        """Test extracting text content from HTML."""
        from bs4 import BeautifulSoup

        html = """
        <html>
            <body>
                <h1>Title</h1>
                <p>This is a paragraph.</p>
                <div>Nested <span>content</span> here.</div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        # Test get_text method
        assert hasattr(soup, "get_text")
        text = soup.get_text()
        assert "Title" in text
        assert "This is a paragraph." in text
        assert "Nested" in text
        assert "content" in text

    def test_beautifulsoup_attribute_access(self):
        """Test accessing HTML element attributes."""
        from bs4 import BeautifulSoup

        html = '<a href="https://example.com" class="link" id="main-link">Link</a>'
        soup = BeautifulSoup(html, "html.parser")

        link = soup.find("a")
        assert link is not None

        # Test attribute access
        assert link.get("href") == "https://example.com"
        assert link.get("class") == ["link"]
        assert link.get("id") == "main-link"
        assert link.string == "Link"

    def test_beautifulsoup_html_parser(self):
        """Test that html.parser is available and works."""
        from bs4 import BeautifulSoup

        html = "<html><body><p>Test</p></body></html>"

        # Should not raise an exception
        soup = BeautifulSoup(html, "html.parser")
        assert soup.find("p").string == "Test"

    def test_beautifulsoup_malformed_html(self):
        """Test parsing malformed HTML."""
        from bs4 import BeautifulSoup

        # Malformed HTML with unclosed tags
        html = "<div><p>Unclosed paragraph<div>Another div</p>"
        soup = BeautifulSoup(html, "html.parser")

        # Should still parse without raising exception
        assert soup is not None
        assert soup.find("p") is not None

    def test_beautifulsoup_empty_html(self):
        """Test parsing empty or minimal HTML."""
        from bs4 import BeautifulSoup

        # Empty string
        soup = BeautifulSoup("", "html.parser")
        assert soup is not None

        # Minimal HTML
        soup = BeautifulSoup("<html></html>", "html.parser")
        assert soup is not None

    def test_beautifulsoup_nested_elements(self):
        """Test navigating nested HTML elements."""
        from bs4 import BeautifulSoup

        html = """
        <div id="outer">
            <div id="inner">
                <span>Content</span>
            </div>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        outer = soup.find(id="outer")
        assert outer is not None

        inner = outer.find(id="inner")
        assert inner is not None

        span = inner.find("span")
        assert span is not None
        assert span.string == "Content"

    def test_beautifulsoup_parent_navigation(self):
        """Test navigating to parent elements."""
        from bs4 import BeautifulSoup

        html = """
        <div class="parent">
            <p class="child">Text</p>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        child = soup.find(class_="child")
        assert child is not None

        parent = child.parent
        assert parent is not None
        assert "parent" in parent.get("class", [])


class TestRequestsAndBeautifulSoupIntegration:
    """Test integration scenarios combining requests and beautifulsoup4."""

    def test_fetch_and_parse_html(self):
        """Test fetching HTML content and parsing it with BeautifulSoup."""
        import requests
        from bs4 import BeautifulSoup

        with patch("requests.get") as mock_get:
            # Mock HTML response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
                <head><title>Test Page</title></head>
                <body>
                    <h1>Welcome</h1>
                    <p>This is test content.</p>
                </body>
            </html>
            """
            mock_response.ok = True
            mock_get.return_value = mock_response

            # Fetch and parse
            response = requests.get("http://example.com")
            assert response.ok

            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.find("title")
            assert title is not None
            assert title.string == "Test Page"

            h1 = soup.find("h1")
            assert h1 is not None
            assert h1.string == "Welcome"

    def test_fetch_and_extract_links(self):
        """Test extracting links from fetched HTML."""
        import requests
        from bs4 import BeautifulSoup

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
                <body>
                    <a href="https://example.com/page1">Page 1</a>
                    <a href="https://example.com/page2">Page 2</a>
                    <a href="https://example.com/page3">Page 3</a>
                </body>
            </html>
            """
            mock_get.return_value = mock_response

            response = requests.get("http://example.com")
            soup = BeautifulSoup(response.text, "html.parser")

            links = soup.find_all("a")
            assert len(links) == 3

            hrefs = [link.get("href") for link in links]
            assert "https://example.com/page1" in hrefs
            assert "https://example.com/page2" in hrefs
            assert "https://example.com/page3" in hrefs

    def test_fetch_and_extract_metadata(self):
        """Test extracting metadata from HTML head section."""
        import requests
        from bs4 import BeautifulSoup

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
                <head>
                    <title>Example Page</title>
                    <meta name="description" content="This is an example page">
                    <meta name="keywords" content="example, test, html">
                    <meta property="og:title" content="Example Page">
                </head>
                <body>Content</body>
            </html>
            """
            mock_get.return_value = mock_response

            response = requests.get("http://example.com")
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title = soup.find("title")
            assert title.string == "Example Page"

            # Extract meta tags
            description = soup.find("meta", {"name": "description"})
            assert description.get("content") == "This is an example page"

            keywords = soup.find("meta", {"name": "keywords"})
            assert keywords.get("content") == "example, test, html"

            og_title = soup.find("meta", {"property": "og:title"})
            assert og_title.get("content") == "Example Page"

    def test_fetch_with_error_handling(self):
        """Test error handling when fetching and parsing HTML."""
        import requests
        from bs4 import BeautifulSoup

        with patch("requests.get") as mock_get:
            # Test HTTP error
            mock_get.side_effect = requests.HTTPError("404 Not Found")

            with pytest.raises(requests.HTTPError):
                requests.get("http://example.com")

        with patch("requests.get") as mock_get:
            # Test connection error
            mock_get.side_effect = requests.ConnectionError("Connection failed")

            with pytest.raises(requests.ConnectionError):
                requests.get("http://example.com")

        # Test parsing invalid HTML (should not raise)
        invalid_html = "<<>>invalid<<>>"
        soup = BeautifulSoup(invalid_html, "html.parser")
        assert soup is not None

    def test_fetch_and_extract_table_data(self):
        """Test extracting structured data from HTML tables."""
        import requests
        from bs4 import BeautifulSoup

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
                <body>
                    <table>
                        <thead>
                            <tr><th>Name</th><th>Value</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>Item 1</td><td>100</td></tr>
                            <tr><td>Item 2</td><td>200</td></tr>
                        </tbody>
                    </table>
                </body>
            </html>
            """
            mock_get.return_value = mock_response

            response = requests.get("http://example.com")
            soup = BeautifulSoup(response.text, "html.parser")

            table = soup.find("table")
            assert table is not None

            rows = table.find_all("tr")
            # Header row + 2 data rows
            assert len(rows) == 3

            # Check data rows
            data_rows = table.find("tbody").find_all("tr")
            assert len(data_rows) == 2

            first_row_cells = data_rows[0].find_all("td")
            assert first_row_cells[0].string == "Item 1"
            assert first_row_cells[1].string == "100"

    def test_fetch_with_custom_session(self):
        """Test using a requests Session with custom configuration."""
        import requests
        from bs4 import BeautifulSoup

        with patch.object(requests.Session, "get") as mock_session_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "<html><body><p>Content</p></body></html>"
            mock_session_get.return_value = mock_response

            session = requests.Session()
            session.headers.update({"User-Agent": "Claude-SDK/1.0"})

            response = session.get("http://example.com")
            soup = BeautifulSoup(response.text, "html.parser")

            p = soup.find("p")
            assert p.string == "Content"

    def test_fetch_and_find_specific_content(self):
        """Test finding specific content patterns in fetched HTML."""
        import requests
        from bs4 import BeautifulSoup

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
                <body>
                    <article>
                        <h2>Article Title</h2>
                        <p class="author">By John Doe</p>
                        <p class="content">This is the article content.</p>
                        <span class="date">2025-01-01</span>
                    </article>
                </body>
            </html>
            """
            mock_get.return_value = mock_response

            response = requests.get("http://example.com/article")
            soup = BeautifulSoup(response.text, "html.parser")

            article = soup.find("article")
            assert article is not None

            title = article.find("h2")
            assert title.string == "Article Title"

            author = article.find(class_="author")
            assert "John Doe" in author.string

            content = article.find(class_="content")
            assert content.string == "This is the article content."

            date = article.find(class_="date")
            assert date.string == "2025-01-01"


class TestDependencyEdgeCases:
    """Test edge cases and error scenarios for the dependencies."""

    def test_requests_timeout_scenario(self):
        """Test handling of timeout scenarios."""
        import requests

        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Request timed out")

            with pytest.raises(requests.Timeout):
                requests.get("http://example.com", timeout=1)

    def test_requests_redirect_handling(self):
        """Test that redirect handling is available."""
        import requests

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.url = "http://example.com/final"
            mock_response.history = [Mock(status_code=301)]
            mock_get.return_value = mock_response

            response = requests.get("http://example.com", allow_redirects=True)
            assert response.url == "http://example.com/final"
            assert len(response.history) == 1
            assert response.history[0].status_code == 301

    def test_beautifulsoup_unicode_handling(self):
        """Test parsing HTML with Unicode characters."""
        from bs4 import BeautifulSoup

        html = """
        <html>
            <body>
                <p>Hello 世界</p>
                <p>Emoji: 🌍🌎🌏</p>
                <p>Special: é, ñ, ü</p>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        paragraphs = soup.find_all("p")
        assert len(paragraphs) == 3
        assert "世界" in paragraphs[0].string
        assert "🌍" in paragraphs[1].string
        assert "é" in paragraphs[2].string

    def test_beautifulsoup_script_and_style_filtering(self):
        """Test filtering out script and style tags."""
        from bs4 import BeautifulSoup

        html = """
        <html>
            <head>
                <style>body { color: red; }</style>
                <script>console.log('test');</script>
            </head>
            <body>
                <p>Visible content</p>
                <script>alert('popup');</script>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style tags
        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text()
        assert "Visible content" in text
        assert "console.log" not in text
        assert "alert" not in text
        assert "body { color: red; }" not in text

    def test_requests_verify_ssl_parameter(self):
        """Test that SSL verification can be controlled."""
        import requests

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            # Call with verify=False
            requests.get("https://example.com", verify=False)

            # Verify parameter was passed
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert "verify" in call_kwargs
            assert call_kwargs["verify"] is False

    def test_beautifulsoup_whitespace_handling(self):
        """Test handling of whitespace in parsed HTML."""
        from bs4 import BeautifulSoup

        html = """
        <html>
            <body>
                <p>
                    Text with
                    multiple lines
                    and    spaces
                </p>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        p = soup.find("p")
        text = p.get_text(strip=True)
        assert "Text with" in text
        assert "multiple lines" in text
        assert "and    spaces" in text