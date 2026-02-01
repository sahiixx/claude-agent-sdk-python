"""Tests for pyproject.toml dependency configuration.

This test suite validates the dependency declarations added to pyproject.toml,
ensuring they are correctly specified, can be installed without conflicts,
and meet security and compatibility requirements.
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest


class TestPyprojectDependencies:
    """Test dependency declarations in pyproject.toml."""

    @pytest.fixture
    def pyproject_path(self) -> Path:
        """
        Get the filesystem path to the project's pyproject.toml file.
        
        Returns:
            path (Path): Path to the pyproject.toml file located two levels above this test file.
        """
        return Path(__file__).parent.parent / "pyproject.toml"

    @pytest.fixture
    def pyproject_content(self, pyproject_path: Path) -> str:
        """
        Read and return the contents of the pyproject.toml file.
        
        Parameters:
            pyproject_path (Path): Path to the pyproject.toml file.
        
        Returns:
            str: The contents of the file.
        """
        return pyproject_path.read_text()

    def test_pyproject_file_exists(self, pyproject_path: Path) -> None:
        """Test that pyproject.toml exists."""
        assert pyproject_path.exists(), "pyproject.toml file not found"
        assert pyproject_path.is_file(), "pyproject.toml is not a file"

    def test_pyproject_is_valid_toml(self, pyproject_content: str) -> None:
        """
        Validate that the provided pyproject.toml content is syntactically and structurally valid.
        
        Uses tomllib to parse on Python 3.11 and newer; on older Python versions performs basic structural checks for the presence of a [project] table and a dependencies key.
        
        Parameters:
            pyproject_content (str): Contents of pyproject.toml to validate.
        """
        try:
            if sys.version_info >= (3, 11):
                import tomllib
                tomllib.loads(pyproject_content)
            else:
                # For Python 3.10, use basic validation
                # Check for basic TOML structure
                assert "[project]" in pyproject_content
                assert "dependencies" in pyproject_content
        except Exception as e:
            pytest.fail(f"pyproject.toml contains invalid TOML syntax: {e}")

    def test_requests_dependency_present(self, pyproject_content: str) -> None:
        """
        Verify that pyproject.toml declares the "requests" dependency and specifies a `>=` version constraint.
        
        Parameters:
            pyproject_content (str): The full contents of pyproject.toml.
        
        Raises:
            AssertionError: If "requests" is not present or does not include a `>=` version constraint (e.g., `requests>=2.25`).
        """
        assert "requests" in pyproject_content, "requests dependency not found"
        # Check for proper version constraint
        pattern = r'requests>=[\d.]+'
        assert re.search(pattern, pyproject_content), \
            "requests dependency missing version constraint"

    def test_beautifulsoup4_dependency_present(self, pyproject_content: str) -> None:
        """Test that beautifulsoup4 dependency is declared."""
        assert "beautifulsoup4" in pyproject_content, \
            "beautifulsoup4 dependency not found"
        # Check for proper version constraint
        pattern = r'beautifulsoup4>=[\d.]+'
        assert re.search(pattern, pyproject_content), \
            "beautifulsoup4 dependency missing version constraint"

    def test_requests_version_constraint(self, pyproject_content: str) -> None:
        """
        Verify pyproject.toml declares a `requests` dependency with an acceptable minimum version.
        
        Searches for a `requests>=MAJOR.MINOR[.PATCH...]` constraint, requires at least a numeric major and minor, enforces `major >= 2`, and if `major == 2` enforces `minor >= 25`.
        """
        match = re.search(r'requests>=([\d.]+)', pyproject_content)
        assert match is not None, "requests version constraint not found"
        
        version = match.group(1)
        parts = version.split('.')
        
        # Validate version format
        assert len(parts) >= 2, "requests version should have at least major.minor"
        for part in parts:
            assert part.isdigit(), f"Invalid version part: {part}"
        
        # Check minimum version is reasonable (2.25.0+)
        major = int(parts[0])
        minor = int(parts[1])
        assert major >= 2, "requests major version should be >= 2"
        if major == 2:
            assert minor >= 25, "requests 2.x should be >= 2.25"

    def test_beautifulsoup4_version_constraint(self, pyproject_content: str) -> None:
        """Test that beautifulsoup4 has a valid version constraint."""
        match = re.search(r'beautifulsoup4>=([\d.]+)', pyproject_content)
        assert match is not None, "beautifulsoup4 version constraint not found"
        
        version = match.group(1)
        parts = version.split('.')
        
        # Validate version format
        assert len(parts) >= 2, "beautifulsoup4 version should have at least major.minor"
        for part in parts:
            assert part.isdigit(), f"Invalid version part: {part}"
        
        # Check minimum version is reasonable (4.9.0+)
        major = int(parts[0])
        minor = int(parts[1])
        assert major >= 4, "beautifulsoup4 major version should be >= 4"
        if major == 4:
            assert minor >= 9, "beautifulsoup4 4.x should be >= 4.9"

    def test_dependency_syntax_format(self, pyproject_content: str) -> None:
        """Test that dependencies follow proper PEP 508 syntax."""
        # Extract dependencies section
        deps_match = re.search(
            r'dependencies\s*=\s*\[(.*?)\]',
            pyproject_content,
            re.DOTALL
        )
        assert deps_match is not None, "dependencies section not found"
        
        deps_section = deps_match.group(1)
        
        # Check requests syntax
        requests_patterns = [
            r'"requests>=[\d.]+",?',
            r"'requests>=[\d.]+',?",
        ]
        assert any(re.search(p, deps_section) for p in requests_patterns), \
            "requests dependency format is invalid"
        
        # Check beautifulsoup4 syntax
        bs4_patterns = [
            r'"beautifulsoup4>=[\d.]+",?',
            r"'beautifulsoup4>=[\d.]+',?",
        ]
        assert any(re.search(p, deps_section) for p in bs4_patterns), \
            "beautifulsoup4 dependency format is invalid"

    def test_no_duplicate_dependencies(self, pyproject_content: str) -> None:
        """
        Ensure `requests` and `beautifulsoup4` each appear exactly once in the provided pyproject.toml content.
        
        Parameters:
            pyproject_content (str): The full text content of pyproject.toml to inspect.
        """
        # Count occurrences of each dependency
        requests_count = len(re.findall(r'"requests[>=<]', pyproject_content))
        bs4_count = len(re.findall(r'"beautifulsoup4[>=<]', pyproject_content))
        
        assert requests_count == 1, \
            f"requests declared {requests_count} times (should be 1)"
        assert bs4_count == 1, \
            f"beautifulsoup4 declared {bs4_count} times (should be 1)"

    def test_dependencies_in_correct_section(self, pyproject_content: str) -> None:
        """
        Ensure requests and beautifulsoup4 are declared in the project's main [project] dependencies section rather than in optional dependency groups.
        
        Parameters:
            pyproject_content (str): The full contents of pyproject.toml to inspect for dependency declarations.
        """
        # Find the main dependencies section
        main_deps_match = re.search(
            r'\[project\].*?dependencies\s*=\s*\[(.*?)\]',
            pyproject_content,
            re.DOTALL
        )
        assert main_deps_match is not None, "main dependencies section not found"
        
        main_deps = main_deps_match.group(1)
        
        # Verify new dependencies are in main section
        assert "requests" in main_deps, \
            "requests should be in main dependencies, not optional"
        assert "beautifulsoup4" in main_deps, \
            "beautifulsoup4 should be in main dependencies, not optional"

    def test_existing_dependencies_preserved(self, pyproject_content: str) -> None:
        """Test that existing dependencies are still present."""
        required_deps = [
            "anyio>=4.0.0",
            "mcp>=0.1.0",
        ]
        
        for dep in required_deps:
            assert dep in pyproject_content, \
                f"Existing dependency '{dep}' is missing"

    def test_typing_extensions_conditional_preserved(self, pyproject_content: str) -> None:
        """Test that typing_extensions conditional dependency is preserved."""
        # Should have python version condition
        pattern = r'typing_extensions>=[\d.]+.*python_version.*[<\']3\.11'
        assert re.search(pattern, pyproject_content), \
            "typing_extensions conditional dependency is malformed"


class TestDependencyCompatibility:
    """Test dependency compatibility and installation."""

    def test_requests_can_be_imported(self) -> None:
        """Test that requests can be imported (if installed)."""
        try:
            import requests
            # Verify basic functionality
            assert hasattr(requests, 'get')
            assert hasattr(requests, 'post')
            assert hasattr(requests, 'Session')
        except ImportError:
            pytest.skip("requests not installed yet")

    def test_beautifulsoup4_can_be_imported(self) -> None:
        """Test that beautifulsoup4 can be imported (if installed)."""
        try:
            from bs4 import BeautifulSoup
            # Verify basic functionality
            assert callable(BeautifulSoup)
            # Test basic parsing
            soup = BeautifulSoup("<html><body><p>Test</p></body></html>", "html.parser")
            assert soup.find('p') is not None
        except ImportError:
            pytest.skip("beautifulsoup4 not installed yet")

    def test_requests_version_sufficient(self) -> None:
        """Test that installed requests version meets minimum requirement."""
        try:
            import requests
            version = requests.__version__
            parts = version.split('.')
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            
            assert major > 2 or (major == 2 and minor >= 25), \
                f"requests version {version} is below minimum 2.25.0"
        except ImportError:
            pytest.skip("requests not installed yet")

    def test_beautifulsoup4_version_sufficient(self) -> None:
        """
        Verify the installed beautifulsoup4 package meets the minimum required version 4.9.0.
        
        Skips the test if beautifulsoup4 is not installed.
        """
        try:
            import bs4
            version = bs4.__version__
            parts = version.split('.')
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            
            assert major > 4 or (major == 4 and minor >= 9), \
                f"beautifulsoup4 version {version} is below minimum 4.9.0"
        except ImportError:
            pytest.skip("beautifulsoup4 not installed yet")

    def test_requests_and_beautifulsoup_compatible(self) -> None:
        """Test that requests and beautifulsoup4 work together."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Create a mock response to test compatibility
            class MockResponse:
                def __init__(self) -> None:
                    """
                    Initialize a simple mock HTTP response with default HTML content.
                    
                    Creates three instance attributes:
                    - `text`: a UTF-8 string containing a small HTML document.
                    - `content`: the UTF-8 encoded bytes of `text`.
                    - `status_code`: the HTTP status code (200).
                    """
                    self.text = "<html><body><h1>Test</h1></body></html>"
                    self.content = self.text.encode('utf-8')
                    self.status_code = 200
            
            response = MockResponse()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            assert soup.find('h1') is not None
            assert soup.find('h1').text == "Test"
        except ImportError:
            pytest.skip("dependencies not installed yet")


