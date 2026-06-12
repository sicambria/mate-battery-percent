PREFIX  ?= /usr
LIBDIR  ?= $(PREFIX)/lib/mate-panel
APPLETS ?= $(PREFIX)/share/mate-panel/applets
DBUS    ?= $(PREFIX)/share/dbus-1/services

PREFIX  ?= /usr
LIBDIR  ?= $(PREFIX)/lib/mate-panel
APPLETS ?= $(PREFIX)/share/mate-panel/applets
DBUS    ?= $(PREFIX)/share/dbus-1/services

SCRIPT    = battery-percent
LIBSCRIPT = battery_lib.py
APPLET    = org.mate.applets.BatteryPercent.mate-panel-applet
SERVICE   = org.mate.panel.applet.BatteryPercentFactory.service

INSTALL   = install -D -m 0644
INSTALL_X = install -D -m 0755

all:
	@echo "usage: make install   (as root)"
	@echo "       make uninstall (as root)"
	@echo "       make test      (run tests)"
	@echo "       make coverage  (run tests with coverage)"

install:
	$(INSTALL_X) $(SCRIPT)    $(DESTDIR)$(LIBDIR)/$(SCRIPT)
	$(INSTALL_X) $(LIBSCRIPT) $(DESTDIR)$(LIBDIR)/$(LIBSCRIPT)
	$(INSTALL)   $(APPLET)    $(DESTDIR)$(APPLETS)/$(APPLET)
	$(INSTALL)   $(SERVICE)   $(DESTDIR)$(DBUS)/$(SERVICE)
	@echo "Installed battery-percent applet."
	@echo "Restart panel or run: mate-panel --replace &"

uninstall:
	rm -f $(DESTDIR)$(LIBDIR)/$(SCRIPT)
	rm -f $(DESTDIR)$(LIBDIR)/$(LIBSCRIPT)
	rm -f $(DESTDIR)$(APPLETS)/$(APPLET)
	rm -f $(DESTDIR)$(DBUS)/$(SERVICE)
	@echo "Removed battery-percent applet."
	@echo "Restart panel or run: mate-panel --replace &"

test:
	python3 -m pytest tests/ -v

coverage:
	python3 -m pytest tests/ --cov=battery_lib --cov=battery_percent --cov-report=term-missing --cov-report=html

.PHONY: all install uninstall test coverage
