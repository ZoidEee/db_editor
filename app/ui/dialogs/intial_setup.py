import os
import sqlite3

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox, QTableWidget,
                             QTableWidgetItem, QSpinBox, QMessageBox, QHeaderView,
                             QFileDialog)


class InitialSetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQLite Database Setup")
        self.setMinimumSize(600, 400)
        self.setup_ui()
        self.is_opening_existing = False

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Database name row
        db_row = QHBoxLayout()
        db_row.addWidget(QLabel("Database Path:"))
        self.db_name_input = QLineEdit()
        self.db_name_input.setPlaceholderText("Enter new name or browse existing")
        self.browse_btn = QPushButton("Browse")
        db_row.addWidget(self.db_name_input)
        db_row.addWidget(self.browse_btn)
        layout.addLayout(db_row)

        # Table name and actions row
        table_action_row = QHBoxLayout()
        table_action_row.addWidget(QLabel("Table Name:"))
        self.table_name_input = QLineEdit()
        table_action_row.addWidget(self.table_name_input)

        # Column buttons
        self.add_col_btn = QPushButton("+ Column")
        self.remove_col_btn = QPushButton("- Column")
        table_action_row.addWidget(self.add_col_btn)
        table_action_row.addWidget(self.remove_col_btn)

        # Initial rows
        table_action_row.addWidget(QLabel("Rows:"))
        self.initial_rows = QSpinBox()
        self.initial_rows.setMaximum(1000)
        self.initial_rows.setFixedWidth(50)
        table_action_row.addWidget(self.initial_rows)

        layout.addLayout(table_action_row)

        # Column table
        self.column_table = QTableWidget(0, 2)
        self.column_table.setHorizontalHeaderLabels(["Column Name", "Data Type"])
        self.column_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.column_table)

        # Dialog buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.create_btn = QPushButton("Create")
        self.open_btn = QPushButton("Open")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.create_btn)
        btn_layout.addWidget(self.open_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        # Connect signals
        self.add_col_btn.clicked.connect(self.add_column)
        self.remove_col_btn.clicked.connect(self.remove_column)
        self.create_btn.clicked.connect(self.create_database)
        self.open_btn.clicked.connect(self.open_database)
        self.cancel_btn.clicked.connect(self.reject)
        self.browse_btn.clicked.connect(self.browse_database)

    def add_column(self):
        row = self.column_table.rowCount()
        self.column_table.insertRow(row)
        self.column_table.setItem(row, 0, QTableWidgetItem(""))
        type_combo = QComboBox()
        type_combo.addItems(["TEXT", "INTEGER", "REAL", "BLOB", "DATE"])
        self.column_table.setCellWidget(row, 1, type_combo)

    def remove_column(self):
        current_row = self.column_table.currentRow()
        if current_row >= 0:
            self.column_table.removeRow(current_row)

    def browse_database(self):
        """Open file dialog to select existing database"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Database",
            "",
            "SQLite Databases (*.db *.sqlite);;All Files (*)"
        )
        if path:
            self.db_name_input.setText(path)

    def create_database(self):
        """Handle creation of new database"""
        db_path = self.db_name_input.text().strip()
        if not db_path:
            QMessageBox.warning(self, "Error", "Database path is required")
            return

        if not db_path.endswith('.db'):
            db_path += '.db'

        # Validate table setup
        if not self.table_name_input.text().strip():
            QMessageBox.warning(self, "Error", "Table name is required for new database")
            return
        if self.column_table.rowCount() == 0:
            QMessageBox.warning(self, "Error", "At least one column is required for new database")
            return

        # Check if file already exists
        if os.path.exists(db_path):
            reply = QMessageBox.question(
                self,
                "Confirm Overwrite",
                "Database already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        self.is_opening_existing = False
        self.accept()

    def open_database(self):
        """Handle opening existing database"""
        db_path = self.db_name_input.text().strip()
        if not db_path:
            QMessageBox.warning(self, "Error", "Database path is required")
            return

        if not db_path.endswith('.db'):
            db_path += '.db'

        if not os.path.exists(db_path):
            QMessageBox.warning(self, "Error", "Database file does not exist")
            return

        try:
            # Validate it's a proper SQLite database
            conn = sqlite3.connect(db_path)
            conn.close()
            self.is_opening_existing = True
            self.accept()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Invalid database: {str(e)}")
            return

    def get_config(self):
        db_path = self.db_name_input.text().strip()
        if not db_path.endswith('.db'):
            db_path += '.db'

        config = {
            'type': 'SQLite',
            'path': os.path.abspath(db_path),
            'is_new': not self.is_opening_existing,
        }

        if not self.is_opening_existing:
            config.update({
                'table_name': self.table_name_input.text(),
                'columns': [],
                'initial_rows': self.initial_rows.value()
            })
            for row in range(self.column_table.rowCount()):
                col_name = self.column_table.item(row, 0).text()
                col_type = self.column_table.cellWidget(row, 1).currentText()
                config['columns'].append((col_name, col_type))

        return config