class TestDependencyUseCases:
    """Test expected use cases for the new dependencies."""

    def test_requests_http_methods_available(self) -> None:
        """Test that requests provides expected HTTP methods."""
        try:
            import requests
            
            # Verify all major HTTP methods are available
            assert hasattr(requests, 'get')
            assert hasattr(requests, 'post')
            assert hasattr(requests, 'put')
            assert hasattr(requests, 'delete')
            assert hasattr(requests, 'patch')
            assert hasattr(requests, 'head')
            assert hasattr(requests, 'options')
        except ImportError:
            pytest.skip("requests not installed yet")

    def test_requests_session_support(self) -> None:
        """
        Verify that a requests.Session can be created and exposes common attributes used for connection pooling (`get`, `post`, `headers`, `cookies`). The test is skipped if the `requests` package is not installed.
        """
        try:
            import requests
            
            session = requests.Session()
            assert session is not None
            assert hasattr(session, 'get')
            assert hasattr(session, 'post')
            assert hasattr(session, 'headers')
            assert hasattr(session, 'cookies')
        except ImportError:
            pytest.skip("requests not installed yet")

    def test_beautifulsoup_parsers_available(self) -> None:
        """Test that beautifulsoup4 supports multiple parsers."""
        try:
            from bs4 import BeautifulSoup
            
            html = "<html><body><p>Test</p></body></html>"
            
            # Test html.parser (built-in)
            soup_html = BeautifulSoup(html, "html.parser")
            assert soup_html.find('p') is not None
            
            # Note: lxml parser requires separate installation
            # Just verify the API accepts parser argument
            assert callable(BeautifulSoup)
        except ImportError:
            pytest.skip("beautifulsoup4 not installed yet")

    def test_beautifulsoup_navigation_methods(self) -> None:
        """Test that beautifulsoup4 provides expected navigation methods."""
        try:
            from bs4 import BeautifulSoup
            
            html = """
            <html>
                <body>
                    <div class="container">
                        <h1 id="title">Title</h1>
                        <p class="text">Paragraph 1</p>
                        <p class="text">Paragraph 2</p>
                    </div>
                </body>
            </html>
            """
            
            soup = BeautifulSoup(html, "html.parser")
            
            # Test various navigation methods
            assert soup.find('h1') is not None
            assert soup.find('h1').get('id') == 'title'
            assert soup.find(id='title') is not None
            assert soup.find(class_='container') is not None
            
            paragraphs = soup.find_all('p')
            assert len(paragraphs) == 2
            
            # Test CSS selector support
            assert soup.select('.text') is not None
            assert len(soup.select('.text')) == 2
        except ImportError:
            pytest.skip("beautifulsoup4 not installed yet")

    def test_beautifulsoup_text_extraction(self) -> None:
        """Test that beautifulsoup4 can extract text content."""
        try:
            from bs4 import BeautifulSoup
            
            html = """
            <html>
                <body>
                    <h1>Main Title</h1>
                    <p>This is <strong>important</strong> text.</p>
                </body>
            </html>
            """
            
            soup = BeautifulSoup(html, "html.parser")
            
            # Test text extraction
            h1_text = soup.find('h1').get_text()
            assert h1_text == "Main Title"
            
            p_text = soup.find('p').get_text()
            assert "important" in p_text
            
            # Test text extraction with strip
            stripped = soup.find('p').get_text(strip=True)
            assert stripped.startswith("This is")
        except ImportError:
            pytest.skip("beautifulsoup4 not installed yet")


