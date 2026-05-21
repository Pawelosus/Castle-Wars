import importlib
import inspect
from pathlib import Path
from models.AIPlayer import AIPlayer

class GameResourcesManager:
    @staticmethod
    def resolve_ai_model(ai_model_name: str):
        """Resolve AI model string to the corresponding class."""
        try:
            module = importlib.import_module(f"models.{ai_model_name}")
            cls = getattr(module, ai_model_name)
            if issubclass(cls, AIPlayer):
                return cls
        except (ImportError, AttributeError, TypeError):
            return AIPlayer

    @staticmethod
    def load_ai_models(progress_callback=None, status_callback=None) -> list[str]:
        """Returns a list of all AI model class names that inherit from AIPlayer.

        Args:
            progress_callback: Optional callable receiving an int (0-100) after
                each file is processed, for use with progress bars.
            status_callback: Optional callable receiving a status string before
                each file is imported, for displaying loading messages.
        """
        ai_models = []

        models_dir = Path("models")
        files = [f for f in models_dir.glob("*.py") if not f.stem.startswith("_")]
        total = len(files)

        for i, file in enumerate(files):
            module_name = file.stem
            if status_callback is not None:
                status_callback(f"Loading {module_name}...")
            try:
                module = importlib.import_module(f"models.{module_name}")
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, AIPlayer) and obj is not AIPlayer and obj.__module__ == module.__name__:
                        ai_models.append(name)
            except (ImportError, AttributeError):
                pass

            if progress_callback is not None and total > 0:
                progress_callback(int((i + 1) * 100 / total))

        return sorted(ai_models)

    @staticmethod
    def load_decks() -> list[str]:
        """Returns a list of available deck files from the 'resources/decks' directory."""
        decks_dir = Path("resources/decks")
        deck_files = [file.stem for file in decks_dir.glob("*.json")]
        return sorted(deck_files)
