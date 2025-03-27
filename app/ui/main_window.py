import logging

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QTableWidget, QLabel, QPushButton, QComboBox,
                             QLineEdit, QHeaderView, QSpinBox,
                             QMessageBox, QDialog, QTableView)

from app.ui.dialogs.intial_setup import InitialSetupDialog
from app.ui.menu_bar import MenuBar
from app.ui.table_model import TableModel
from app.utils.auto_save import AutoSave
from app.utils.database.controller import DatabaseController

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

    def setup_menu_bar(self):
        self.menubar = MenuBar(self)
        self.setMenuBar(self.menubar)

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
        self.table = QTableView()
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


    def setup_auto_save(self):
        self.auto_save = AutoSave(self.db_controller)

    def start_auto_save_timer(self):
        self.auto_save.start()

    def perform_auto_save(self):
        self.auto_save.perform_auto_save()

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
            self.table_model = TableModel(self.db_controller, table_name)
            self.table.setModel(self.table_model)

            # Display a success message in the status bar
            self.statusBar().showMessage(f"Loaded table: {table_name}", 3000)

        except Exception as e:
            # Log and display an error message if something goes wrong
            logger.error(f"Failed to load table {table_name}: {str(e)}")
            QMessageBox.critical(self, "Load Error", f"Failed to load table {table_name}: {str(e)}")
