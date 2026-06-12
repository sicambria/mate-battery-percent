from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def common_mocks(mod):
    mod.NO_BAT_ICON = None


class TestIconNameSafe:
    def test_returns_battery_missing_when_icon_available(self, mod):
        mod.Gtk.IconTheme.get_default().has_icon.return_value = True
        mod.NO_BAT_ICON = None
        assert mod.icon_name_safe(None, 'Discharging') == 'battery-missing'

    def test_fallback_to_battery_when_missing_icon_unavailable(self, mod):
        mod.Gtk.IconTheme.get_default().has_icon.return_value = False
        mod.NO_BAT_ICON = None
        assert mod.icon_name_safe(None, 'Discharging') == 'battery'

    def test_caches_no_bat_icon_flag(self, mod):
        mod.Gtk.IconTheme.get_default().has_icon.return_value = True
        mod.NO_BAT_ICON = None
        mod.icon_name_safe(None, 'Discharging')
        assert mod.NO_BAT_ICON is True

    def test_reuses_cached_flag(self, mod):
        mod.NO_BAT_ICON = False
        mod.Gtk.IconTheme.get_default().has_icon.return_value = True
        mod.icon_name_safe(None, 'Discharging')
        assert mod.icon_name_safe(None, 'Discharging') == 'battery'

    def test_passes_through_other_icons(self, mod):
        mod.NO_BAT_ICON = True
        assert mod.icon_name_safe(75, 'Discharging') == 'battery-good'

    def test_charging_icon_passes_through(self, mod):
        mod.NO_BAT_ICON = True
        assert mod.icon_name_safe(95, 'Charging') == 'battery-full-charging'


class TestBatteryAppletConstructor:
    @pytest.fixture
    def mock_applet(self, mod):
        applet = MagicMock()
        applet.get_orient.return_value = 'up'
        return applet

    @pytest.fixture
    def applet_instance(self, mod, mock_applet):
        mod.GLib.timeout_add_seconds.return_value = 42
        with patch.object(mod, 'find_battery', return_value='BAT0'):
            with patch.object(mod, 'read_battery', return_value=(50, 'Discharging')):
                ba = mod.BatteryApplet(mock_applet)
                yield ba

    def test_stores_applet_and_battery(self, applet_instance, mock_applet):
        assert applet_instance.applet is mock_applet
        assert applet_instance.battery == 'BAT0'

    def test_creates_box(self, applet_instance, mock_applet, mod):
        mod.Gtk.Box.assert_called_once()
        assert mock_applet.add.called

    def test_creates_icon_and_label(self, applet_instance, mod):
        mod.Gtk.Image.assert_called_once()
        mod.Gtk.Label.assert_called_once()

    def test_sets_up_timeout(self, applet_instance, mod):
        mod.GLib.timeout_add_seconds.assert_called_once_with(5, applet_instance.update)

    def test_initial_update_ran(self, applet_instance, mod):
        applet_instance.icon.set_from_icon_name.assert_called()


class TestAppletFill:
    def test_applet_fill_creates_applet_and_returns_true(self, mod):
        mock_applet = MagicMock()
        mock_applet.get_orient.return_value = 'up'
        mod.GLib.timeout_add_seconds.return_value = 42
        with patch.object(mod, 'find_battery', return_value='BAT0'):
            with patch.object(mod, 'read_battery', return_value=(50, 'Discharging')):
                result = mod.applet_fill(mock_applet, None, None)
        assert result is True


