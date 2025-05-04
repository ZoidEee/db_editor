# toolbar_functions.py (Complete Implementation)
from PyQt6.QtWidgets import (QInputDialog, QMessageBox, QFileDialog,
                             QTableWidgetItem, QDialog, QLineEdit)
from PyQt6.QtCore import QItemSelectionModel
import csv
import json
import sqlite3


def new_database(parent):
    dlg = NewDatabaseDialog(mode="new")
    if dlg.exec() == QDialog.DialogCode.Accepted:
        try:
            config = dlg.get_config()
            parent.db_controller = DatabaseController(config)
            if config['is_new']:
                parent.db_controller.create_table(
                    config['table_name'],
                    config['columns'],
                    config['initial_rows']
                )
            parent.update_ui_state()
            parent.statusBar().showMessage("Database created", 3000)
        except Exception as e:
            parent.show_error(f"Database creation failed: {str(e)}")


def open_database(parent):
    path, _ = QFileDialog.getOpenFileName(
        parent, "Open Database", "", "SQLite Databases (*.db *.sqlite)"
    )
    if path:
        try:
            parent.db_controller = DatabaseController({
                'type': 'SQLite',
                'path': path,
                'is_new': False
            })
            parent.update_ui_state()
            parent.statusBar().showMessage(f"Opened {path}", 3000)
        except Exception as e:
            parent.show_error(f"Open failed: {str(e)}")


def refresh_database(parent):
    if parent.db_controller:
        parent.load_tables()
        parent.statusBar().showMessage("Database refreshed", 2000)


def optimize_database(parent):
    if parent.db_controller:
        try:
            parent.db_controller.optimize()
            QMessageBox.information(parent, "Optimized", "Database vacuumed and optimized")
        except Exception as e:
            parent.show_error(f"Optimization failed: {str(e)}")


def change_table(parent):
    current_table = parent.current_table()
    tables = parent.db_controller.get_tables()
    table, ok = QInputDialog.getItem(
        parent, "Change Table", "Select table:", tables, 0, False
    )
    if ok and table != current_table:
        parent.load_table(table)


def new_table(parent):
    name, ok = QInputDialog.getText(
        parent, "New Table", "Table name:"
    )
    if ok and name:
        try:
            parent.db_controller.create_table(name, [('id', 'INTEGER PRIMARY KEY')])
            parent.load_tables()
        except Exception as e:
            parent.show_error(f"Table creation failed: {str(e)}")


def rename_table(parent):
    old_name = parent.current_table()
    new_name, ok = QInputDialog.getText(
        parent, "Rename Table", "New name:", text=old_name
    )
    if ok and new_name:
        try:
            parent.db_controller.rename_table(old_name, new_name)
            parent.load_tables()
        except Exception as e:
            parent.show_error(f"Rename failed: {str(e)}")


