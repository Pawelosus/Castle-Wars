from PyQt6.QtCore import QThread, pyqtSignal
from utils.GameResourcesManager import GameResourcesManager

class ResourceLoadWorker(QThread):
    progress = pyqtSignal(int)   # 0-100
    status = pyqtSignal(str)     # current loading message
    finished = pyqtSignal(list)  # sorted list of AI model class names

    def run(self):
        ai_models = GameResourcesManager.load_ai_models(
            progress_callback=self.progress.emit,
            status_callback=self.status.emit
        )
        self.finished.emit(ai_models)
