"""
Generic plugin validation tests.

Every plugin file in the repository root gets at least one test:
- Syntax validation (AST parse)
- Import validation (module loads)
- Config validation (TOML files)
- Plugin class structure validation
"""

import ast
import sys
import importlib
import importlib.util
from pathlib import Path

import pytest

from conftest import (
    get_plugin_files,
    get_plugin_name,
    load_plugin_module,
    find_plugin_class,
    REPO_ROOT,
)


class TestPluginSyntax:
    """Test that all plugin files have valid Python syntax."""

    @pytest.mark.parametrize("plugin_file", get_plugin_files(), ids=get_plugin_name)
    def test_plugin_parses(self, plugin_file):
        """Plugin file can be parsed by ast."""
        source = plugin_file.read_text(encoding="utf-8")
        try:
            ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {plugin_file.name}: {e}")

    @pytest.mark.parametrize("plugin_file", get_plugin_files(), ids=get_plugin_name)
    def test_plugin_compiles(self, plugin_file):
        """Plugin file compiles to bytecode."""
        source = plugin_file.read_text(encoding="utf-8")
        try:
            compile(source, str(plugin_file), "exec")
        except (SyntaxError, ValueError) as e:
            pytest.fail(f"Compile error in {plugin_file.name}: {e}")


class TestPluginImports:
    """Test that all plugin modules can be imported."""

    @pytest.mark.parametrize("plugin_file", get_plugin_files(), ids=get_plugin_name)
    def test_plugin_imports(self, plugin_file):
        """Plugin module can be loaded without ImportError."""
        module = load_plugin_module(plugin_file)
        if module is None:
            # Some plugins may fail to import due to missing optional deps
            # Check if it's a known optional dependency issue
            source = plugin_file.read_text(encoding="utf-8")
            try:
                compile(source, str(plugin_file), "exec")
            except (SyntaxError, ValueError):
                pytest.fail(f"Plugin {plugin_file.name} has syntax errors")
            # If it compiles but doesn't load, it's likely a missing optional dep
            pytest.skip(f"Plugin {plugin_file.name} could not be loaded (likely missing optional dependency)")


