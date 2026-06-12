import os

POWER_SUPPLY_DIR = '/sys/class/power_supply'


def find_battery():
    try:
        for name in os.listdir(POWER_SUPPLY_DIR):
            type_path = os.path.join(POWER_SUPPLY_DIR, name, 'type')
            present_path = os.path.join(POWER_SUPPLY_DIR, name, 'present')
            try:
                with open(type_path) as f:
                    if f.read().strip() != 'Battery':
                        continue
                with open(present_path) as f:
                    if f.read().strip() != '1':
                        continue
                return name
            except (OSError, IOError):
                continue
    except FileNotFoundError:
        pass
    return None


def read_battery(bat_name):
    if bat_name is None:
        return (None, None)
    base = os.path.join(POWER_SUPPLY_DIR, bat_name)
    try:
        with open(os.path.join(base, 'capacity')) as f:
            pct = int(f.read().strip())
        with open(os.path.join(base, 'status')) as f:
            status = f.read().strip()
        return (pct, status)
    except (OSError, IOError, ValueError):
        return (None, None)


def icon_name(pct, status):
    if pct is None:
        return 'battery-missing'
    charging = (status in ('Charging', 'Full'))
    if charging:
        if pct >= 90:
            return 'battery-full-charging'
        if pct >= 30:
            return 'battery-good-charging'
        if pct >= 10:
            return 'battery-low-charging'
        return 'battery-caution-charging'
    else:
        if pct >= 90:
            return 'battery-full'
        if pct >= 30:
            return 'battery-good'
        if pct >= 10:
            return 'battery-low'
        return 'battery-caution'