class TestBatteryAppletUpdate:
    @pytest.fixture
    def applet(self, mod):
        a = MagicMock()
        a.get_orient.return_value = 'up'
        return a

    def test_sets_icon_and_label(self, mod, applet):
        mod.GLib.timeout_add_seconds.return_value = 42
        with patch.object(mod, 'find_battery', return_value='BAT0'):
            with patch.object(mod, 'read_battery', return_value=(75, 'Charging')):
                ba = mod.BatteryApplet(applet)

        assert ba.label.set_text.call_args_list[0] == (('75%',),)
        applet.set_tooltip_text.assert_called_with('Battery: 75% (Charging)')

    def test_no_battery_shows_na(self, mod, applet):
        mod.GLib.timeout_add_seconds.return_value = 42
        with patch.object(mod, 'find_battery', return_value=None):
            with patch.object(mod, 'read_battery', return_value=(None, None)):
                ba = mod.BatteryApplet(applet)

        assert ba.label.set_text.call_args_list[0] == (('N/A',),)
        applet.set_tooltip_text.assert_called_with('No battery detected')

    def test_manually_called_update(self, mod, applet):
        mod.GLib.timeout_add_seconds.return_value = 42
        with patch.object(mod, 'find_battery', return_value='BAT0'):
            with patch.object(mod, 'read_battery', return_value=(30, 'Discharging')):
                ba = mod.BatteryApplet(applet)

        ba.label.set_text.reset_mock()
        applet.set_tooltip_text.reset_mock()

        with patch.object(mod, 'read_battery', return_value=(42, 'Charging')):
            ba.update()

        ba.label.set_text.assert_called_with('42%')
        applet.set_tooltip_text.assert_called_with('Battery: 42% (Charging)')

    def test_returns_true(self, mod, applet):
        mod.GLib.timeout_add_seconds.return_value = 42
        with patch.object(mod, 'find_battery', return_value='BAT0'):
            with patch.object(mod, 'read_battery', return_value=(50, 'Discharging')):
                ba = mod.BatteryApplet(applet)
        assert ba.update() is True


