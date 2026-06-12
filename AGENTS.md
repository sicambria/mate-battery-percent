# AGENTS.md — mate-battery-percent

## Structure

Single Python file `battery-percent` (200 lines). Entrypoint: `applet_fill` → `BatteryApplet` constructor, registered via `MatePanelApplet.Applet.factory_main()`.

## Commands

| Command | Purpose |
|---------|---------|
| `sudo make install` | Install applet, registration, D-Bus service |
| `sudo make uninstall` | Remove all installed files |
| `make` | Prints usage (no build step) |
| `mate-panel --replace &` | Restart panel after install/uninstall |

## Tests

| Command | Purpose |
|---------|---------|
| `make test` | Run pytest test suite (55 tests) |
| `make coverage` | Run tests with coverage report (99%+, HTML in `htmlcov/`) |

- `battery_lib.py` — pure-library functions extracted for testability (100% cov)
- `battery-percent` — GTK-dependent code tested via mock GI imports (99% cov; `__main__` guard only uncovered)

Dependencies: `python3 -m pip install pytest pytest-cov`

## Dependencies

```
python3-gi gir1.2-gtk-3.0 gir1.2-matepanelapplet-4.0
```

## Install paths

| File | System path |
|------|-------------|
| Applet script | `/usr/lib/mate-panel/battery-percent` |
| Registration | `/usr/share/mate-panel/applets/org.mate.applets.BatteryPercent.mate-panel-applet` |
| D-Bus service | `/usr/share/dbus-1/services/org.mate.panel.applet.BatteryPercentFactory.service` |

**Gotcha**: MATE panel only scans `/usr/share/mate-panel/applets/` — not `~/.local/share/`. Installing registration to a user-local path silently fails. See `errors/01-registration-file-not-found.md`.

## Battery detection

Reads `/sys/class/power_supply/<name>/capacity` and `status`. Auto-detects first entry with `type == Battery` and `present == 1`. Handles hotplug (re-checks on each 5s tick).

## Icon fallback

`battery-fair` / `battery-fair-charging` missing in default themes. Mapped to `battery-good` / `battery-good-charging` for 30–89% range.

## Applet lifecycle

- `button-press-event`: left click → `mate-power-statistics`, right click → context menu
- `change-orient`: reorients internal Gtk.Box (horizontal ↔ vertical)
- `destroy`: removes GLib timeout

## gsettings

- `org.mate.panel object-id-list` — list of applet object IDs
- `org.mate.panel.object` at `/org/mate/panel/objects/<id>/` — `applet-iid` must be `BatteryPercentFactory::BatteryPercent`
