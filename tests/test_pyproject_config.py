"""Tests for pyproject.toml configuration validation."""

import sys

# Use tomllib for Python 3.11+, tomli for Python 3.10
if sys.version_info >= (3, 11):
    import tomllib as tomli
else:
    try:
        import tomli
    except ImportError:
        raise ImportError(
            "tomli is required for Python < 3.11. Install with: pip install tomli"
        )
import re
from pathlib import Path


class TestPyprojectConfig:
    """Test suite for pyproject.toml validation."""

    @classmethod
    def setup_class(cls):
        """Load pyproject.toml once for all tests."""
        cls.project_root = Path(__file__).parent.parent
        cls.pyproject_path = cls.project_root / "pyproject.toml"
        
        with open(cls.pyproject_path, "rb") as f:
            cls.config = tomli.load(f)

    def test_pyproject_file_exists(self):
        """Test that pyproject.toml exists."""
        assert self.pyproject_path.exists(), "pyproject.toml should exist"

    def test_project_metadata_present(self):
        """Test that required project metadata is present."""
        project = self.config.get("project", {})
        
        assert "name" in project, "Project name should be defined"
        assert project["name"] == "claude-agent-sdk", "Project name should be claude-agent-sdk"
        
        assert "version" in project, "Project version should be defined"
        assert re.match(r"\d+\.\d+\.\d+", project["version"]), "Version should follow semver"
        
        assert "description" in project, "Project description should be defined"
        assert len(project["description"]) > 0, "Description should not be empty"
        
        assert "requires-python" in project, "Python version requirement should be defined"

    def test_python_version_requirement(self):
        """Test that Python version requirement is valid."""
        project = self.config.get("project", {})
        requires_python = project.get("requires-python", "")
        
        assert ">=3.10" in requires_python, "Should require Python 3.10 or higher"

    def test_dependencies_structure(self):
        """Test that dependencies are properly structured."""
        project = self.config.get("project", {})
        dependencies = project.get("dependencies", [])
        
        assert isinstance(dependencies, list), "Dependencies should be a list"
        assert len(dependencies) > 0, "Should have at least one dependency"

    def test_core_dependencies_present(self):
        """Test that core dependencies are present."""
        project = self.config.get("project", {})
        dependencies = project.get("dependencies", [])
        
        # Convert to normalized format for easier checking
        dep_names = [dep.split(">=")[0].split("[")[0].strip() for dep in dependencies]
        
        # Test core dependencies
        assert "anyio" in dep_names, "anyio should be a dependency"
        assert "mcp" in dep_names, "mcp should be a dependency"

    def test_new_dependencies_present(self):
        """Test that newly added dependencies are present."""
        project = self.config.get("project", {})
        dependencies = project.get("dependencies", [])
        
        # Convert to normalized format
        dep_names = [dep.split(">=")[0].split("[")[0].strip() for dep in dependencies]
        
        # Test newly added dependencies
        assert "requests" in dep_names, "requests should be a dependency"
        assert "beautifulsoup4" in dep_names, "beautifulsoup4 should be a dependency"

    def test_dependency_version_constraints(self):
        """Test that dependencies have proper version constraints."""
        project = self.config.get("project", {})
        dependencies = project.get("dependencies", [])
        
        # Check requests version constraint
        requests_dep = [d for d in dependencies if d.startswith("requests")]
        assert len(requests_dep) == 1, "Should have exactly one requests dependency"
        assert ">=2.25.0" in requests_dep[0], "requests should have minimum version 2.25.0"
        
        # Check beautifulsoup4 version constraint
        bs4_dep = [d for d in dependencies if d.startswith("beautifulsoup4")]
        assert len(bs4_dep) == 1, "Should have exactly one beautifulsoup4 dependency"
        assert ">=4.9.0" in bs4_dep[0], "beautifulsoup4 should have minimum version 4.9.0"

    def test_no_duplicate_dependencies(self):
        """Test that there are no duplicate dependencies."""
        project = self.config.get("project", {})
        dependencies = project.get("dependencies", [])
        
        dep_names = [dep.split(">=")[0].split("[")[0].split(";")[0].strip() for dep in dependencies]
        
        assert len(dep_names) == len(set(dep_names)), (
            f"Dependencies should not have duplicates. Found: {dep_names}"
        )

    def test_dev_dependencies_present(self):
        """Test that development dependencies are properly configured."""
        project = self.config.get("project", {})
        optional_deps = project.get("optional-dependencies", {})
        
        assert "dev" in optional_deps, "Should have dev optional dependencies"
        dev_deps = optional_deps["dev"]
        
        assert isinstance(dev_deps, list), "Dev dependencies should be a list"
        
        # Check for essential dev tools
        dev_dep_names = [dep.split(">=")[0].strip() for dep in dev_deps]
        assert "pytest" in dev_dep_names, "pytest should be in dev dependencies"
        assert "pytest-asyncio" in dev_dep_names, "pytest-asyncio should be in dev dependencies"
        assert "mypy" in dev_dep_names, "mypy should be in dev dependencies"
        assert "ruff" in dev_dep_names, "ruff should be in dev dependencies"

    def test_build_system_configured(self):
        """Test that build system is properly configured."""
        build_system = self.config.get("build-system", {})
        
        assert "requires" in build_system, "Build system should have requires"
        assert "build-backend" in build_system, "Build system should have build-backend"
        
        assert "hatchling" in build_system["requires"], "Should use hatchling"
        assert build_system["build-backend"] == "hatchling.build", "Should use hatchling.build backend"

    def test_pytest_configuration(self):
        """Test that pytest is properly configured."""
        tool_pytest = self.config.get("tool", {}).get("pytest", {}).get("ini_options", {})
        
        assert "testpaths" in tool_pytest, "pytest testpaths should be configured"
        assert "tests" in tool_pytest["testpaths"], "tests directory should be in testpaths"
        
        assert "pythonpath" in tool_pytest, "pytest pythonpath should be configured"
        assert "src" in tool_pytest["pythonpath"], "src should be in pythonpath"

    def test_mypy_configuration(self):
        """Test that mypy is properly configured."""
        tool_mypy = self.config.get("tool", {}).get("mypy", {})
        
        assert "python_version" in tool_mypy, "mypy python_version should be configured"
        assert "strict" in tool_mypy, "mypy strict mode should be configured"
        assert tool_mypy["strict"] is True, "mypy should be in strict mode"

    def test_ruff_configuration(self):
        """Test that ruff is properly configured."""
        tool_ruff = self.config.get("tool", {}).get("ruff", {})
        
        assert "target-version" in tool_ruff, "ruff target-version should be configured"
        assert "line-length" in tool_ruff, "ruff line-length should be configured"
        
        lint_config = tool_ruff.get("lint", {})
        assert "select" in lint_config, "ruff lint rules should be selected"
        assert isinstance(lint_config["select"], list), "ruff select should be a list"
        assert len(lint_config["select"]) > 0, "Should have at least one lint rule selected"

    def test_project_urls_configured(self):
        """Test that project URLs are configured."""
        project = self.config.get("project", {})
        urls = project.get("urls", {})
        
        assert "Homepage" in urls, "Homepage URL should be configured"
        assert "Documentation" in urls, "Documentation URL should be configured"
        assert "Issues" in urls, "Issues URL should be configured"
        
        # Validate URL format
        for url_name, url_value in urls.items():
            assert url_value.startswith(("http://", "https://")), (
                f"{url_name} should be a valid URL"
            )

    def test_license_specified(self):
        """Test that license is specified."""
        project = self.config.get("project", {})
        license_info = project.get("license", {})
        
        assert "text" in license_info, "License should have text field"
        assert license_info["text"] == "MIT", "License should be MIT"

    def test_classifiers_present(self):
        """Test that package classifiers are present and valid."""
        project = self.config.get("project", {})
        classifiers = project.get("classifiers", [])
        
        assert isinstance(classifiers, list), "Classifiers should be a list"
        assert len(classifiers) > 0, "Should have at least one classifier"
        
        # Check for essential classifiers
        classifier_text = " ".join(classifiers)
        assert "License :: OSI Approved :: MIT License" in classifiers, "Should have MIT license classifier"
        assert any("Python :: 3.10" in c for c in classifiers), "Should support Python 3.10"
        assert any("Python :: 3.11" in c for c in classifiers), "Should support Python 3.11"
        assert any("Python :: 3.12" in c for c in classifiers), "Should support Python 3.12"

    def test_package_includes_configured(self):
        """Test that package includes are properly configured."""
        tool_hatch = self.config.get("tool", {}).get("hatch", {})
        build_targets = tool_hatch.get("build", {}).get("targets", {})
        
        wheel = build_targets.get("wheel", {})
        assert "packages" in wheel, "Wheel packages should be configured"
        assert "src/claude_agent_sdk" in wheel["packages"], "Should include claude_agent_sdk package"
        
        sdist = build_targets.get("sdist", {})
        assert "include" in sdist, "Source distribution includes should be configured"
        includes = sdist["include"]
        assert "/src" in includes, "Should include /src in source distribution"
        assert "/tests" in includes, "Should include /tests in source distribution"

    def test_dependency_versions_reasonable(self):
        """Test that dependency versions are reasonable (not too old)."""
        project = self.config.get("project", {})
        dependencies = project.get("dependencies", [])
        
        # Parse version requirements
        for dep in dependencies:
            if ">=" in dep:
                pkg_name, version_part = dep.split(">=")
                pkg_name = pkg_name.strip()
                # Extract just the version number (handle cases like "4.0.0; python_version<'3.11'")
                version = version_part.split(";")[0].strip()
                
                # Validate version format
                version_match = re.match(r"(\d+)\.(\d+)\.(\d+)", version)
                assert version_match, f"Version for {pkg_name} should be in X.Y.Z format, got: {version}"
                
                major, minor, patch = map(int, version_match.groups())
                
                # Reasonable version checks (not too old)
                if pkg_name == "requests":
                    assert major >= 2 and minor >= 25, "requests version should be at least 2.25.0"
                elif pkg_name == "beautifulsoup4":
                    assert major >= 4 and minor >= 9, "beautifulsoup4 version should be at least 4.9.0"
                elif pkg_name == "anyio":
                    assert major >= 4, "anyio should be version 4 or higher"

    def test_conditional_dependencies_valid(self):
        """Test that conditional dependencies have valid conditions."""
        project = self.config.get("project", {})
        dependencies = project.get("dependencies", [])
        
        # Check typing_extensions conditional dependency
        typing_ext_deps = [d for d in dependencies if "typing_extensions" in d]
        if typing_ext_deps:
            dep = typing_ext_deps[0]
            assert "python_version<'3.11'" in dep or "python_version<" in dep, (
                "typing_extensions should have Python version condition"
            )

    def test_keywords_present(self):
        """Test that package keywords are present."""
        project = self.config.get("project", {})
        keywords = project.get("keywords", [])
        
        assert isinstance(keywords, list), "Keywords should be a list"
        assert len(keywords) > 0, "Should have at least one keyword"
        assert "claude" in keywords, "Should have 'claude' as a keyword"
        assert "ai" in keywords or "anthropic" in keywords, "Should have AI-related keywords"

    def test_authors_specified(self):
        """Test that authors are specified."""
        project = self.config.get("project", {})
        authors = project.get("authors", [])
        
        assert isinstance(authors, list), "Authors should be a list"
        assert len(authors) > 0, "Should have at least one author"
        
        # Check first author has required fields
        first_author = authors[0]
        assert "name" in first_author, "Author should have a name"
        assert "email" in first_author, "Author should have an email"

    def test_readme_specified(self):
        """Test that README is specified."""
        project = self.config.get("project", {})
        readme = project.get("readme", "")
        
        assert readme, "README should be specified"
        assert readme == "README.md", "README should point to README.md"
        
        # Verify README file exists
        readme_path = self.project_root / readme
        assert readme_path.exists(), "README.md file should exist"


