import os

from battery_lib import POWER_SUPPLY_DIR, find_battery, read_battery, icon_name


class TestIconName:
    def test_none_battery(self):
        assert icon_name(None, 'Discharging') == 'battery-missing'
        assert icon_name(None, 'Charging') == 'battery-missing'
        assert icon_name(None, 'Full') == 'battery-missing'

    def test_charging_above_90(self):
        assert icon_name(100, 'Charging') == 'battery-full-charging'
        assert icon_name(90, 'Charging') == 'battery-full-charging'

    def test_charging_30_to_89(self):
        assert icon_name(89, 'Charging') == 'battery-good-charging'
        assert icon_name(30, 'Charging') == 'battery-good-charging'

    def test_charging_10_to_29(self):
        assert icon_name(29, 'Charging') == 'battery-low-charging'
        assert icon_name(10, 'Charging') == 'battery-low-charging'

    def test_charging_below_10(self):
        assert icon_name(9, 'Charging') == 'battery-caution-charging'
        assert icon_name(0, 'Charging') == 'battery-caution-charging'

    def test_full_counts_as_charging(self):
        assert icon_name(100, 'Full') == 'battery-full-charging'

    def test_discharging_above_90(self):
        assert icon_name(100, 'Discharging') == 'battery-full'
        assert icon_name(90, 'Discharging') == 'battery-full'

    def test_discharging_30_to_89(self):
        assert icon_name(89, 'Discharging') == 'battery-good'
        assert icon_name(30, 'Discharging') == 'battery-good'

    def test_discharging_10_to_29(self):
        assert icon_name(29, 'Discharging') == 'battery-low'
        assert icon_name(10, 'Discharging') == 'battery-low'

    def test_discharging_below_10(self):
        assert icon_name(9, 'Discharging') == 'battery-caution'
        assert icon_name(0, 'Discharging') == 'battery-caution'


class TestFindBattery:
    def test_no_power_supply_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR',
                            str(tmp_path / 'nonexistent'))
        assert find_battery() is None

    def test_finds_battery(self, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        bat_dir = ps_dir / 'BAT0'
        bat_dir.mkdir(parents=True)
        (bat_dir / 'type').write_text('Battery\n')
        (bat_dir / 'present').write_text('1\n')
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        assert find_battery() == 'BAT0'

    def test_skips_non_battery_type(self, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        ac_dir = ps_dir / 'AC0'
        ac_dir.mkdir(parents=True)
        (ac_dir / 'type').write_text('Mains\n')
        (ac_dir / 'present').write_text('1\n')
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        assert find_battery() is None

    def test_skips_not_present(self, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        bat_dir = ps_dir / 'BAT0'
        bat_dir.mkdir(parents=True)
        (bat_dir / 'type').write_text('Battery\n')
        (bat_dir / 'present').write_text('0\n')
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        assert find_battery() is None

    def test_skips_non_battery_and_returns_first_battery(self, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        ps_dir.mkdir()
        for name in ['AC0', 'BAT0', 'BAT1']:
            d = ps_dir / name
            d.mkdir()
            (d / 'type').write_text('Battery\n' if name.startswith('BAT') else 'Mains\n')
            (d / 'present').write_text('1\n')
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        result = find_battery()
        assert result is not None
        assert result.startswith('BAT')

    def test_skips_entry_when_type_file_missing(self, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        bat_dir = ps_dir / 'BAT0'
        bat_dir.mkdir(parents=True)
        (bat_dir / 'present').write_text('1\n')
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        assert find_battery() is None

    def test_skips_entry_when_present_file_missing(self, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        bat_dir = ps_dir / 'BAT0'
        bat_dir.mkdir(parents=True)
        (bat_dir / 'type').write_text('Battery\n')
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        assert find_battery() is None

    def test_skips_entry_when_type_file_unreadable(self, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        bat_dir = ps_dir / 'BAT0'
        bat_dir.mkdir(parents=True)
        type_file = bat_dir / 'type'
        type_file.write_text('Battery\n')
        type_file.chmod(0o000)
        (bat_dir / 'present').write_text('0\n')
        bat_dir.chmod(0o000)
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        try:
            result = find_battery()
        finally:
            bat_dir.chmod(0o755)
            type_file.chmod(0o644)
        assert result is None

    def test_empty_power_supply_dir(self, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        ps_dir.mkdir()
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        assert find_battery() is None


class TestReadBattery:
    def test_none_name(self):
        assert read_battery(None) == (None, None)

    def test_reads_capacity_and_status(self, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        bat_dir = ps_dir / 'BAT0'
        bat_dir.mkdir(parents=True)
        (bat_dir / 'capacity').write_text('75\n')
        (bat_dir / 'status').write_text('Discharging\n')
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        assert read_battery('BAT0') == (75, 'Discharging')

    def test_strips_whitespace(self, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        bat_dir = ps_dir / 'BAT0'
        bat_dir.mkdir(parents=True)
        (bat_dir / 'capacity').write_text('  50  \n')
        (bat_dir / 'status').write_text('  Charging  \n')
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        assert read_battery('BAT0') == (50, 'Charging')

    def test_missing_capacity_file(self, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        bat_dir = ps_dir / 'BAT0'
        bat_dir.mkdir(parents=True)
        (bat_dir / 'status').write_text('Discharging\n')
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        assert read_battery('BAT0') == (None, None)

    def test_missing_status_file(self, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        bat_dir = ps_dir / 'BAT0'
        bat_dir.mkdir(parents=True)
        (bat_dir / 'capacity').write_text('75\n')
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        assert read_battery('BAT0') == (None, None)

    def test_invalid_capacity_value(self, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        bat_dir = ps_dir / 'BAT0'
        bat_dir.mkdir(parents=True)
        (bat_dir / 'capacity').write_text('not_a_number\n')
        (bat_dir / 'status').write_text('Discharging\n')
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        assert read_battery('BAT0') == (None, None)

    def test_battery_dir_not_exists(self, tmp_path, monkeypatch):
        ps_dir = tmp_path / 'power_supply'
        ps_dir.mkdir()
        monkeypatch.setattr('battery_lib.POWER_SUPPLY_DIR', str(ps_dir))
        assert read_battery('BAT0') == (None, None)
