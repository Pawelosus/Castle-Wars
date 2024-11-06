from Game import Game
from utils.GameLogger import GameLogger
from config.config import Config
from argparse import ArgumentParser
from typing import Optional

game_results = {
    'wins': 0,
    'losses': 0,
    'draws': 0,
}

def print_summary(num_games) -> None:
    win_rate = (game_results['wins'] / num_games) * 100
    draw_rate = (game_results['draws'] / num_games) * 100
    print(f'Played Games: {num_games}')
    print(f'Wins: {game_results["wins"]}/{num_games} {win_rate}%')
    print(f'Losses: {game_results["losses"]}/{num_games} {100 - win_rate - draw_rate}%')
    print(f'Ties: {game_results["draws"]}/{num_games} {draw_rate}%')

def handle_game_result(game_result: int) -> None:
    if game_result == 1:
        game_results['wins'] += 1
    elif game_result == 2:
        game_results['losses'] += 1
    elif game_result == -1:
        game_results['draws'] += 1
    else:
        raise ValueError('Invalid game result')

def handle_turn(game_instance: Game, logger: Optional[GameLogger]) -> None:
    current_player = game_instance.current_player
    if current_player is None:
        raise ValueError('current_player cannot be None')
    
    card, discarded = current_player.take_turn()
    if not discarded:
        game_instance.use_card_effect(current_player, card)
        current_player.spend_resources(card)

    current_player.discard_card(card)
    current_player.draw_card()
    game_instance.update_resources(game_instance.get_other_player(current_player))
    game_instance.set_game_status()

    if logger is not None:
        logger.log_move(game_instance, card, discarded)

    if game_instance.game_status == 0:
        game_instance.change_current_player()

def play_game(enable_logs: bool) -> int:
    config = Config()
    game_instance = Game()
    player_names = [config.default_cpu_name, config.default_cpu_name]
    logger = GameLogger() if enable_logs else None

    game_instance.setup_cpu_only(player_names)
    while game_instance.game_status == 0:
        handle_turn(game_instance, logger)
    
    return game_instance.game_status

def simulate_games(num_games: int, enable_logs: bool) -> None:
    for _ in range(num_games):
        game_result = play_game(enable_logs)
        handle_game_result(game_result)

    print_summary(num_games)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-num_games', type=int, default=10, help='number of games to simulate')
    parser.add_argument('--enable_logs', action='store_true', help='enable game state logging')
    args = parser.parse_args()

    try:
        simulate_games(args.num_games, args.enable_logs)
    except ValueError as e:
        print(f'Error: {e}')

