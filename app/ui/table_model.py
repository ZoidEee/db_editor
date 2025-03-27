from PyQt6.QtCore import Qt, QAbstractTableModel

from app.utils.database.controller import DatabaseController


class TableModel(QAbstractTableModel):
    def __init__(self, db_controller: DatabaseController, table_name: str):
        super().__init__()
        self.db_controller = db_controller
        self.table_name = table_name
        self.columns = []
        self.data = []
        self.load_data()

    def load_data(self):
        self.columns, self.data = self.db_controller.get_table_data(self.table_name)
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return len(self.data)

    def columnCount(self, parent=None):
        return len(self.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self.data[index.row()][self.columns[index.column()]])
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.columns[section]
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            row = index.row()
            column = index.column()
            column_name = self.columns[column]
            primary_key_col = self.columns[0]
            primary_key_value = self.data[row][primary_key_col]

            try:
                self.db_controller.update_record(self.table_name, primary_key_col, primary_key_value, column_name,
                                                 value)
                self.data[row][column_name] = value
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                return True
            except Exception as e:
                print(f"Failed to update record: {str(e)}")
                return False
        return False

    def flags(self, index):
        return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
