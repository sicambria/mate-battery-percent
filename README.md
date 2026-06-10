# mate-battery-percent

MATE Panel applet that displays battery charge level as an icon + percentage.

## Features

- Shows battery percentage text + themed icon directly in the panel
- Updates every 5 seconds
- Icon changes based on charge level (full/good/low/caution) and charging status
- Auto-detects battery devices via sysfs (`/sys/class/power_supply/`)
- Handles battery hotplug (removable batteries)
- Shows "N/A" on desktops without a battery
- Adapts layout to horizontal/vertical panel orientation
- Left-click opens MATE Power Statistics
- Right-click menu shows current battery info + Power Statistics + Remove from Panel

## Dependencies

- `python3-gi`, `gir1.2-gtk-3.0`, `gir1.2-matepanelapplet-4.0`
- MATE desktop environment (for `mate-power-statistics`)

## Installation

```sh
sudo make install
```

Then restart the panel or run `mate-panel --replace &` to pick up the new applet.

Right-click the panel → **Add to Panel** → find **Battery Percent**.

## Files

| File | Purpose |
|------|---------|
| `battery-percent` | Python applet script |
| `org.mate.applets.BatteryPercent.mate-panel-applet` | Applet registration |
| `org.mate.panel.applet.BatteryPercentFactory.service` | D-Bus activation service |
| `Makefile` | Install/uninstall targets |

## Uninstall

```sh
sudo make uninstall
```

Remove the applet from the panel, then restart the panel.
