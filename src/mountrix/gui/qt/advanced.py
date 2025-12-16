# -*- coding: utf-8 -*-
"""
Advanced mode dialog for power users.

Direct fstab entry editing with validation and syntax highlighting.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from ...core.fstab import FstabEntry


class FstabSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for fstab options."""

    def __init__(self, parent=None):
        """Initialize the syntax highlighter."""
        super().__init__(parent)

        # Define formats
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#0066CC"))
        self.keyword_format.setFontWeight(QFont.Weight.Bold)

        self.value_format = QTextCharFormat()
        self.value_format.setForeground(QColor("#008800"))

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#888888"))
        self.comment_format.setFontItalic(True)

        # Common fstab keywords
        self.keywords = [
            "defaults", "nofail", "noauto", "auto", "ro", "rw",
            "user", "users", "nouser", "exec", "noexec",
            "suid", "nosuid", "dev", "nodev", "sync", "async",
            "soft", "hard", "intr", "nointr",
            "vers", "username", "password", "credentials",
            "uid", "gid", "fmask", "dmask", "iocharset",
            "timeo", "retrans", "sec", "domain"
        ]

    def highlightBlock(self, text):
        """Highlight a block of text."""
        # Highlight keywords
        for keyword in self.keywords:
            index = text.lower().find(keyword)
            while index >= 0:
                length = len(keyword)
                self.setFormat(index, length, self.keyword_format)
                index = text.lower().find(keyword, index + length)

        # Highlight values after =
        if "=" in text:
            parts = text.split("=")
            if len(parts) >= 2:
                value_start = text.index("=") + 1
                self.setFormat(value_start, len(text) - value_start, self.value_format)

        # Highlight comments
        if "#" in text:
            comment_start = text.index("#")
            self.setFormat(comment_start, len(text) - comment_start, self.comment_format)