def delete_table(parent):
    table = parent.current_table()
    reply = QMessageBox.question(
        parent, "Delete Table", f"Permanently delete {table}?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
        try:
            parent.db_controller.drop_table(table)
            parent.load_tables()
        except Exception as e:
            parent.show_error(f"Delete failed: {str(e)}")


def properties_table(parent):
    table = parent.current_table()
    schema = parent.db_controller.get_schema(table)
    QMessageBox.information(
        parent,
        "Table Properties",
        f"Name: {table}\nColumns: {len(schema)}\nRows: {parent.model.rowCount()}"
    )


def edit_record(parent):
    index = parent.table.currentIndex()
    if index.isValid():
        parent.table.edit(index)


def delete_record(parent):
    if not (table := parent.current_table()):
        return
    row = parent.table.currentIndex().row()
    if row < 0: return

    try:
        record_id = parent.model.data[row]['id']
        parent.db_controller.delete_record(table, record_id)
        parent.model.refresh()
    except Exception as e:
        parent.show_error(f"Delete failed: {str(e)}")


def undo_record(parent):
    try:
        parent.db_controller.undo()
        parent.model.refresh()
    except Exception as e:
        parent.show_error(f"Undo failed: {str(e)}")


def redo_record(parent):
    try:
        parent.db_controller.redo()
        parent.model.refresh()
    except Exception as e:
        parent.show_error(f"Redo failed: {str(e)}")


def first_row(parent):
    parent.table.selectionModel().clearSelection()
    parent.table.selectRow(0)


def prev_row(parent):
    current = parent.table.currentIndex().row()
    if current > 0:
        parent.table.selectRow(current - 1)


def next_row(parent):
    current = parent.table.currentIndex().row()
    if current < parent.model.rowCount() - 1:
        parent.table.selectRow(current + 1)


def last_row(parent):
    last_row = parent.model.rowCount() - 1
    if last_row >= 0:
        parent.table.selectRow(last_row)


def add_column(parent):
    if not (table := parent.current_table()):
        return
    col_name, ok = QInputDialog.getText(
        parent, "New Column", "Column name:"
    )
    if ok and col_name:
        try:
            parent.db_controller.add_column(table, col_name, "TEXT")
            parent.model.refresh()
        except Exception as e:
            parent.show_error(f"Add column failed: {str(e)}")


def remove_column(parent):
    table = parent.current_table()
    col = parent.table.currentIndex().column()
    if col < 0: return

    col_name = parent.model.columns[col]
    reply = QMessageBox.question(
        parent, "Delete Column", f"Delete {col_name}?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
        try:
            parent.db_controller.remove_column(table, col_name)
            parent.model.refresh()
        except Exception as e:
            parent.show_error(f"Column deletion failed: {str(e)}")


def rename_column(parent):
    table = parent.current_table()
    col = parent.table.currentIndex().column()
    if col < 0: return

    old_name = parent.model.columns[col]
    new_name, ok = QInputDialog.getText(
        parent, "Rename Column", "New name:", text=old_name
    )
    if ok and new_name:
        try:
            parent.db_controller.rename_column(table, old_name, new_name)
            parent.model.refresh()
        except Exception as e:
            parent.show_error(f"Rename failed: {str(e)}")


def export_data(parent):
    if not (table := parent.current_table()):
        return
    path, _ = QFileDialog.getSaveFileName(
        parent, "Export Data", "", "CSV (*.csv);;JSON (*.json)"
    )
    if path:
        try:
            columns, data = parent.db_controller.get_table_data(table)
            if path.endswith('.csv'):
                with open(path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=columns)
                    writer.writeheader()
                    writer.writerows(data)
            elif path.endswith('.json'):
                with open(path, 'w') as f:
                    json.dump(data, f, indent=2)
            parent.statusBar().showMessage(f"Exported to {path}", 3000)
        except Exception as e:
            parent.show_error(f"Export failed: {str(e)}")


def import_data(parent):
    path, _ = QFileDialog.getOpenFileName(
        parent, "Import Data", "", "CSV (*.csv);;JSON (*.json)"
    )
    if path:
        try:
            table = parent.current_table()
            columns = parent.model.columns

            if path.endswith('.csv'):
                with open(path, 'r') as f:
                    reader = csv.DictReader(f)
                    data = [row for row in reader]
            elif path.endswith('.json'):
                with open(path, 'r') as f:
                    data = json.load(f)

            parent.db_controller.batch_insert(table, data)
            parent.model.refresh()
        except Exception as e:
            parent.show_error(f"Import failed: {str(e)}")


def commit(parent):
    try:
        parent.db_controller.commit()
        parent.statusBar().showMessage("Changes committed", 2000)
    except Exception as e:
        parent.show_error(f"Commit failed: {str(e)}")


def rollback(parent):
    try:
        parent.db_controller.rollback()
        parent.model.refresh()
    except Exception as e:
        parent.show_error(f"Rollback failed: {str(e)}")


def schema_view(parent):
    table = parent.current_table()
    schema = parent.db_controller.get_schema(table)
    schema_text = "\n".join([f"{col['name']} ({col['type']})" for col in schema])
    QMessageBox.information(parent, "Schema", schema_text)


def execute_query(parent):
    query, ok = QInputDialog.getMultiLineText(
        parent, "Execute Query", "Enter SQL Query:"
    )
    if ok and query:
        try:
            result = parent.db_controller.execute(query)
            if result:
                parent.model.refresh()
                QMessageBox.information(parent, "Result", f"Rows affected: {result}")
        except Exception as e:
            parent.show_error(f"Query failed: {str(e)}")
