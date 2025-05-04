from functools import partial

from PyQt6.QtCore import QDir, QSize
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtWidgets import QToolBar, QPushButton, QComboBox, QLineEdit, QToolButton, QMenu
import os
import sys
from app.utils.toolbar_functions import *

class DatabaseToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_toolbar()
        self.connect_actions()


    def setup_toolbar(self):
        self.setIconSize(QSize(20, 20))

        # Database Operations
        self.new_database_act = self.create_action("new-file.png", "New")
        self.open_database_act = self.create_action("import-file.png", "Open")
        self.refresh_database_act = self.create_action("refresh-file.png", "Refresh")
        self.optimize_database_act = self.create_action("optimize-file.png", "Optimize")

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
        self.edit_record_act = self.create_action("edit.png", "Edit")
        self.delete_record_act = self.create_action("delete.png", "Delete")
        self.undo_record_act = self.create_action("undo.png", "Undo")
        self.redo_record_act = self.create_action("redo.png", "Redo")

        # New: Row Navigation
        self.first_row_act = self.create_action("first-record.png", "First Record")
        self.prev_row_act = self.create_action("previous-record.png", "Previous Record")
        self.next_row_act = self.create_action("next-record.png", "Next Record")
        self.last_row_act = self.create_action("last-record.png", "Last Record")

        # Column Operations
        self.add_column_act = self.create_action("add-column.png", "Add Column")
        self.remove_column_act = self.create_action("remove-column.png", "Delete Column")
        self.rename_column_act = self.create_action("add-column.png", "Rename Column")

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

    def connect_actions(self):
        self.new_database_act.triggered.connect(partial(new_database, self.parent()))
        self.open_database_act.triggered.connect(partial(open_database, self.parent()))
        self.refresh_database_act.triggered.connect(partial(refresh_database, self.parent()))
        self.optimize_database_act.triggered.connect(partial(optimize_database, self.parent()))

        self.change_table_act.triggered.connect(partial(change_table, self.parent()))
        self.new_table_act.triggered.connect(partial(new_table, self.parent()))
        self.rename_table_act.triggered.connect(partial(rename_table, self.parent()))
        self.delete_table_act.triggered.connect(partial(delete_table, self.parent()))
        self.properties_table_act.triggered.connect(partial(properties_table, self.parent()))

        self.edit_record_act.triggered.connect(partial(edit_record, self.parent()))
        self.delete_record_act.triggered.connect(partial(delete_record, self.parent()))
        self.undo_record_act.triggered.connect(partial(undo_record, self.parent()))
        self.redo_record_act.triggered.connect(partial(redo_record, self.parent()))

        self.first_row_act.triggered.connect(partial(first_row, self.parent()))
        self.prev_row_act.triggered.connect(partial(prev_row, self.parent()))
        self.next_row_act.triggered.connect(partial(next_row, self.parent()))
        self.last_row_act.triggered.connect(partial(last_row, self.parent()))

        self.add_column_act.triggered.connect(partial(add_column, self.parent()))
        self.remove_column_act.triggered.connect(partial(remove_column, self.parent()))
        self.rename_column_act.triggered.connect(partial(rename_column, self.parent()))

        self.export_data_act.triggered.connect(partial(export_data, self.parent()))
        self.import_data_act.triggered.connect(partial(import_data, self.parent()))

        self.commit_act.triggered.connect(partial(commit, self.parent()))
        self.rollback_act.triggered.connect(partial(rollback, self.parent()))

        self.schema_view_act.triggered.connect(partial(schema_view, self.parent()))
        self.execute_query_act.triggered.connect(partial(execute_query, self.parent()))