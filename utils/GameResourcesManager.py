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
    def load_ai_models() -> list[str]:
        """Returns a list of all AI model class names that inherit from AIPlayer."""
        ai_models = []

        models_dir = Path("models")
        for file in models_dir.glob("*.py"):
            module_name = file.stem
            if module_name.startswith("_"):
                continue

            try:
                module = importlib.import_module(f"models.{module_name}")
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, AIPlayer) and obj is not AIPlayer and obj.__module__ == module.__name__:
                        ai_models.append(name)
            except (ImportError, AttributeError):
                continue

        return sorted(ai_models)

    @staticmethod
    def load_decks() -> list[str]:
        """Returns a list of available deck files from the 'resources/decks' directory."""
        decks_dir = Path("resources/decks")
        deck_files = [file.stem for file in decks_dir.glob("*.json")]
        return sorted(deck_files)