class AdvancedMountDialog(QDialog):
    """Advanced dialog for power users to configure mounts directly."""

    def __init__(self, parent=None, entry: FstabEntry = None):
        """
        Initialize the advanced mount dialog.

        Args:
            parent: Parent widget
            entry: Existing FstabEntry to edit (None for new entry)
        """
        super().__init__(parent)

        self.entry = entry
        self.is_edit_mode = entry is not None

        self.setWindowTitle(
            "Mount bearbeiten (Power-User)" if self.is_edit_mode else "Neuer Mount (Power-User)"
        )
        self.setMinimumSize(700, 600)

        self._setup_ui()
        self._load_entry()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()

        # Info label
        info = QLabel(
            "<b>Power-User-Modus</b><br>"
            "Konfigurieren Sie alle fstab-Parameter direkt. "
            "Änderungen werden in Echtzeit validiert."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # Source configuration
        source_group = QGroupBox("Quelle (Source)")
        source_layout = QVBoxLayout()

        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText(
            "z.B. //192.168.1.100/share, 192.168.1.100:/data, UUID=..., /dev/sdb1"
        )
        self.source_input.textChanged.connect(self._validate_and_update_preview)

        source_layout.addWidget(self.source_input)

        # Quick source templates
        source_btns_layout = QHBoxLayout()
        smb_btn = QPushButton("SMB: //host/share")
        smb_btn.clicked.connect(lambda: self.source_input.setText("//"))
        nfs_btn = QPushButton("NFS: host:/path")
        nfs_btn.clicked.connect(lambda: self.source_input.setText(":/"))
        uuid_btn = QPushButton("UUID=...")
        uuid_btn.clicked.connect(lambda: self.source_input.setText("UUID="))

        source_btns_layout.addWidget(smb_btn)
        source_btns_layout.addWidget(nfs_btn)
        source_btns_layout.addWidget(uuid_btn)
        source_layout.addLayout(source_btns_layout)

        source_group.setLayout(source_layout)
        layout.addWidget(source_group)

        # Mountpoint configuration
        mount_group = QGroupBox("Mountpoint")
        mount_layout = QFormLayout()

        self.mountpoint_input = QLineEdit()
        self.mountpoint_input.setPlaceholderText("/mnt/nas oder /media/$USER/externe")
        self.mountpoint_input.textChanged.connect(self._validate_and_update_preview)

        mount_layout.addRow("Pfad:", self.mountpoint_input)
        mount_group.setLayout(mount_layout)
        layout.addWidget(mount_group)

        # Filesystem type
        fs_group = QGroupBox("Dateisystem-Typ")
        fs_layout = QFormLayout()

        self.fstype_combo = QComboBox()
        self.fstype_combo.addItems([
            "cifs", "smb", "nfs", "nfs4",
            "ext4", "ext3", "ntfs", "exfat", "vfat"
        ])
        self.fstype_combo.setEditable(True)
        self.fstype_combo.currentTextChanged.connect(self._on_fstype_changed)
        self.fstype_combo.currentTextChanged.connect(self._validate_and_update_preview)

        fs_layout.addRow("Typ:", self.fstype_combo)
        fs_group.setLayout(fs_layout)
        layout.addWidget(fs_group)

        # Mount options
        opts_group = QGroupBox("Mount-Optionen")
        opts_layout = QVBoxLayout()

        self.options_input = QTextEdit()
        self.options_input.setMaximumHeight(80)
        self.options_input.setPlaceholderText(
            "Komma-separiert, z.B.:\ndefaults,nofail,username=admin,password=secret"
        )
        self.options_input.textChanged.connect(self._validate_and_update_preview)

        # Syntax highlighting
        self.highlighter = FstabSyntaxHighlighter(self.options_input.document())

        opts_layout.addWidget(self.options_input)

        # Common options buttons
        common_opts_layout = QHBoxLayout()

        defaults_btn = QPushButton("defaults")
        defaults_btn.clicked.connect(lambda: self._add_option("defaults"))

        nofail_btn = QPushButton("nofail")
        nofail_btn.clicked.connect(lambda: self._add_option("nofail"))

        noauto_btn = QPushButton("noauto")
        noauto_btn.clicked.connect(lambda: self._add_option("noauto"))

        ro_btn = QPushButton("ro (read-only)")
        ro_btn.clicked.connect(lambda: self._add_option("ro"))

        common_opts_layout.addWidget(defaults_btn)
        common_opts_layout.addWidget(nofail_btn)
        common_opts_layout.addWidget(noauto_btn)
        common_opts_layout.addWidget(ro_btn)

        opts_layout.addLayout(common_opts_layout)
        opts_group.setLayout(opts_layout)
        layout.addWidget(opts_group)

        # Advanced options
        adv_group = QGroupBox("Erweiterte Optionen")
        adv_layout = QFormLayout()

        self.dump_input = QLineEdit("0")
        self.dump_input.setMaximumWidth(50)
        self.dump_input.textChanged.connect(self._validate_and_update_preview)

        self.pass_input = QLineEdit("0")
        self.pass_input.setMaximumWidth(50)
        self.pass_input.textChanged.connect(self._validate_and_update_preview)

        adv_layout.addRow("Dump:", self.dump_input)
        adv_layout.addRow("Pass:", self.pass_input)

        adv_group.setLayout(adv_layout)
        layout.addWidget(adv_group)

        # Preview
        preview_group = QGroupBox("fstab-Eintrag Vorschau")
        preview_layout = QVBoxLayout()

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(80)
        self.preview_text.setFontFamily("Monospace")
        self.preview_text.setStyleSheet("background-color: #f5f5f5;")

        preview_layout.addWidget(self.preview_text)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Validation status
        self.validation_label = QLabel()
        self.validation_label.setWordWrap(True)
        layout.addWidget(self.validation_label)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

        # Initial validation
        self._validate_and_update_preview()

    def _on_fstype_changed(self, fstype):
        """Update recommended options based on filesystem type."""
        if fstype in ("cifs", "smb"):
            # Suggest SMB options
            if not self.options_input.toPlainText().strip():
                self.options_input.setPlainText("defaults,nofail,username=,password=")
        elif fstype in ("nfs", "nfs4"):
            # Suggest NFS options
            if not self.options_input.toPlainText().strip():
                self.options_input.setPlainText("defaults,nofail,soft,timeo=30")

    def _add_option(self, option):
        """Add an option to the options field."""
        current = self.options_input.toPlainText().strip()
        if current:
            # Add comma if not present
            if not current.endswith(","):
                current += ","
            self.options_input.setPlainText(current + option)
        else:
            self.options_input.setPlainText(option)

    def _validate_and_update_preview(self):
        """Validate input and update preview."""
        try:
            # Get current values
            source = self.source_input.text().strip()
            mountpoint = self.mountpoint_input.text().strip()
            fstype = self.fstype_combo.currentText().strip()
            options_text = self.options_input.toPlainText().strip()
            dump = int(self.dump_input.text() or "0")
            pass_num = int(self.pass_input.text() or "0")

            # Validate
            errors = []

            if not source:
                errors.append("Quelle darf nicht leer sein")

            if not mountpoint:
                errors.append("Mountpoint darf nicht leer sein")
            elif not mountpoint.startswith("/"):
                errors.append("Mountpoint muss mit / beginnen")

            if not fstype:
                errors.append("Dateisystem-Typ darf nicht leer sein")

            if not options_text:
                errors.append("Mindestens eine Option erforderlich (z.B. 'defaults')")

            # Parse options
            if options_text:
                options = [o.strip() for o in options_text.replace("\n", ",").split(",") if o.strip()]
            else:
                options = []

            if errors:
                self.validation_label.setText(
                    f"<font color='red'>⚠ Fehler:<br>• " + "<br>• ".join(errors) + "</font>"
                )
                self.preview_text.setPlainText("")
                return
            else:
                self.validation_label.setText(
                    "<font color='green'>✓ Konfiguration gültig</font>"
                )

            # Create entry and show preview
            entry = FstabEntry(
                source=source,
                mountpoint=mountpoint,
                fstype=fstype,
                options=options,
                dump=dump,
                pass_num=pass_num
            )

            self.preview_text.setPlainText(str(entry))

        except ValueError as e:
            self.validation_label.setText(
                f"<font color='red'>⚠ Ungültige Eingabe: {str(e)}</font>"
            )
            self.preview_text.setPlainText("")

    def _load_entry(self):
        """Load an existing entry into the dialog (edit mode)."""
        if not self.entry:
            return

        self.source_input.setText(self.entry.source)
        self.mountpoint_input.setText(self.entry.mountpoint)
        self.fstype_combo.setCurrentText(self.entry.fstype)

        if self.entry.options:
            self.options_input.setPlainText(",".join(self.entry.options))

        self.dump_input.setText(str(self.entry.dump))
        self.pass_input.setText(str(self.entry.pass_num))

    def get_entry(self) -> FstabEntry:
        """
        Get the configured fstab entry.

        Returns:
            FstabEntry: The configured entry
        """
        options_text = self.options_input.toPlainText().strip()
        options = [o.strip() for o in options_text.replace("\n", ",").split(",") if o.strip()]

        return FstabEntry(
            source=self.source_input.text().strip(),
            mountpoint=self.mountpoint_input.text().strip(),
            fstype=self.fstype_combo.currentText().strip(),
            options=options,
            dump=int(self.dump_input.text() or "0"),
            pass_num=int(self.pass_input.text() or "0")
        )


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = AdvancedMountDialog()

    if dialog.exec() == QDialog.DialogCode.Accepted:
        entry = dialog.get_entry()
        print("Created entry:", entry)

    sys.exit(0)