class TestBatteryAppletHotplug:
    @pytest.fixture
    def applet(self, mod):
        a = MagicMock()
        a.get_orient.return_value = 'up'
        return a

    def test_rediscovers_when_battery_none(self, mod, applet, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        ps_dir.mkdir()
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        mod.POWER_SUPPLY_DIR = str(ps_dir)

        mod.GLib.timeout_add_seconds.return_value = 42
        with patch.object(mod, 'find_battery', return_value=None):
            with patch.object(mod, 'read_battery', return_value=(None, None)):
                ba = mod.BatteryApplet(applet)
        ba.label.set_text.reset_mock()

        bat0 = ps_dir / 'BAT0'
        bat0.mkdir()
        (bat0 / 'type').write_text('Battery\n')
        (bat0 / 'present').write_text('1\n')
        (bat0 / 'capacity').write_text('60\n')
        (bat0 / 'status').write_text('Discharging\n')

        ba.update()
        assert ba.battery == 'BAT0'

    def test_loses_battery_when_not_present(self, mod, applet, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        bat0_dir = ps_dir / 'BAT0'
        bat0_dir.mkdir(parents=True)
        (bat0_dir / 'type').write_text('Battery\n')
        (bat0_dir / 'present').write_text('0\n')
        (bat0_dir / 'capacity').write_text('50\n')
        (bat0_dir / 'status').write_text('Discharging\n')
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        mod.POWER_SUPPLY_DIR = str(ps_dir)

        mod.GLib.timeout_add_seconds.return_value = 42
        with patch.object(mod, 'find_battery', return_value='BAT0'):
            ba = mod.BatteryApplet(applet)
        ba.label.set_text.reset_mock()

        ba.update()
        assert ba.battery is None

    def test_loses_battery_when_present_file_gone(self, mod, applet, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        bat0_dir = ps_dir / 'BAT0'
        bat0_dir.mkdir(parents=True)
        (bat0_dir / 'type').write_text('Battery\n')
        (bat0_dir / 'capacity').write_text('50\n')
        (bat0_dir / 'status').write_text('Discharging\n')
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        mod.POWER_SUPPLY_DIR = str(ps_dir)

        mod.GLib.timeout_add_seconds.return_value = 42
        with patch.object(mod, 'find_battery', return_value='BAT0'):
            ba = mod.BatteryApplet(applet)
        ba.label.set_text.reset_mock()

        ba.update()
        assert ba.battery is None


class TestBatteryAppletCallbacks:
    @pytest.fixture
    def applet_instance(self, mod):
        mock_applet = MagicMock()
        mock_applet.get_orient.return_value = 'up'
        mod.GLib.timeout_add_seconds.return_value = 42
        with patch.object(mod, 'find_battery', return_value='BAT0'):
            with patch.object(mod, 'read_battery', return_value=(50, 'Discharging')):
                ba = mod.BatteryApplet(mock_applet)
                yield ba, mock_applet

    def test_left_click_opens_power_statistics(self, mod, applet_instance):
        ba, applet = applet_instance
        event = MagicMock()
        event.button = 1
        with patch('os.system') as mock_system:
            result = ba.on_button_press(None, event)
        assert result is True
        mock_system.assert_called_once_with('mate-power-statistics &')

    def test_right_click_shows_menu(self, mod, applet_instance):
        ba, applet = applet_instance
        event = MagicMock()
        event.button = 3
        with patch.object(ba, 'show_menu') as mock_show:
            result = ba.on_button_press(None, event)
        assert result is True
        mock_show.assert_called_once_with(event)

    def test_other_button_returns_false(self, mod, applet_instance):
        ba, applet = applet_instance
        event = MagicMock()
        event.button = 2
        result = ba.on_button_press(None, event)
        assert result is False

    def test_orient_change_to_vertical(self, mod, applet_instance):
        ba, applet = applet_instance
        ba.on_orient_change(None, 'left')
        ba.box.set_orientation.assert_called_with('vertical')

    def test_orient_change_to_horizontal(self, mod, applet_instance):
        ba, applet = applet_instance
        ba.on_orient_change(None, 'up')
        ba.box.set_orientation.assert_called_with('horizontal')

    def test_destroy_removes_timeout(self, mod, applet_instance):
        ba, applet = applet_instance
        ba.timeout_id = 99
        ba.on_destroy(None)
        mod.GLib.source_remove.assert_called_once_with(99)
        assert ba.timeout_id is None

    def test_destroy_no_timeout(self, mod, applet_instance):
        ba, applet = applet_instance
        ba.timeout_id = None
        ba.on_destroy(None)
        mod.GLib.source_remove.assert_not_called()


class TestBatteryAppletMenu:
    @pytest.fixture
    def applet_instance(self, mod):
        mock_applet = MagicMock()
        mock_applet.get_orient.return_value = 'up'
        mod.GLib.timeout_add_seconds.return_value = 42
        with patch.object(mod, 'find_battery', return_value='BAT0'):
            with patch.object(mod, 'read_battery', return_value=(50, 'Discharging')):
                ba = mod.BatteryApplet(mock_applet)
                yield ba

    def test_show_menu_creates_items(self, mod, applet_instance):
        event = MagicMock()
        applet_instance.show_menu(event)
        mod.Gtk.Menu.assert_called_once()
        mod.Gtk.MenuItem.assert_any_call(label='Battery: 50% (Discharging)')
        mod.Gtk.MenuItem.assert_any_call(label='Power Statistics')
        mod.Gtk.MenuItem.assert_any_call(label='Remove from Panel')

    def test_show_menu_no_battery_runs_without_error(self, mod, applet_instance):
        event = MagicMock()
        with patch.object(mod, 'read_battery', return_value=(None, None)):
            applet_instance.show_menu(event)
        menu = mod.Gtk.Menu.return_value
        menu.show_all.assert_called_once()
        menu.popup_at_pointer.assert_called_once_with(event)

    def test_show_menu_shows_and_pops_up(self, mod, applet_instance):
        event = MagicMock()
        applet_instance.show_menu(event)
        menu = mod.Gtk.Menu.return_value
        menu.show_all.assert_called_once()
        menu.popup_at_pointer.assert_called_once_with(event)


class TestMainBlock:
    def test_main_block_calls_factory_main(self, mod, mock_gi):
        from unittest.mock import MagicMock
        MockApplet = type('Applet', (), {
            '__gtype__': 'the_gtype',
            'factory_main': MagicMock(),
        })
        mod.MatePanelApplet.Applet = MockApplet
        mock_factory = MockApplet.factory_main

        namespace = dict(mod.__dict__)
        namespace['__name__'] = '__main__'
        with open(mod.__file__) as f:
            code = compile(f.read(), mod.__file__, 'exec')
        exec(code, namespace)

        mock_factory.assert_called_once()
        pos_args = mock_factory.call_args[0]
        assert pos_args[:3] == ('BatteryPercentFactory', True, 'the_gtype')
        assert pos_args[4] is None
        assert callable(pos_args[3])
        assert pos_args[3].__name__ == 'applet_fill'
