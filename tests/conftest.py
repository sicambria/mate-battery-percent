from unittest.mock import MagicMock, patch

import pytest


def _build_mock_gi():
    mock_gtk = MagicMock()
    mock_gdk = MagicMock()
    mock_glib = MagicMock()
    mock_mate = MagicMock()

    orient_cls = MagicMock()
    orient_cls.LEFT = 'left'
    orient_cls.RIGHT = 'right'
    orient_cls.UP = 'up'
    orient_cls.DOWN = 'down'
    mock_mate.AppletOrient = orient_cls

    mock_gtk.Orientation = type('Orientation', (), {
        'VERTICAL': 'vertical',
        'HORIZONTAL': 'horizontal',
    })
    mock_gtk.IconSize.MENU = 'menu'
    mock_gtk.STYLE_PROVIDER_PRIORITY_APPLICATION = 'app'
    mock_gdk.EventMask.BUTTON_PRESS_MASK = 'button-press-mask'

    icon_theme = MagicMock()
    icon_theme.has_icon.return_value = True
    mock_gtk.IconTheme.get_default.return_value = icon_theme

    mock_gi = MagicMock()
    mock_gi.require_version = MagicMock()

    mock_repository = MagicMock()
    mock_repository.Gtk = mock_gtk
    mock_repository.Gdk = mock_gdk
    mock_repository.GLib = mock_glib
    mock_repository.MatePanelApplet = mock_mate

    modules = {
        'gi': mock_gi,
        'gi.repository': mock_repository,
        'gi.repository.Gtk': mock_gtk,
        'gi.repository.Gdk': mock_gdk,
        'gi.repository.GLib': mock_glib,
        'gi.repository.MatePanelApplet': mock_mate,
    }

    handles = {
        'Gtk': mock_gtk,
        'Gdk': mock_gdk,
        'GLib': mock_glib,
        'MatePanelApplet': mock_mate,
        'icon_theme': icon_theme,
    }

    return modules, handles


@pytest.fixture
def mock_gi():
    modules, handles = _build_mock_gi()
    with patch.dict('sys.modules', modules, clear=False):
        yield handles


@pytest.fixture
def mod(mock_gi):
    import importlib.machinery
    import importlib.util
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    script = os.path.join(os.path.dirname(here), 'battery-percent')
    loader = importlib.machinery.SourceFileLoader('battery_percent', script)
    spec = importlib.util.spec_from_loader('battery_percent', loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    module.NO_BAT_ICON = None
    return module
