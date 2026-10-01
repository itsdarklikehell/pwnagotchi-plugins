"""
Pytest configuration and fixtures for pwnagotchi-plugins testing.

Mocks the pwnagotchi framework so plugins can be imported and validated
without a running pwnagotchi instance.
"""

import sys
import types
import importlib
import importlib.util
import os
import ast
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Repository root
REPO_ROOT = Path(__file__).resolve().parent.parent

# Plugin directories to scan
PLUGIN_DIRS = [REPO_ROOT]

# Directories to exclude from plugin scanning
EXCLUDE_DIRS = {
    ".git", ".github", "extras", "defaults", "scripts",
    "sound", "weather", "B0rk3d", "BROKEN_WIP",
    "Old Weather with icon", "wof_assets", "img", "configs",
    "tests", "__pycache__",
}


def _ensure_pwnagotchi_mocks():
    """Install mock pwnagotchi modules if not already present."""
    if "pwnagotchi" in sys.modules:
        return

    # Create mock pwnagotchi package
    pwnagotchi = types.ModuleType("pwnagotchi")
    pwnagotchi.__path__ = []
    sys.modules["pwnagotchi"] = pwnagotchi

    # pwnagotchi.plugins
    plugins_mod = types.ModuleType("pwnagotchi.plugins")
    plugins_mod.Plugin = type("Plugin", (), {})
    plugins_mod.BasePlugin = type("BasePlugin", (), {})
    plugins_mod.toggle_plugin = MagicMock()
    sys.modules["pwnagotchi.plugins"] = plugins_mod
    pwnagotchi.plugins = plugins_mod

    # pwnagotchi.ui
    ui_mod = types.ModuleType("pwnagotchi.ui")
    ui_mod.__path__ = []
    sys.modules["pwnagotchi.ui"] = ui_mod
    pwnagotchi.ui = ui_mod

    # pwnagotchi.ui.components
    components_mod = types.ModuleType("pwnagotchi.ui.components")
    components_mod.LabeledValue = MagicMock
    components_mod.Text = MagicMock
    components_mod.Line = MagicMock
    components_mod.Rect = MagicMock
    components_mod.FilledRect = MagicMock
    components_mod.Widget = MagicMock
    sys.modules["pwnagotchi.ui.components"] = components_mod
    ui_mod.components = components_mod

    # pwnagotchi.ui.view
    view_mod = types.ModuleType("pwnagotchi.ui.view")
    view_mod.BLACK = 0
    view_mod.WHITE = 1
    view_mod.__dict__["__getattr__"] = lambda name: MagicMock()
    sys.modules["pwnagotchi.ui.view"] = view_mod
    ui_mod.view = view_mod

    # pwnagotchi.ui.fonts
    fonts_mod = types.ModuleType("pwnagotchi.ui.fonts")
    fonts_mod.Bold = MagicMock()
    fonts_mod.Medium = MagicMock()
    fonts_mod.Small = MagicMock()
    fonts_mod.Huge = MagicMock()
    sys.modules["pwnagotchi.ui.fonts"] = fonts_mod
    ui_mod.fonts = fonts_mod

    # pwnagotchi.ui.faces
    faces_mod = types.ModuleType("pwnagotchi.ui.faces")
    sys.modules["pwnagotchi.ui.faces"] = faces_mod
    ui_mod.faces = faces_mod

    # pwnagotchi.ui.web
    web_mod = types.ModuleType("pwnagotchi.ui.web")
    sys.modules["pwnagotchi.ui.web"] = web_mod
    ui_mod.web = web_mod

    # pwnagotchi.ui.hw
    hw_mod = types.ModuleType("pwnagotchi.ui.hw")
    hw_mod.__path__ = []
    sys.modules["pwnagotchi.ui.hw"] = hw_mod
    ui_mod.hw = hw_mod

    # pwnagotchi.ui.hw.base
    hw_base_mod = types.ModuleType("pwnagotchi.ui.hw.base")
    hw_base_mod.DisplayImpl = type("DisplayImpl", (), {})
    sys.modules["pwnagotchi.ui.hw.base"] = hw_base_mod
    hw_mod.base = hw_base_mod

    # pwnagotchi.utils
    utils_mod = types.ModuleType("pwnagotchi.utils")
    utils_mod.save_config = MagicMock()
    utils_mod.merge_config = MagicMock()
    utils_mod.StatusFile = MagicMock
    utils_mod.parse_version = MagicMock()
    utils_mod.remove_whitelisted = MagicMock()
    sys.modules["pwnagotchi.utils"] = utils_mod
    pwnagotchi.utils = utils_mod

    # pwnagotchi.grid
    grid_mod = types.ModuleType("pwnagotchi.grid")
    grid_mod.call = MagicMock()
    grid_mod.get_advertisement_data = MagicMock()
    sys.modules["pwnagotchi.grid"] = grid_mod
    pwnagotchi.grid = grid_mod

    # pwnagotchi.bettercap
    bettercap_mod = types.ModuleType("pwnagotchi.bettercap")
    bettercap_mod.Client = MagicMock
    sys.modules["pwnagotchi.bettercap"] = bettercap_mod
    pwnagotchi.bettercap = bettercap_mod

    # pwnagotchi.voice
    voice_mod = types.ModuleType("pwnagotchi.voice")
    voice_mod.Voice = MagicMock
    sys.modules["pwnagotchi.voice"] = voice_mod
    pwnagotchi.voice = voice_mod

    # pwnagotchi.ai
    ai_mod = types.ModuleType("pwnagotchi.ai")
    ai_mod.__path__ = []
    sys.modules["pwnagotchi.ai"] = ai_mod
    pwnagotchi.ai = ai_mod

    # pwnagotchi.ai.reward
    reward_mod = types.ModuleType("pwnagotchi.ai.reward")
    reward_mod.RewardFunction = MagicMock
    sys.modules["pwnagotchi.ai.reward"] = reward_mod
    ai_mod.reward = reward_mod

    # pwnagotchi.mesh
    mesh_mod = types.ModuleType("pwnagotchi.mesh")
    mesh_mod.__path__ = []
    sys.modules["pwnagotchi.mesh"] = mesh_mod
    pwnagotchi.mesh = mesh_mod

    # pwnagotchi.mesh.peer
    peer_mod = types.ModuleType("pwnagotchi.mesh.peer")
    peer_mod.Peer = MagicMock
    sys.modules["pwnagotchi.mesh.peer"] = peer_mod
    mesh_mod.peer = peer_mod

    # pwnagotchi.wifi
    wifi_mod = types.ModuleType("pwnagotchi.wifi")
    wifi_mod.freq_to_channel = MagicMock()
    sys.modules["pwnagotchi.wifi"] = wifi_mod
    pwnagotchi.wifi = wifi_mod

    # pwnagotchi.fs
    fs_mod = types.ModuleType("pwnagotchi.fs")
    sys.modules["pwnagotchi.fs"] = fs_mod
    pwnagotchi.fs = fs_mod

    # pwnagotchi._version
    version_mod = types.ModuleType("pwnagotchi._version")
    version_mod.__version__ = "1.0.0"
    sys.modules["pwnagotchi._version"] = version_mod

    # pwnagotchi.reboot / restart
    reboot_mod = types.ModuleType("pwnagotchi.reboot")
    sys.modules["pwnagotchi.reboot"] = reboot_mod
    pwnagotchi.reboot = reboot_mod

    restart_mod = types.ModuleType("pwnagotchi.restart")
    sys.modules["pwnagotchi.restart"] = restart_mod
    pwnagotchi.restart = restart_mod

    # pwnagotchi.agent
    agent_mod = types.ModuleType("pwnagotchi.agent")
    sys.modules["pwnagotchi.agent"] = agent_mod
    pwnagotchi.agent = agent_mod

    # pwnagotchi.config
    config_mod = types.ModuleType("pwnagotchi.config")
    sys.modules["pwnagotchi.config"] = config_mod
    pwnagotchi.config = config_mod


