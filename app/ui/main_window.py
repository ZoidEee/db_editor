from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QTableWidget, QLabel, QPushButton, QComboBox,
                             QLineEdit, QHeaderView, QStatusBar, QSpinBox,
                             QTableWidgetItem, QMessageBox, QDialog)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QTimer, QSettings

from app.ui.dialogs.intial_setup import InitialSetupDialog
from app.utils.database.controller import DatabaseController
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DatabaseEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_controller = None
        self.current_table = None
        self.setup_ui()
        self.check_first_run()

    def setup_ui(self):
        self.setWindowTitle("Database Editor")
        self.setMinimumSize(1000, 700)
        self.setup_menu_bar()
        self.setup_main_window()
        self.setup_auto_save()

    def setup_main_window(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)


        # Database controls
        db_controls = QHBoxLayout()
        self.db_label = QLabel("Current Database: Not Connected")
        self.new_db_btn = QPushButton("New Database")
        self.open_db_btn = QPushButton("Open Database")
        db_controls.addWidget(self.db_label)
        db_controls.addStretch(1)
        db_controls.addWidget(self.new_db_btn)
        db_controls.addWidget(self.open_db_btn)
        main_layout.addLayout(db_controls)

        # Table selection
        table_controls = QHBoxLayout()
        self.table_combo = QComboBox()
        self.new_table_btn = QPushButton("New Table")
        table_controls.addWidget(QLabel("Select Table:"))
        table_controls.addWidget(self.table_combo)
        table_controls.addWidget(self.new_table_btn)
        main_layout.addLayout(table_controls)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_btn = QPushButton("Search")
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        main_layout.addLayout(search_layout)

        # CRUD Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.delete_button = QPushButton("Delete")
        self.add_column_button = QPushButton("Add Column")
        self.export_button = QPushButton("Export")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.add_column_button)
        button_layout.addWidget(self.export_button)
        main_layout.addLayout(button_layout)

        # Table setup
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        main_layout.addWidget(self.table)

        # Pagination controls
        pagination_layout = QHBoxLayout()
        self.prev_page_btn = QPushButton("Previous")
        self.next_page_btn = QPushButton("Next")
        self.page_number = QSpinBox()
        self.page_number.setMinimum(1)
        self.page_size = QSpinBox()
        self.page_size.setMinimum(10)
        self.page_size.setMaximum(1000)
        self.page_size.setValue(100)
        pagination_layout.addWidget(QLabel("Page:"))
        pagination_layout.addWidget(self.page_number)
        pagination_layout.addWidget(QLabel("of"))
        self.total_pages_label = QLabel("1")
        pagination_layout.addWidget(self.total_pages_label)
        pagination_layout.addStretch(1)
        pagination_layout.addWidget(QLabel("Page Size:"))
        pagination_layout.addWidget(self.page_size)
        pagination_layout.addWidget(self.prev_page_btn)
        pagination_layout.addWidget(self.next_page_btn)
        main_layout.addLayout(pagination_layout)

        self.statusBar().showMessage("Ready")

        # Connect signals
        self.new_db_btn.clicked.connect(self.show_setup_dialog)
        self.open_db_btn.clicked.connect(self.open_database)
        self.table_combo.currentTextChanged.connect(self.load_table)
        self.table.cellChanged.connect(self.handle_cell_change)

    def setup_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

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
        edit_menu = menubar.addMenu("&Edit")

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
        view_menu = menubar.addMenu("&View")

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
        tools_menu = menubar.addMenu("&Tools")

        self.query_editor_action = QAction("&SQL Query Editor", self)
        self.settings_action = QAction("&Preferences", self)

        tools_menu.addAction(self.query_editor_action)
        tools_menu.addSeparator()
        tools_menu.addAction(self.settings_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        self.docs_action = QAction("&Documentation", self)
        self.about_action = QAction("&About", self)

        help_menu.addAction(self.docs_action)
        help_menu.addSeparator()
        help_menu.addAction(self.about_action)

    def setup_auto_save(self):
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setInterval(500)
        self.auto_save_timer.timeout.connect(self.perform_auto_save)

    def check_first_run(self):
        settings = QSettings("YourCompany", "DatabaseEditor")
        if not settings.value("database_path"):
            self.show_setup_dialog()

    def show_setup_dialog(self):
        dlg = InitialSetupDialog()
        if dlg.exec() == QDialog.DialogCode.Accepted:
            config = dlg.get_config()
            logger.debug(f"Database configuration: {config}")
            try:
                self.db_controller = DatabaseController(config)
                if config['is_new'] and config['table_name']:
                    self.db_controller.create_table(config['table_name'], config['columns'], config['initial_rows'])
                self.db_label.setText(f"Current Database: {config['path']}")
                self.load_tables()
            except Exception as e:
                logger.error(f"Setup Error: {str(e)}")
                QMessageBox.critical(self, "Setup Error", f"Failed to setup database: {str(e)}")

    def open_database(self):
        # Implement opening an existing database
        pass

    def load_tables(self):
        try:
            if self.db_controller:
                tables = self.db_controller.get_tables()
                self.table_combo.clear()
                self.table_combo.addItems(tables)
                if tables:
                    self.load_table(tables[0])
        except Exception as e:
            logger.error(f"Error loading tables: {str(e)}")
            QMessageBox.warning(self, "Load Error", f"Failed to load tables: {str(e)}")

    def load_table(self, table_name):
        try:
            if not table_name:
                return

            self.current_table = table_name

            # Fetch table data and column names from the database
            columns, data = self.db_controller.get_table_data(table_name)

            # Set up the table widget with the appropriate number of columns and headers
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)
            self.table.setRowCount(len(data))

            # Populate the table with the data retrieved from the database
            for row, record in enumerate(data):
                for col, value in enumerate(record.values()):
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row, col, item)

            # Display a success message in the status bar
            self.statusBar().showMessage(f"Loaded table: {table_name}", 3000)

        except Exception as e:
            # Log and display an error message if something goes wrong
            logger.error(f"Failed to load table {table_name}: {str(e)}")
            QMessageBox.critical(self, "Load Error", f"Failed to load table {table_name}: {str(e)}")

    def handle_cell_change(self, row, column):
        if self.current_table:
            new_value = self.table.item(row, column).text()
            column_name = self.table.horizontalHeaderItem(column).text()
            primary_key_col = self.table.horizontalHeaderItem(0).text()
            primary_key_value = self.table.item(row, 0).text()
            try:
                self.db_controller.update_record(self.current_table, primary_key_col, primary_key_value, column_name, new_value)
                self.start_auto_save_timer()
            except Exception as e:
                logger.error(f"Failed to update record: {str(e)}")
                QMessageBox.critical(self, "Update Error", f"Failed to update record: {str(e)}")

    def start_auto_save_timer(self):
        self.auto_save_timer.start()

    def perform_auto_save(self):
        try:
            self.db_controller.commit()
            self.statusBar().showMessage("Changes saved", 2000)
        except Exception as e:
            logger.error(f"Auto-save failed: {str(e)}")
            QMessageBox.critical(self, "Save Error", f"Auto-save failed: {str(e)}")
        finally:
            self.auto_save_timer.stop()