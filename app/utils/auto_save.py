from PyQt6.QtCore import QObject, QTimer
from app.utils.database.controller import DatabaseController

class AutoSave(QObject):
    def __init__(self, db_controller: DatabaseController, interval: int = 500):
        super().__init__()
        self.db_controller = db_controller
        self.timer = QTimer()
        self.timer.setInterval(interval)
        self.timer.timeout.connect(self.perform_auto_save)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def perform_auto_save(self):
        try:
            self.db_controller.commit()
            print("Changes saved automatically")
        except Exception as e:
            print(f"Auto-save failed: {str(e)}")
        finally:
            self.stop()
