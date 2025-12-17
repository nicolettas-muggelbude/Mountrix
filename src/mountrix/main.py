# -*- coding: utf-8 -*-
"""
Main entry point for Mountrix application.

Detects desktop environment and launches appropriate GUI framework.
"""

import sys
from pathlib import Path

from .core.detector import detect_desktop_environment, DesktopEnvironment


def check_dependencies():
    """
    Check if required dependencies are available.

    Returns:
        tuple: (has_qt, has_gtk)
    """
    has_qt = False
    has_gtk = False

    try:
        import PyQt6
        has_qt = True
    except ImportError:
        pass

    try:
        import gi
        gi.require_version('Gtk', '4.0')
        from gi.repository import Gtk
        has_gtk = True
    except (ImportError, ValueError):
        pass

    return has_qt, has_gtk


def launch_qt_gui():
    """Launch PyQt6 GUI."""
    try:
        from .gui.qt.main_window import main as qt_main
        qt_main()
    except ImportError as e:
        print(f"Fehler beim Laden der Qt-GUI: {e}")
        print("Stelle sicher, dass PyQt6 installiert ist: pip install PyQt6")
        sys.exit(1)


def launch_gtk_gui():
    """Launch GTK4 GUI."""
    # TODO: Implement GTK4 GUI
    print("⚠ GTK4-GUI ist noch nicht implementiert.")
    print("Verwende stattdessen die Qt-Version...")
    launch_qt_gui()


def main():
    """Main entry point."""
    print("🚀 Mountrix wird gestartet...")

    # Detect desktop environment
    desktop = detect_desktop_environment()
    print(f"🖥️  Desktop-Umgebung erkannt: {desktop.value}")

    # Check available GUI frameworks
    has_qt, has_gtk = check_dependencies()

    if not has_qt and not has_gtk:
        print("❌ Fehler: Keine GUI-Bibliothek gefunden!")
        print("Installiere entweder:")
        print("  - PyQt6: pip install PyQt6")
        print("  - GTK4: sudo apt install python3-gi gir1.2-gtk-4.0")
        sys.exit(1)

    # Launch appropriate GUI based on desktop environment
    if desktop in (DesktopEnvironment.KDE, DesktopEnvironment.LXQT):
        # Qt-based desktops prefer Qt GUI
        if has_qt:
            print("✅ Starte Qt-GUI (nativ für deine Desktop-Umgebung)")
            launch_qt_gui()
        elif has_gtk:
            print("⚠️  Qt nicht verfügbar, nutze GTK4 als Fallback")
            launch_gtk_gui()

    elif desktop in (DesktopEnvironment.GNOME, DesktopEnvironment.XFCE, DesktopEnvironment.CINNAMON):
        # GTK-based desktops prefer GTK GUI
        if has_gtk:
            print("✅ Starte GTK4-GUI (nativ für deine Desktop-Umgebung)")
            launch_gtk_gui()
        elif has_qt:
            print("⚠️  GTK4 nicht verfügbar, nutze Qt als Fallback")
            launch_qt_gui()

    else:
        # Unknown desktop or fallback
        if has_qt:
            print("✅ Starte Qt-GUI")
            launch_qt_gui()
        elif has_gtk:
            print("✅ Starte GTK4-GUI")
            launch_gtk_gui()


if __name__ == "__main__":
    main()
