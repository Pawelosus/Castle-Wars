import csv
import uuid
from pathlib import Path
from datetime import datetime
from models.Card import Card

class GameLogger:
    def __init__(self) -> None:
        self.log_base_dir = Path(__file__).parent.parent / "logs"
        self.log_file_name = self.generate_unique_filename()
        self.game_state_log_file = self.init_log_file()

    def _flatten_resources(self, resources) -> list:
        return [x for resource in resources for x in resource]
    
    def init_log_file(self) -> Path:
        self.log_base_dir.mkdir(parents=True, exist_ok=True)
        csv_file = self.log_base_dir / Path(self.log_file_name)
        headers = [
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
        ]

        if not csv_file.is_file():
            with csv_file.open(mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
        return csv_file

    def log_move(self, game_data, card_played, card_discarded) -> None:
        if not self.game_state_log_file.is_file():
            raise FileNotFoundError('Cannot find the game_state_data.csv file!')

        with self.game_state_log_file.open(mode='a', newline='') as file:
            writer = csv.writer(file)
            current_player = game_data.current_player
            other_player = game_data.get_other_player(current_player)
            writer.writerow([
                game_data.turn_count,
                current_player.id,
                other_player.id,
                current_player.castle_hp,
                current_player.fence_hp,
                self._flatten_resources(current_player.resources),
                [card.id for card in current_player.hand if isinstance(card, Card)],
                other_player.castle_hp,
                other_player.fence_hp,
                self._flatten_resources(other_player.resources),
                card_played.id,
                card_discarded,
                game_data.game_status
            ])

    def generate_unique_filename(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]  # shorten UUID to 8 chars
        return f'game_state_log_{timestamp}_{unique_id}.csv'
