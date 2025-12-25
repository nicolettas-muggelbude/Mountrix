#!/usr/bin/env python3
"""Test the modern Breeze-inspired design."""

import sys
from PyQt6.QtWidgets import QApplication

from src.mountrix.gui.qt.main_window import MountrixMainWindow, get_modern_stylesheet

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Stylesheet VOR Fenster-Erstellung anwenden
    app.setStyleSheet(get_modern_stylesheet())

    # Create and show main window
    window = MountrixMainWindow()
    window.show()

    print("=" * 60)
    print("MOUNTRIX - MODERN DESIGN MIT LOGO-FARBEN")
    print("=" * 60)
    print("\nDesign Features:")
    print("✨ Fusion Style als Basis")
    print("🎨 Mountrix Logo-Farben:")
    print("   🔵 Primär-Blau: #2b85c0 (Buttons, Focus, Selection)")
    print("   🟢 Akzent-Grün: #2ecc71 (CheckBoxes, Success)")
    print("📐 Moderne abgerundete Ecken (4px radius)")
    print("🖱️  Hover-Effekte mit Logo-Farben")
    print("📝 Bessere Typography (10pt)")
    print("⚪ Optimiertes Spacing/Padding")
    print("🎯 Focus-Styles mit Mountrix-Blau")
    print("\nTeste:")
    print("- Buttons (Default-Button ist Mountrix-Blau)")
    print("- Input-Felder (Focus zeigt blauen Rand)")
    print("- CheckBoxes (Grüner Haken wenn aktiviert)")
    print("- TreeWidget (Blaue Selection)")
    print("- Settings Dialog (View → Einstellungen)")
    print("- ComboBoxes (Blauer Hover)")
    print("=" * 60)

    sys.exit(app.exec())
