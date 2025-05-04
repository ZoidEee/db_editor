import logging
import os.path

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QTableWidget, QLabel, QPushButton, QHeaderView, QSpinBox,
                             QMessageBox, QDialog, QTableView, QLineEdit, QSizePolicy, QComboBox)

from app.ui.dialogs.intial_setup import NewDatabaseDialog
from app.ui.toolbar import DatabaseToolBar
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
        # self.current_table = None
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
        main_layout.setSpacing(15)

        # Connection Status
        status_widget = QWidget()
        status_layout = QHBoxLayout()

        database_connection_layout = QHBoxLayout()
        database_connection_layout.addWidget(QLabel("Database:"))

        self.db_connected_label = QLabel("Not Connected")
        self.db_connected_label.setStyleSheet("font-weight: bold; color: red; font-size: 16px;")
        database_connection_layout.addWidget(self.db_connected_label)

        database_connection_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)

        table_status_layout = QHBoxLayout()
        table_status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignRight)
        self.table_combo = QComboBox()
        self.table_combo.setMinimumWidth(75)
        self.table_combo.setMaximumWidth(150)

        status_layout.addLayout(database_connection_layout)
        table_status_layout.addWidget(QLabel("Table:"))
        table_status_layout.addWidget(self.table_combo)
        status_layout.addLayout(table_status_layout)
        status_widget.setLayout(status_layout)
        status_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)


        # Search Layout
        search_widget = QWidget()
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        search_layout.addWidget(self.search_box)
        search_widget.setLayout(search_layout)
        search_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Combined Layout
        top_layout = QHBoxLayout()
        top_layout.addWidget(status_widget)
        top_layout.addWidget(search_widget)

        # Add stretch factors for equal space
        top_layout.setStretch(0, 1)  # Status section
        top_layout.setStretch(1, 1)  # Search section

        main_layout.addLayout(top_layout)

        # Add Toolbar
        self.toolbar = DatabaseToolBar(self)
        self.addToolBar(self.toolbar)

        # === Sort/Export Buttons ===
        util_layout = QHBoxLayout()
        util_layout.setSpacing(5)

        # === Main Table View ===
        self.table = QTableView()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        main_layout.addWidget(self.table)

        # === Pagination ===
        pagination_layout = QHBoxLayout()
        pagination_layout.setSpacing(10)

        self.prev_page_btn = QPushButton("Previous")
        self.next_page_btn = QPushButton("Next")
        self.page_number = QSpinBox()
        self.page_number.setMinimum(1)
        self.page_size = QSpinBox()
        self.page_size.setMinimum(10)
        self.page_size.setMaximum(1000)
        self.page_size.setValue(100)

        self.prev_page_btn.setFixedWidth(80)
        self.next_page_btn.setFixedWidth(80)

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

        # === Connect Signals ===
        '''self.new_open_db_btn.clicked.connect(self.show_setup_dialog)
        self.close_db_btn.clicked.connect(self.close_database)
        self.refresh_btn.clicked.connect(self.load_table)
        self.repair_db_btn.clicked.connect(self.optimize_database)
        self.table_combo.currentTextChanged.connect(self.load_table)
        self.new_table_btn.clicked.connect(self.create_new_table)
        self.rename_table_btn.clicked.connect(self.rename_table)
        self.delete_table_btn.clicked.connect(self.delete_table)
        self.clone_table_btn.clicked.connect(self.clone_table)
        '''


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
        dlg = NewDatabaseDialog(mode="both")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            config = dlg.get_config()
            logger.debug(f"Database configuration: {config}")
            try:
                self.db_controller = DatabaseController(config)
                if config['is_new'] and config['table_name']:
                    self.db_controller.create_table(config['table_name'], config['columns'], config['initial_rows'])
                self.db_connected_label.setText(f"{os.path.basename(config['path'])}")
                self.load_tables()
            except Exception as e:
                logger.error(f"Setup Error: {str(e)}")
                QMessageBox.critical(self, "Setup Error", f"Failed to setup database: {str(e)}")

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

            # self.current_table = table_name
            self.table_model = TableModel(self.db_controller, table_name)
            self.table.setModel(self.table_model)

            # Display a success message in the status bar
            self.statusBar().showMessage(f"Loaded table: {table_name}", 3000)

        except Exception as e:
            # Log and display an error message if something goes wrong
            logger.error(f"Failed to load table {table_name}: {str(e)}")
            QMessageBox.critical(self, "Load Error", f"Failed to load table {table_name}: {str(e)}")