class TestDependencyCompatibility:
    """Test suite for dependency compatibility validation."""

    @classmethod
    def setup_class(cls):
        """Load pyproject.toml for compatibility tests."""
        cls.project_root = Path(__file__).parent.parent
        cls.pyproject_path = cls.project_root / "pyproject.toml"
        
        with open(cls.pyproject_path, "rb") as f:
            cls.config = tomli.load(f)

    def test_requests_beautifulsoup4_compatibility(self):
        """Test that requests and beautifulsoup4 versions are compatible."""
        project = self.config.get("project", {})
        dependencies = project.get("dependencies", [])
        
        # Find requests and beautifulsoup4
        has_requests = any("requests" in d for d in dependencies)
        has_bs4 = any("beautifulsoup4" in d for d in dependencies)
        
        assert has_requests, "requests should be in dependencies"
        assert has_bs4, "beautifulsoup4 should be in dependencies"
        
        # If both are present, they should be compatible
        # requests >= 2.25.0 is compatible with beautifulsoup4 >= 4.9.0
        requests_dep = [d for d in dependencies if "requests" in d][0]
        bs4_dep = [d for d in dependencies if "beautifulsoup4" in d][0]
        
        # Extract versions
        requests_version = requests_dep.split(">=")[1].split(";")[0].strip()
        bs4_version = bs4_dep.split(">=")[1].split(";")[0].strip()
        
        # Parse versions
        req_major, req_minor, _ = map(int, requests_version.split("."))
        bs4_major, bs4_minor, _ = map(int, bs4_version.split("."))
        
        # Check compatibility (these versions are known to work together)
        assert req_major == 2 and req_minor >= 25, "requests should be 2.25.0 or higher"
        assert bs4_major == 4 and bs4_minor >= 9, "beautifulsoup4 should be 4.9.0 or higher"

    def test_all_dependencies_have_version_constraints(self):
        """Test that all dependencies specify version constraints."""
        project = self.config.get("project", {})
        dependencies = project.get("dependencies", [])
        
        for dep in dependencies:
            # Remove platform/python version markers for checking
            base_dep = dep.split(";")[0].strip()
            
            # Should have version constraint (>=, ==, ~=, etc.)
            assert any(op in base_dep for op in [">=", "==", "~=", ">", "<"]), (
                f"Dependency {base_dep} should have a version constraint"
            )

    def test_python_version_consistency(self):
        """Test that Python version requirements are consistent across config sections."""
        project = self.config.get("project", {})
        requires_python = project.get("requires-python", "")
        
        classifiers = project.get("classifiers", [])
        python_classifiers = [c for c in classifiers if "Programming Language :: Python ::" in c]
        
        # Extract minimum version from requires-python
        min_version_match = re.search(r">=(\d+\.\d+)", requires_python)
        assert min_version_match, "Should have minimum Python version"
        min_version = min_version_match.group(1)
        
        # Check that classifiers include the minimum version
        assert any(f"Python :: {min_version}" in c for c in python_classifiers), (
            f"Classifiers should include Python {min_version}"
        )
        
        # Check tool.mypy python_version matches
        tool_mypy = self.config.get("tool", {}).get("mypy", {})
        mypy_version = tool_mypy.get("python_version", "")
        assert mypy_version == min_version, (
            f"mypy python_version ({mypy_version}) should match minimum required version ({min_version})"
        )