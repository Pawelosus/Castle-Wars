import resources.resources_ui  # Loads in all resource files into UI
from PyQt6 import uic
from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import QTimer
from workers.ResourceLoadWorker import ResourceLoadWorker

class SplashScreenView(QFrame):
    SMOOTH_TICK_MS = 30
    SMOOTH_STEP = 1.5  # max progress units per tick (~50 units/sec)

    def __init__(self, parent, done_callback) -> None:
        super().__init__(parent)
        self.done_callback = done_callback
        self._finished = False
        self._load_complete = False
        self._loaded_resources = None
        self._target_progress = 0
        self._displayed_progress = 0.0

        uic.loadUi("views/splash_screen_view.ui", self)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self._worker = ResourceLoadWorker()
        self._worker.progress.connect(self._on_progress)
        self._worker.status.connect(self.status_label.setText)
        self._worker.finished.connect(self._on_load_finished)
        self._worker.start()

        self._smooth_timer = QTimer(self)
        self._smooth_timer.setInterval(self.SMOOTH_TICK_MS)
        self._smooth_timer.timeout.connect(self._smooth_tick)
        self._smooth_timer.start()

    def _on_progress(self, value: int) -> None:
        self._target_progress = value

    def _smooth_tick(self) -> None:
        if self._displayed_progress < self._target_progress:
            self._displayed_progress = min(
                self._displayed_progress + self.SMOOTH_STEP,
                float(self._target_progress)
            )
            self.progress_bar.setValue(int(self._displayed_progress))

        if self._load_complete and int(self._displayed_progress) >= 100:
            self.status_label.setText("Ready!")
            self._finish()

    def _on_load_finished(self, ai_models: list) -> None:
        self._loaded_resources = ai_models
        self._load_complete = True
        self._target_progress = 100

    def _finish(self) -> None:
        if self._finished:
            return
        self._finished = True
        self._smooth_timer.stop()
        self._worker.quit()
        self._worker.wait()
        self.done_callback(self._loaded_resources)