# Install mocks at module load time
_ensure_pwnagotchi_mocks()


def get_plugin_files():
    """Return all plugin .py files in the repository root."""
    plugins = []
    for d in PLUGIN_DIRS:
        for f in d.glob("*.py"):
            if f.name.startswith("test_") or f.name == "conftest.py":
                continue
            if f.parent.name in EXCLUDE_DIRS:
                continue
            plugins.append(f)
    return sorted(plugins)


def get_plugin_name(filepath):
    """Extract plugin name from file path."""
    return Path(filepath).stem


def load_plugin_module(filepath):
    """Dynamically load a plugin module from file path."""
    plugin_name = get_plugin_name(filepath)
    spec = importlib.util.spec_from_file_location(plugin_name, filepath)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[plugin_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        # Clean up failed import
        sys.modules.pop(plugin_name, None)
        return None
    return module


def find_plugin_class(module):
    """Find the main plugin class in a module."""
    for name in dir(module):
        obj = getattr(module, name)
        if (
            isinstance(obj, type)
            and name not in ("Plugin", "BasePlugin")
            and hasattr(obj, "__version__")
            and hasattr(obj, "__license__")
        ):
            return obj
    return None


@pytest.fixture(scope="session", autouse=True)
def pwnagotchi_mocks():
    """Ensure pwnagotchi mocks are installed for the test session."""
    _ensure_pwnagotchi_mocks()
    yield


@pytest.fixture
def plugin_files():
    """Return list of all plugin files."""
    return get_plugin_files()


@pytest.fixture
def loaded_plugins():
    """Load all plugins and return (name, module, class) tuples."""
    results = []
    for filepath in get_plugin_files():
        name = get_plugin_name(filepath)
        module = load_plugin_module(filepath)
        if module is None:
            continue
        plugin_class = find_plugin_class(module)
        results.append((name, module, plugin_class))
    return results
