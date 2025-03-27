from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenuBar


class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_menu_bar()

    def setup_menu_bar(self):
        # File menu
        file_menu = self.addMenu("&File")
        self.new_db_action = QAction("&New Database", self)
        self.open_db_action = QAction("&Open Database", self)
        self.save_action = QAction("&Save", self)
        self.save_as_action = QAction("Save &As", self)
        self.export_action = QAction("&Export", self)
        self.exit_action = QAction("E&xit", self)

        file_menu.addAction(self.new_db_action)
        file_menu.addAction(self.open_db_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # Edit menu
        edit_menu = self.addMenu("&Edit")
        self.add_row_action = QAction("&Add Row", self)
        self.delete_row_action = QAction("&Delete Row", self)
        self.add_column_action = QAction("Add &Column", self)
        self.edit_column_action = QAction("&Edit Column", self)
        self.find_action = QAction("&Find", self)
        self.replace_action = QAction("&Replace", self)

        edit_menu.addAction(self.add_row_action)
        edit_menu.addAction(self.delete_row_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.add_column_action)
        edit_menu.addAction(self.edit_column_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.find_action)
        edit_menu.addAction(self.replace_action)

        # View menu
        view_menu = self.addMenu("&View")
        self.refresh_action = QAction("&Refresh", self)
        self.zoom_in_action = QAction("Zoom &In", self)
        self.zoom_out_action = QAction("Zoom &Out", self)
        self.reset_zoom_action = QAction("&Reset Zoom", self)

        view_menu.addAction(self.refresh_action)
        view_menu.addSeparator()
        view_menu.addAction(self.zoom_in_action)
        view_menu.addAction(self.zoom_out_action)
        view_menu.addAction(self.reset_zoom_action)

        # Tools menu
        tools_menu = self.addMenu("&Tools")
        self.query_editor_action = QAction("&SQL Query Editor", self)
        self.settings_action = QAction("&Preferences", self)

        tools_menu.addAction(self.query_editor_action)
        tools_menu.addSeparator()
        tools_menu.addAction(self.settings_action)

        # Help menu
        help_menu = self.addMenu("&Help")
        self.docs_action = QAction("&Documentation", self)
        self.about_action = QAction("&About", self)

        help_menu.addAction(self.docs_action)
        help_menu.addSeparator()
        help_menu.addAction(self.about_action)
