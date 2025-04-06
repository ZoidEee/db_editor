from PyQt6.QtCore import QDir, QSize
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtWidgets import QToolBar, QPushButton, QComboBox, QLineEdit, QToolButton, QMenu
import os
import sys


class DatabaseToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_toolbar()

    def setup_toolbar(self):
        self.setIconSize(QSize(20, 20))

        # Database Operations
        self.new_database_act = self.create_action("database_add.png", "New")
        self.open_database_act = self.create_action("database_open.png", "Open")
        self.refresh_database_act = self.create_action("refresh.png", "Refresh")
        self.optimize_database_act = self.create_action("optimize.png", "Optimize")

        # Tables Dropdown
        self.tables_dropdown_btn = QToolButton()
        self.tables_dropdown_btn.setText(" Tables ")
        self.tables_menu = QMenu()

        self.change_table_act = QAction("Change")
        self.new_table_act = QAction("New")
        self.rename_table_act = QAction("Rename")
        self.delete_table_act = QAction("Delete")
        self.properties_table_act = QAction("Properties")
        self.tables_menu.addAction(self.change_table_act)
        self.tables_menu.addAction(self.new_table_act)
        self.tables_menu.addAction(self.rename_table_act)
        self.tables_menu.addAction(self.delete_table_act)
        self.tables_menu.addAction(self.properties_table_act)

        self.tables_dropdown_btn.setMenu(self.tables_menu)
        self.tables_dropdown_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        # Record Operations
        self.edit_record_act = QAction("Edit")
        self.delete_record_act = QAction("Delete")
        self.undo_record_act = QAction("Undo")
        self.redo_record_act = QAction("Redo")

        # New: Row Navigation
        self.first_row_act = self.create_action("first.png", "First Record")
        self.prev_row_act = self.create_action("prev.png", "Previous Record")
        self.next_row_act = self.create_action("next.png", "Next Record")
        self.last_row_act = self.create_action("last.png", "Last Record")

        # Column Operations
        self.add_column_act = QAction("Add")
        self.remove_column_act = QAction("Remove")
        self.rename_column_act = QAction("Rename")

        # New: Data Operations
        self.export_data_act = self.create_action("export.png", "Export")
        self.import_data_act = self.create_action("import.png", "Import")

        # New: Transactions
        self.commit_act = self.create_action("commit.png", "Commit")
        self.rollback_act = self.create_action("rollback.png", "Rollback")

        # New: Schema/Query
        self.schema_view_act = self.create_action("schema.png", "View Schema")
        self.execute_query_act = self.create_action("run.png", "Execute Query")



        # Layout
        self.addAction(self.new_database_act)
        self.addAction(self.open_database_act)
        self.addAction(self.refresh_database_act)
        self.addAction(self.optimize_database_act)
        self.addSeparator()
        self.addWidget(self.tables_dropdown_btn)
        self.addSeparator()
        self.addAction(self.edit_record_act)
        self.addAction(self.delete_record_act)
        self.addAction(self.undo_record_act)
        self.addAction(self.redo_record_act)
        self.addSeparator()
        self.addAction(self.first_row_act)
        self.addAction(self.prev_row_act)
        self.addAction(self.next_row_act)
        self.addAction(self.last_row_act)
        self.addSeparator()
        self.addAction(self.add_column_act)
        self.addAction(self.remove_column_act)
        self.addAction(self.rename_column_act)
        self.addSeparator()
        self.addAction(self.export_data_act)
        self.addAction(self.import_data_act)
        self.addSeparator()
        self.addAction(self.commit_act)
        self.addAction(self.rollback_act)
        self.addSeparator()
        self.addAction(self.schema_view_act)
        self.addAction(self.execute_query_act)


    def create_action(self, icon_name, text):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        icon_path = os.path.join(BASE_DIR,"app", "ui", "images", "icons", icon_name)

        if os.path.exists(icon_path):
            action = QAction(QIcon(icon_path), text)
            action.setToolTip(text)
            return action
        else:
            print(f"Icon not found at: {icon_path}")
            return QAction(text)  # Fallback: text-only action