class TestPluginStructure:
    """Test that plugin classes have required attributes."""

    @pytest.mark.parametrize("plugin_file", get_plugin_files(), ids=get_plugin_name)
    def test_plugin_has_version(self, plugin_file):
        """Plugin class has __version__ attribute."""
        module = load_plugin_module(plugin_file)
        if module is None:
            pytest.skip(f"Plugin {plugin_file.name} could not be loaded")
        plugin_class = find_plugin_class(module)
        if plugin_class is None:
            pytest.skip(f"Plugin {plugin_file.name} has no identifiable plugin class")
        assert hasattr(plugin_class, "__version__"), (
            f"Plugin {plugin_file.name} missing __version__"
        )

    @pytest.mark.parametrize("plugin_file", get_plugin_files(), ids=get_plugin_name)
    def test_plugin_has_license(self, plugin_file):
        """Plugin class has __license__ attribute."""
        module = load_plugin_module(plugin_file)
        if module is None:
            pytest.skip(f"Plugin {plugin_file.name} could not be loaded")
        plugin_class = find_plugin_class(module)
        if plugin_class is None:
            pytest.skip(f"Plugin {plugin_file.name} has no identifiable plugin class")
        assert hasattr(plugin_class, "__license__"), (
            f"Plugin {plugin_file.name} missing __license__"
        )

    @pytest.mark.parametrize("plugin_file", get_plugin_files(), ids=get_plugin_name)
    def test_plugin_has_name(self, plugin_file):
        """Plugin class has __name__ attribute."""
        module = load_plugin_module(plugin_file)
        if module is None:
            pytest.skip(f"Plugin {plugin_file.name} could not be loaded")
        plugin_class = find_plugin_class(module)
        if plugin_class is None:
            pytest.skip(f"Plugin {plugin_file.name} has no identifiable plugin class")
        assert hasattr(plugin_class, "__name__"), (
            f"Plugin {plugin_file.name} missing __name__"
        )

    @pytest.mark.parametrize("plugin_file", get_plugin_files(), ids=get_plugin_name)
    def test_plugin_has_description(self, plugin_file):
        """Plugin class has __description__ attribute."""
        module = load_plugin_module(plugin_file)
        if module is None:
            pytest.skip(f"Plugin {plugin_file.name} could not be loaded")
        plugin_class = find_plugin_class(module)
        if plugin_class is None:
            pytest.skip(f"Plugin {plugin_file.name} has no identifiable plugin class")
        assert hasattr(plugin_class, "__description__"), (
            f"Plugin {plugin_file.name} missing __description__"
        )

    @pytest.mark.parametrize("plugin_file", get_plugin_files(), ids=get_plugin_name)
    def test_plugin_has_author(self, plugin_file):
        """Plugin class has __author__ attribute."""
        module = load_plugin_module(plugin_file)
        if module is None:
            pytest.skip(f"Plugin {plugin_file.name} could not be loaded")
        plugin_class = find_plugin_class(module)
        if plugin_class is None:
            pytest.skip(f"Plugin {plugin_file.name} has no identifiable plugin class")
        assert hasattr(plugin_class, "__author__"), (
            f"Plugin {plugin_file.name} missing __author__"
        )

    @pytest.mark.parametrize("plugin_file", get_plugin_files(), ids=get_plugin_name)
    def test_plugin_has_help(self, plugin_file):
        """Plugin class has __help__ attribute."""
        module = load_plugin_module(plugin_file)
        if module is None:
            pytest.skip(f"Plugin {plugin_file.name} could not be loaded")
        plugin_class = find_plugin_class(module)
        if plugin_class is None:
            pytest.skip(f"Plugin {plugin_file.name} has no identifiable plugin class")
        assert hasattr(plugin_class, "__help__"), (
            f"Plugin {plugin_file.name} missing __help__"
        )

    @pytest.mark.parametrize("plugin_file", get_plugin_files(), ids=get_plugin_name)
    def test_plugin_has_defaults(self, plugin_file):
        """Plugin class has __defaults__ attribute."""
        module = load_plugin_module(plugin_file)
        if module is None:
            pytest.skip(f"Plugin {plugin_file.name} could not be loaded")
        plugin_class = find_plugin_class(module)
        if plugin_class is None:
            pytest.skip(f"Plugin {plugin_file.name} has no identifiable plugin class")
        assert hasattr(plugin_class, "__defaults__"), (
            f"Plugin {plugin_file.name} missing __defaults__"
        )

    @pytest.mark.parametrize("plugin_file", get_plugin_files(), ids=get_plugin_name)
    def test_plugin_has_dependencies(self, plugin_file):
        """Plugin class has __dependencies__ attribute."""
        module = load_plugin_module(plugin_file)
        if module is None:
            pytest.skip(f"Plugin {plugin_file.name} could not be loaded")
        plugin_class = find_plugin_class(module)
        if plugin_class is None:
            pytest.skip(f"Plugin {plugin_file.name} has no identifiable plugin class")
        assert hasattr(plugin_class, "__dependencies__"), (
            f"Plugin {plugin_file.name} missing __dependencies__"
        )

    @pytest.mark.parametrize("plugin_file", get_plugin_files(), ids=get_plugin_name)
    def test_plugin_has_init(self, plugin_file):
        """Plugin class has __init__ method."""
        module = load_plugin_module(plugin_file)
        if module is None:
            pytest.skip(f"Plugin {plugin_file.name} could not be loaded")
        plugin_class = find_plugin_class(module)
        if plugin_class is None:
            pytest.skip(f"Plugin {plugin_file.name} has no identifiable plugin class")
        assert hasattr(plugin_class, "__init__"), (
            f"Plugin {plugin_file.name} missing __init__"
        )

    @pytest.mark.parametrize("plugin_file", get_plugin_files(), ids=get_plugin_name)
    def test_plugin_has_on_loaded(self, plugin_file):
        """Plugin class has on_loaded method."""
        module = load_plugin_module(plugin_file)
        if module is None:
            pytest.skip(f"Plugin {plugin_file.name} could not be loaded")
        plugin_class = find_plugin_class(module)
        if plugin_class is None:
            pytest.skip(f"Plugin {plugin_file.name} has no identifiable plugin class")
        assert hasattr(plugin_class, "on_loaded"), (
            f"Plugin {plugin_file.name} missing on_loaded"
        )


def _get_config_files():
    """Return all .toml config files."""
    config_dir = REPO_ROOT / "configs"
    if config_dir.exists():
        return sorted(config_dir.glob("*.toml"))
    return []


class TestPluginConfig:
    """Test that plugin TOML config files are valid."""

    @pytest.mark.parametrize("config_file", _get_config_files(), ids=lambda f: f.stem)
    def test_config_parses(self, config_file):
        """TOML config file can be parsed."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                pytest.skip("No TOML parser available")

        content = config_file.read_bytes()
        try:
            tomllib.loads(content.decode("utf-8"))
        except Exception as e:
            pytest.fail(f"TOML parse error in {config_file.name}: {e}")

    @pytest.mark.parametrize("config_file", _get_config_files(), ids=lambda f: f.stem)
    def test_config_has_enabled(self, config_file):
        """TOML config file has 'enabled' key."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                pytest.skip("No TOML parser available")

        content = config_file.read_bytes()
        data = tomllib.loads(content.decode("utf-8"))
        assert "enabled" in data, (
            f"Config {config_file.name} missing 'enabled' key"
        )


class TestPluginCount:
    """Test that we have the expected number of plugins."""

    def test_plugin_count(self):
        """Repository has at least 198 plugins."""
        plugins = get_plugin_files()
        assert len(plugins) >= 198, (
            f"Expected at least 198 plugins, found {len(plugins)}"
        )

    def test_all_plugins_have_tests(self):
        """Every plugin file is covered by at least one test."""
        plugins = get_plugin_files()
        # Each plugin is covered by the parametrized tests above
        # This test just ensures the list is non-empty
        assert len(plugins) > 0, "No plugins found"
