#!/usr/bin/env python3
"""Minimal stylesheet test to debug styling issues."""

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

# Very simple, obvious stylesheet that should work
SIMPLE_STYLESHEET = """
    QPushButton {
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 20px;
        font-size: 12pt;
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #5dade2;
    }

    QPushButton:pressed {
        background-color: #2980b9;
    }

    QLabel {
        color: #2980b9;
        font-size: 11pt;
    }
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply stylesheet to app
    app.setStyleSheet(SIMPLE_STYLESHEET)

    # Create simple test window
    window = QWidget()
    window.setWindowTitle("Stylesheet Test")
    window.setMinimumSize(400, 200)

    layout = QVBoxLayout()

    label = QLabel("Wenn das Stylesheet funktioniert:")
    layout.addWidget(label)

    label2 = QLabel("- Dieser Text sollte blau sein (#2980b9)")
    layout.addWidget(label2)

    label3 = QLabel("- Die Buttons sollten blau sein (#3498db)")
    layout.addWidget(label3)

    button1 = QPushButton("Test Button 1")
    layout.addWidget(button1)

    button2 = QPushButton("Test Button 2")
    layout.addWidget(button2)

    window.setLayout(layout)
    window.show()

    print("=" * 60)
    print("STYLESHEET MINIMAL TEST")
    print("=" * 60)
    print("Wenn das Stylesheet funktioniert, solltest du sehen:")
    print("- Blaue Labels")
    print("- Blaue Buttons ohne Rahmen")
    print("- Hellblau beim Hover über Buttons")
    print()
    print("Wenn du NUR graue Buttons mit blauen Rahmen siehst,")
    print("dann wird das Stylesheet nicht angewendet.")
    print("=" * 60)

    sys.exit(app.exec())
