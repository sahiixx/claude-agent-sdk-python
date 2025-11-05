"""Tests for pyproject.toml configuration validation."""

import re
import tomllib
from pathlib import Path
from typing import Any, Dict


class TestPyprojectToml:
    """Test pyproject.toml configuration and structure."""

    def setup_method(self):
        """Set up test fixtures."""
        self.pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(self.pyproject_path, "rb") as f:
            self.config = tomllib.load(f)

    def test_pyproject_exists(self):
        """Test that pyproject.toml file exists."""
        assert self.pyproject_path.exists(), "pyproject.toml file should exist"

    def test_pyproject_is_valid_toml(self):
        """Test that pyproject.toml is valid TOML format."""
        # If we got here, the file parsed successfully in setup_method
        assert self.config is not None
        assert isinstance(self.config, dict)

    def test_required_sections_exist(self):
        """Test that all required sections are present."""
        required_sections = [
            "build-system",
            "project",
            "tool",
        ]
        for section in required_sections:
            assert section in self.config, f"Required section '{section}' is missing"

    def test_build_system_configuration(self):
        """Test build-system configuration is correct."""
        build_system = self.config["build-system"]
        assert "requires" in build_system
        assert "build-backend" in build_system
        assert "hatchling" in build_system["requires"]
        assert build_system["build-backend"] == "hatchling.build"

    def test_project_metadata(self):
        """Test project metadata is properly defined."""
        project = self.config["project"]
        
        # Required fields
        required_fields = ["name", "version", "description", "readme", "requires-python"]
        for field in required_fields:
            assert field in project, f"Required project field '{field}' is missing"
        
        # Validate specific values
        assert project["name"] == "claude-agent-sdk"
        assert re.match(r"^\d+\.\d+\.\d+$", project["version"]), (
            "Version should follow semantic versioning (x.y.z)"
        )
        assert project["readme"] == "README.md"
        assert project["requires-python"] == ">=3.10"

    def test_project_license(self):
        """Test that project has a valid license."""
        project = self.config["project"]
        assert "license" in project
        assert "text" in project["license"]
        assert project["license"]["text"] == "MIT"

    def test_project_authors(self):
        """Test that project authors are defined."""
        project = self.config["project"]
        assert "authors" in project
        assert len(project["authors"]) > 0
        
        # Check first author has required fields
        author = project["authors"][0]
        assert "name" in author
        assert "email" in author
        assert author["name"] == "Anthropic"
        assert "@" in author["email"]

    def test_project_classifiers(self):
        """Test that project classifiers are defined and valid."""
        project = self.config["project"]
        assert "classifiers" in project
        classifiers = project["classifiers"]
        
        assert len(classifiers) > 0, "Should have at least one classifier"
        
        # Check for expected classifier categories
        classifier_text = "\n".join(classifiers)
        assert "Development Status ::" in classifier_text
        assert "License :: OSI Approved :: MIT License" in classifier_text
        assert "Programming Language :: Python :: 3" in classifier_text
        assert "Typing :: Typed" in classifier_text

    def test_project_keywords(self):
        """Test that project keywords are defined."""
        project = self.config["project"]
        assert "keywords" in project
        keywords = project["keywords"]
        assert len(keywords) > 0
        assert "claude" in keywords
        assert "sdk" in keywords

    def test_dependencies_are_defined(self):
        """Test that project dependencies are properly defined."""
        project = self.config["project"]
        assert "dependencies" in project
        dependencies = project["dependencies"]
        
        assert len(dependencies) > 0, "Should have at least one dependency"
        assert isinstance(dependencies, list)

    def test_required_dependencies_present(self):
        """Test that all required dependencies are included."""
        dependencies = self.config["project"]["dependencies"]
        dep_names = [dep.split(">=")[0].split(";")[0] for dep in dependencies]
        
        required_deps = ["anyio", "mcp", "requests", "beautifulsoup4"]
        for required in required_deps:
            assert required in dep_names, f"Required dependency '{required}' is missing"

    def test_dependency_version_constraints(self):
        """Test that dependencies have appropriate version constraints."""
        dependencies = self.config["project"]["dependencies"]
        
        for dep in dependencies:
            # Each dependency should have a version constraint
            assert ">=" in dep or "==" in dep or "~=" in dep, (
                f"Dependency '{dep}' should have a version constraint"
            )

    def test_requests_dependency_version(self):
        """Test that requests dependency has correct version constraint."""
        dependencies = self.config["project"]["dependencies"]
        requests_dep = [d for d in dependencies if d.startswith("requests")]
        
        assert len(requests_dep) == 1, "Should have exactly one requests dependency"
        assert "requests>=2.25.0" == requests_dep[0]

    def test_beautifulsoup4_dependency_version(self):
        """Test that beautifulsoup4 dependency has correct version constraint."""
        dependencies = self.config["project"]["dependencies"]
        bs4_dep = [d for d in dependencies if d.startswith("beautifulsoup4")]
        
        assert len(bs4_dep) == 1, "Should have exactly one beautifulsoup4 dependency"
        assert "beautifulsoup4>=4.9.0" == bs4_dep[0]

    def test_anyio_dependency_version(self):
        """Test that anyio dependency has correct version constraint."""
        dependencies = self.config["project"]["dependencies"]
        anyio_dep = [d for d in dependencies if d.startswith("anyio")]
        
        assert len(anyio_dep) == 1, "Should have exactly one anyio dependency"
        assert "anyio>=4.0.0" == anyio_dep[0]

    def test_mcp_dependency_version(self):
        """Test that mcp dependency has correct version constraint."""
        dependencies = self.config["project"]["dependencies"]
        mcp_dep = [d for d in dependencies if d.startswith("mcp")]
        
        assert len(mcp_dep) == 1, "Should have exactly one mcp dependency"
        assert "mcp>=0.1.0" == mcp_dep[0]

    def test_conditional_dependencies(self):
        """Test that conditional dependencies have proper markers."""
        dependencies = self.config["project"]["dependencies"]
        
        # Check typing_extensions has Python version marker
        typing_ext = [d for d in dependencies if "typing_extensions" in d]
        if typing_ext:
            assert "python_version" in typing_ext[0], (
                "typing_extensions should have python_version marker"
            )
            assert "python_version<'3.11'" in typing_ext[0]

    def test_optional_dependencies_defined(self):
        """Test that optional dependencies section exists."""
        project = self.config["project"]
        assert "optional-dependencies" in project
        optional_deps = project["optional-dependencies"]
        
        assert "dev" in optional_deps, "Should have 'dev' optional dependencies"

    def test_dev_dependencies(self):
        """Test that dev dependencies include testing tools."""
        dev_deps = self.config["project"]["optional-dependencies"]["dev"]
        dep_names = [dep.split(">=")[0].split("==")[0] for dep in dev_deps]
        
        expected_dev_deps = ["pytest", "pytest-asyncio", "pytest-cov", "mypy", "ruff"]
        for expected in expected_dev_deps:
            assert expected in dep_names, (
                f"Dev dependency '{expected}' should be included"
            )

    def test_project_urls(self):
        """Test that project URLs are defined."""
        project = self.config["project"]
        assert "urls" in project
        urls = project["urls"]
        
        required_urls = ["Homepage", "Documentation", "Issues"]
        for url_type in required_urls:
            assert url_type in urls, f"URL type '{url_type}' is missing"
            assert urls[url_type].startswith("http"), (
                f"{url_type} URL should start with http"
            )

    def test_hatch_build_configuration(self):
        """Test that hatch build configuration is correct."""
        tool = self.config["tool"]
        assert "hatch" in tool
        
        hatch = tool["hatch"]
        assert "build" in hatch
        assert "targets" in hatch["build"]
        
        targets = hatch["build"]["targets"]
        assert "wheel" in targets
        assert "sdist" in targets

    def test_wheel_packages_configuration(self):
        """Test that wheel build includes correct packages."""
        wheel = self.config["tool"]["hatch"]["build"]["targets"]["wheel"]
        assert "packages" in wheel
        assert "src/claude_agent_sdk" in wheel["packages"]

    def test_sdist_includes(self):
        """Test that sdist includes necessary files."""
        sdist = self.config["tool"]["hatch"]["build"]["targets"]["sdist"]
        assert "include" in sdist
        
        includes = sdist["include"]
        expected_includes = ["/src", "/tests", "/README.md", "/LICENSE"]
        for expected in expected_includes:
            assert expected in includes, f"sdist should include '{expected}'"

    def test_pytest_configuration(self):
        """Test that pytest configuration is properly set."""
        tool = self.config["tool"]
        assert "pytest" in tool
        
        pytest_config = tool["pytest"]["ini_options"]
        assert "testpaths" in pytest_config
        assert "tests" in pytest_config["testpaths"]
        assert "pythonpath" in pytest_config
        assert "src" in pytest_config["pythonpath"]

    def test_pytest_async_configuration(self):
        """Test that pytest-asyncio is configured."""
        tool = self.config["tool"]
        assert "pytest-asyncio" in tool
        assert tool["pytest-asyncio"]["asyncio_mode"] == "auto"

    def test_mypy_configuration(self):
        """Test that mypy is properly configured with strict settings."""
        tool = self.config["tool"]
        assert "mypy" in tool
        
        mypy = tool["mypy"]
        assert mypy["python_version"] == "3.10"
        assert mypy["strict"] is True
        
        # Check strict settings
        strict_options = [
            "warn_return_any",
            "disallow_untyped_defs",
            "disallow_incomplete_defs",
            "no_implicit_optional",
            "warn_redundant_casts",
            "strict_equality",
        ]
        for option in strict_options:
            assert mypy[option] is True, f"mypy should have {option} enabled"

    def test_ruff_configuration(self):
        """Test that ruff linter is properly configured."""
        tool = self.config["tool"]
        assert "ruff" in tool
        
        ruff = tool["ruff"]
        assert ruff["target-version"] == "py310"
        assert ruff["line-length"] == 88

    def test_ruff_lint_rules(self):
        """Test that ruff lint rules are properly configured."""
        ruff_lint = self.config["tool"]["ruff"]["lint"]
        assert "select" in ruff_lint
        assert "ignore" in ruff_lint
        
        # Check for important rule categories
        select = ruff_lint["select"]
        expected_rules = ["E", "F", "I", "B"]  # errors, pyflakes, isort, bugbear
        for rule in expected_rules:
            assert rule in select, f"Ruff should enable rule category '{rule}'"

    def test_ruff_isort_configuration(self):
        """Test that ruff isort settings are configured."""
        ruff_isort = self.config["tool"]["ruff"]["lint"]["isort"]
        assert "known-first-party" in ruff_isort
        assert "claude_agent_sdk" in ruff_isort["known-first-party"]

    def test_no_duplicate_dependencies(self):
        """Test that there are no duplicate dependencies."""
        dependencies = self.config["project"]["dependencies"]
        dep_names = [dep.split(">=")[0].split(";")[0].split("==")[0] for dep in dependencies]
        
        assert len(dep_names) == len(set(dep_names)), (
            "Dependencies should not contain duplicates"
        )

    def test_dependency_order_consistency(self):
        """Test that dependencies are in a consistent order."""
        dependencies = self.config["project"]["dependencies"]
        
        # Dependencies should be defined
        assert len(dependencies) >= 5, "Should have at least 5 dependencies"
        
        # Check that core dependencies come first, then optional ones
        dep_list = [d.split(">=")[0].split(";")[0] for d in dependencies]
        
        # anyio should be first or early (core async library)
        anyio_index = dep_list.index("anyio")
        assert anyio_index < 3, "Core async library should be early in list"

    def test_python_version_compatibility(self):
        """Test that Python version requirements are consistent."""
        project = self.config["project"]
        
        # Check requires-python
        requires_python = project["requires-python"]
        assert "3.10" in requires_python
        
        # Check classifiers match
        classifiers = project["classifiers"]
        python_classifiers = [c for c in classifiers if "Programming Language :: Python :: 3." in c]
        
        # Should have classifiers for 3.10, 3.11, 3.12, 3.13
        assert len(python_classifiers) >= 4, "Should have classifiers for supported Python versions"

    def test_version_format_is_valid(self):
        """Test that version follows semantic versioning."""
        version = self.config["project"]["version"]
        
        # Should be in format x.y.z
        parts = version.split(".")
        assert len(parts) == 3, "Version should have exactly 3 parts (major.minor.patch)"
        
        # Each part should be a number
        for part in parts:
            assert part.isdigit(), f"Version part '{part}' should be a number"

    def test_readme_file_exists(self):
        """Test that the specified README file exists."""
        readme_file = self.config["project"]["readme"]
        readme_path = self.pyproject_path.parent / readme_file
        assert readme_path.exists(), f"README file '{readme_file}' should exist"

    def test_license_file_exists(self):
        """Test that LICENSE file exists."""
        license_path = self.pyproject_path.parent / "LICENSE"
        assert license_path.exists(), "LICENSE file should exist"

    def test_source_package_exists(self):
        """Test that the source package directory exists."""
        wheel_config = self.config["tool"]["hatch"]["build"]["targets"]["wheel"]
        packages = wheel_config["packages"]
        
        for package in packages:
            package_path = self.pyproject_path.parent / package
            assert package_path.exists(), f"Package directory '{package}' should exist"
            assert package_path.is_dir(), f"Package '{package}' should be a directory"

    def test_test_directory_exists(self):
        """Test that the test directory exists."""
        pytest_config = self.config["tool"]["pytest"]["ini_options"]
        testpaths = pytest_config["testpaths"]
        
        for testpath in testpaths:
            test_dir = self.pyproject_path.parent / testpath
            assert test_dir.exists(), f"Test directory '{testpath}' should exist"
            assert test_dir.is_dir(), f"Test path '{testpath}' should be a directory"

    def test_dependency_string_format(self):
        """Test that all dependencies follow proper format."""
        dependencies = self.config["project"]["dependencies"]
        
        # Pattern for dependency specification
        # name>=version or name>=version; marker
        pattern = r"^[a-zA-Z0-9_-]+[>=<~!]+[\d.]+(?:;\s*.+)?$"
        
        for dep in dependencies:
            assert re.match(pattern, dep), f"Dependency '{dep}' has invalid format"

    def test_new_dependencies_have_reasonable_versions(self):
        """Test that newly added dependencies have reasonable version constraints."""
        dependencies = self.config["project"]["dependencies"]
        
        # Check requests version (should be >= 2.25.0)
        requests_dep = [d for d in dependencies if d.startswith("requests")]
        assert len(requests_dep) > 0, "requests dependency should be present"
        version_match = re.search(r">=(\d+\.\d+\.\d+)", requests_dep[0])
        assert version_match, "requests should have version constraint"
        major, minor, patch = map(int, version_match.group(1).split("."))
        assert major >= 2, "requests major version should be at least 2"
        assert major > 2 or minor >= 25, "requests version should be at least 2.25.0"
        
        # Check beautifulsoup4 version (should be >= 4.9.0)
        bs4_dep = [d for d in dependencies if d.startswith("beautifulsoup4")]
        assert len(bs4_dep) > 0, "beautifulsoup4 dependency should be present"
        version_match = re.search(r">=(\d+\.\d+\.\d+)", bs4_dep[0])
        assert version_match, "beautifulsoup4 should have version constraint"
        major, minor, patch = map(int, version_match.group(1).split("."))
        assert major >= 4, "beautifulsoup4 major version should be at least 4"
        assert major > 4 or minor >= 9, "beautifulsoup4 version should be at least 4.9.0"

    def test_all_dependencies_importable_names(self):
        """Test that dependency names are valid Python package names."""
        dependencies = self.config["project"]["dependencies"]
        
        for dep in dependencies:
            # Extract package name (before version specifier)
            pkg_name = dep.split(">=")[0].split("==")[0].split(";")[0].strip()
            
            # Package name should contain only valid characters
            assert re.match(r"^[a-zA-Z0-9_-]+$", pkg_name), (
                f"Package name '{pkg_name}' contains invalid characters"
            )

    def test_dev_dependencies_have_versions(self):
        """Test that all dev dependencies have version constraints."""
        dev_deps = self.config["project"]["optional-dependencies"]["dev"]
        
        for dep in dev_deps:
            assert ">=" in dep or "==" in dep or "~=" in dep, (
                f"Dev dependency '{dep}' should have a version constraint"
            )

    def test_configuration_completeness(self):
        """Test that configuration is complete with no TODOs or placeholders."""
        with open(self.pyproject_path, "r") as f:
            content = f.read()
        
        # Should not contain common placeholders
        placeholders = ["TODO", "FIXME", "XXX", "PLACEHOLDER", "TBD"]
        for placeholder in placeholders:
            assert placeholder.upper() not in content.upper(), (
                f"Configuration should not contain '{placeholder}'"
            )

    def test_urls_are_reachable_format(self):
        """Test that URLs follow expected format."""
        urls = self.config["project"]["urls"]
        
        for url_type, url in urls.items():
            # Should start with https (not http for security)
            assert url.startswith("https://"), (
                f"{url_type} URL should use HTTPS: {url}"
            )
            
            # Should be github or anthropic domain for this project
            assert "github.com" in url or "anthropic.com" in url, (
                f"{url_type} URL should be on github.com or anthropic.com"
            )

    def test_package_name_matches_import_name(self):
        """Test that package name and importable name are consistent."""
        project_name = self.config["project"]["name"]
        packages = self.config["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"]
        
        # Convert project name to expected import name
        expected_import = project_name.replace("-", "_")
        
        # Check that at least one package matches
        package_names = [pkg.split("/")[-1] for pkg in packages]
        assert any(expected_import in pkg_name for pkg_name in package_names), (
            f"No package found matching expected import name '{expected_import}'"
        )