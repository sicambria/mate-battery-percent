PREFIX  ?= /usr
LIBDIR  ?= $(PREFIX)/lib/mate-panel
APPLETS ?= $(PREFIX)/share/mate-panel/applets
DBUS    ?= $(PREFIX)/share/dbus-1/services

SCRIPT    = battery-percent
APPLET    = org.mate.applets.BatteryPercent.mate-panel-applet
SERVICE   = org.mate.panel.applet.BatteryPercentFactory.service

INSTALL   = install -D -m 0644
INSTALL_X = install -D -m 0755

all:
	@echo "usage: make install   (as root)"
	@echo "       make uninstall (as root)"

install:
	$(INSTALL_X) $(SCRIPT)  $(DESTDIR)$(LIBDIR)/$(SCRIPT)
	$(INSTALL)   $(APPLET)  $(DESTDIR)$(APPLETS)/$(APPLET)
	$(INSTALL)   $(SERVICE) $(DESTDIR)$(DBUS)/$(SERVICE)
	@echo "Installed battery-percent applet."
	@echo "Restart panel or run: mate-panel --replace &"

uninstall:
	rm -f $(DESTDIR)$(LIBDIR)/$(SCRIPT)
	rm -f $(DESTDIR)$(APPLETS)/$(APPLET)
	rm -f $(DESTDIR)$(DBUS)/$(SERVICE)
	@echo "Removed battery-percent applet."
	@echo "Restart panel or run: mate-panel --replace &"

.PHONY: all install uninstall