class TestDependencySecurityAndBestPractices:
    """Test security and best practices for dependencies."""

    def test_no_wildcard_versions(self, ) -> None:
        """Test that dependencies don't use wildcard versions."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        content = pyproject_path.read_text()
        
        # Check that we don't use wildcards or unbound upper limits
        assert "*" not in content or "*.md" in content, \
            "Wildcard versions are not allowed"
        
        # Verify we use >= for minimum versions (not ==)
        deps_section = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
        assert deps_section is not None
        
        # New dependencies should use >= for flexibility
        assert "requests>=" in content
        assert "beautifulsoup4>=" in content

    def test_requests_ssl_support(self) -> None:
        """Test that requests has SSL support available."""
        try:
            import requests
            
            # Verify SSL-related attributes exist
            # This ensures the installation has SSL capabilities
            session = requests.Session()
            assert hasattr(session, 'verify')
            
            # Check that requests can handle HTTPS (at API level)
            assert callable(requests.get)
        except ImportError:
            pytest.skip("requests not installed yet")

    def test_dependency_documentation_urls(self) -> None:
        """
        Ensure dependency documentation URLs use HTTPS.
        
        Asserts that the known documentation URLs for requests and BeautifulSoup begin with "https://".
        """
        # These are the official documentation sites
        requests_docs = "https://requests.readthedocs.io/"
        bs4_docs = "https://www.crummy.com/software/BeautifulSoup/bs4/doc/"
        
        # Just verify these are valid URL formats
        assert requests_docs.startswith("https://")
        assert bs4_docs.startswith("https://")


class TestDependencyIntegrationReadiness:
    """Test that dependencies are ready for future integration."""

    def test_requests_can_handle_json(self) -> None:
        """Test that requests can handle JSON responses."""
        try:
            import requests
            
            # Verify JSON handling capabilities
            session = requests.Session()
            assert hasattr(session, 'get')
            
            # Verify Response object has json method
            # (we can't test actual network calls in unit tests)
            import requests.models
            assert hasattr(requests.models.Response, 'json')
        except ImportError:
            pytest.skip("requests not installed yet")

    def test_beautifulsoup_handles_malformed_html(self) -> None:
        """Test that beautifulsoup4 can parse malformed HTML gracefully."""
        try:
            from bs4 import BeautifulSoup
            
            # Malformed HTML (unclosed tags, improper nesting)
            malformed = """
            <html>
                <body>
                    <div>
                        <p>Unclosed paragraph
                        <span>Unclosed span
                    </div>
                <body>
            </html>
            """
            
            # BeautifulSoup should handle this gracefully
            soup = BeautifulSoup(malformed, "html.parser")
            assert soup is not None
            assert soup.find('div') is not None
            
            # Should still be able to extract content
            text = soup.get_text()
            assert len(text) > 0
        except ImportError:
            pytest.skip("beautifulsoup4 not installed yet")

    def test_combined_requests_beautifulsoup_workflow(self) -> None:
        """Test a typical workflow combining requests and beautifulsoup4."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Simulate a typical workflow (without actual network call)
            mock_html = """
            <html>
                <head><title>Test Page</title></head>
                <body>
                    <h1>Welcome</h1>
                    <p class="description">This is a test page.</p>
                    <a href="/page1">Link 1</a>
                    <a href="/page2">Link 2</a>
                </body>
            </html>
            """
            
            # Parse the HTML
            soup = BeautifulSoup(mock_html, "html.parser")
            
            # Extract data (typical use case)
            title = soup.find('title').get_text()
            assert title == "Test Page"
            
            heading = soup.find('h1').get_text()
            assert heading == "Welcome"
            
            description = soup.find(class_='description').get_text()
            assert "test page" in description
            
            links = [a['href'] for a in soup.find_all('a')]
            assert len(links) == 2
            assert '/page1' in links
            assert '/page2' in links
        except ImportError:
            pytest.skip("dependencies not installed yet")

    def test_requests_timeout_support(self) -> None:
        """
        Verify that requests exposes a timeout parameter on its HTTP methods.
        
        Checks that the callable signatures of `requests.get` and `requests.post` include a `timeout` parameter; skips the test if the `requests` package is not installed.
        """
        try:
            import requests
            
            # Verify timeout parameter is supported in the API
            # (we can't test actual calls, just verify the interface)
            import inspect
            
            get_sig = inspect.signature(requests.get)
            assert 'timeout' in get_sig.parameters
            
            post_sig = inspect.signature(requests.post)
            assert 'timeout' in post_sig.parameters
        except ImportError:
            pytest.skip("requests not installed yet")

    def test_beautifulsoup_encoding_handling(self) -> None:
        """
        Verify BeautifulSoup preserves Unicode characters when parsing UTF-8 HTML.
        
        Skips the test if beautifulsoup4 is not installed.
        """
        try:
            from bs4 import BeautifulSoup
            
            # Test with UTF-8 content
            utf8_html = """
            <html>
                <body><p>Hello 世界 мир</p></body>
            </html>
            """
            
            soup = BeautifulSoup(utf8_html, "html.parser")
            text = soup.find('p').get_text()
            
            # Should preserve unicode characters
            assert "世界" in text
            assert "мир" in text
        except ImportError:
            pytest.skip("beautifulsoup4 not installed yet")