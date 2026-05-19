import csv
import uuid
import atexit
from pathlib import Path
from datetime import datetime
from models.Card import Card

BATCH_SIZE = 500

class GameLogger:
    def __init__(self) -> None:
        self.log_base_dir = Path(__file__).parent.parent / "logs"
        self.log_base_dir.mkdir(parents=True, exist_ok=True)
        self.log_file_name = self.generate_unique_filename()
        self._buffer = []
        self._file = (self.log_base_dir / self.log_file_name).open(
            mode='w', newline='', buffering=8192
        )
        self._writer = csv.writer(self._file)
        atexit.register(self.close)
        self._writer.writerow([
            'Turn',
            'Current Player',
            'Opponent',
            'Player Castle HP',
            'Player Fence HP',
            'Player Resources',
            'Player Hand',
            'Opponent Castle HP',
            'Opponent Fence HP',
            'Opponent Resources',
            'Card Played',
            'Is discarded',
            'Game Status',
        ])

    def _flatten_resources(self, resources) -> list:
        return [x for resource in resources for x in resource]

    def log_move(self, game_data, card_played, card_discarded) -> None:
        current_player = game_data.current_player
        other_player = game_data.get_other_player(current_player)
        hand = [card.id for card in current_player.hand if isinstance(card, Card)]

        self._buffer.append([
            game_data.turn_count,
            current_player.id,
            other_player.id,
            current_player.castle_hp,
            current_player.fence_hp,
            self._flatten_resources(current_player.resources),
            hand,
            other_player.castle_hp,
            other_player.fence_hp,
            self._flatten_resources(other_player.resources),
            card_played.id,
            card_discarded,
            game_data.game_status
        ])

        if len(self._buffer) >= BATCH_SIZE:
            self._flush()

    def _flush(self) -> None:
        self._writer.writerows(self._buffer)
        self._buffer.clear()

    def close(self) -> None:
        if not self._file.closed:
            self._flush()
            self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def generate_unique_filename(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f'game_state_log_{timestamp}_{unique_id}.csv'