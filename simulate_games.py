import os
from Game import Game
from models.BasicAIPlayer import BasicAIPlayer
from models.MCTSNNAIPlayer import MCTSNNAIPlayer
from models.RuleBasedAIPlayer import RuleBasedAIPlayer
from models.MCTSAIPlayer import MCTSAIPlayer
from utils.GameLogger import GameLogger
from config.config import Config
from argparse import ArgumentParser
from typing import Optional
from multiprocessing import Pool

NUM_THREADS = os.cpu_count()

game_results = {
    'wins': 0,
    'losses': 0,
    'draws': 0,
}

player_types = {
    'BasicAIPlayer': BasicAIPlayer,
    'RuleBasedAIPlayer': RuleBasedAIPlayer,
    'MCTSAIPlayer': MCTSAIPlayer,
    'MCTSNNAIPlayer': MCTSNNAIPlayer,
}

def print_summary(num_games: int) -> None:
    win_rate = (game_results['wins'] / num_games) * 100
    draw_rate = (game_results['draws'] / num_games) * 100
    loss_rate = 100 - win_rate - draw_rate

    print(f'{"Summary":-^30}')
    print(f'Total Games:     {num_games:>6}')
    print(f'Wins:            {game_results["wins"]:>6} ({win_rate:.2f}%)')
    print(f'Losses:          {game_results["losses"]:>6} ({loss_rate:.2f}%)')
    print(f'Ties:            {game_results["draws"]:>6} ({draw_rate:.2f}%)')
    print(f'{"-" * 30}')

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
    game_state = game_instance.to_state()
    if current_player is None:
        raise ValueError('current_player cannot be None')
    
    move = current_player.take_turn(game_state)
    game_instance.apply_move(move, logger)

def play_game(player1_type: type, player2_type: type, player1_deck: str, player2_deck: str, enable_logs: bool) -> int:
    config = Config()
    game_instance = Game()
    player_names = [config.default_cpu_name + '1', config.default_cpu_name + '2']
    logger = GameLogger() if enable_logs else None

    game_instance.setup_cpu_only(
        default_player_names = player_names,
        player1_type = player1_type,
        player2_type = player2_type,
        player1_deck = player1_deck,
        player2_deck = player2_deck
    )
    while game_instance.game_status == 0:
        handle_turn(game_instance, logger)
    
    return game_instance.game_status

def run_game_simulation(game_params: tuple) -> int:
    player1_type, player2_type, player1_deck, player2_deck, enable_logs = game_params
    return play_game(player1_type, player2_type, player1_deck, player2_deck, enable_logs)

def simulate_games(num_games: int, player1_type: type, player2_type: type, player1_deck: str, player2_deck: str, enable_logs: bool, parallel: bool) -> None:
    # Prepare the parameters for each game
    game_params = (player1_type, player2_type, player1_deck, player2_deck, enable_logs)
    
    if num_games == 1 or not parallel:
        # Single game or parallelism disabled
        results = [run_game_simulation(game_params) for _ in range(num_games)]
    else:
        if NUM_THREADS is None:
            raise ValueError('Number of threads is unknown')
        # Multiple games with parallelism
        with Pool(processes=min(num_games, NUM_THREADS//2)) as pool:
            results = pool.map(run_game_simulation, [game_params] * num_games)

    # Process results
    for result in results:
        handle_game_result(result)

    # Print summary
    print_summary(num_games)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-num_games', type=int, default=10, help='number of games to simulate')
    parser.add_argument('-player1_type', type=str, default='BasicAIPlayer', help='AI model for player1')
    parser.add_argument('-player2_type', type=str, default='BasicAIPlayer', help='AI model for player2')
    parser.add_argument('-player1_deck', type=str, default='default_deck', help='name of the player1 deck')
    parser.add_argument('-player2_deck', type=str, default='default_deck', help='name of the player2 deck')
    parser.add_argument('--enable_logs', action='store_true', help='enable game state logging')
    parser.add_argument('--parallel', action='store_true', help='improve game simulation by parallel computing')
    args = parser.parse_args()

    try:
        player1_type = player_types.get(args.player1_type)
        player2_type = player_types.get(args.player2_type)
        args.player1_deck += '.json'
        args.player2_deck += '.json'

        simulate_games(
            num_games=args.num_games,
            player1_type=player1_type,
            player2_type=player2_type,
            player1_deck=args.player1_deck,
            player2_deck=args.player2_deck,
            enable_logs=args.enable_logs,
            parallel=args.parallel
        )
    except ValueError as e:
        print(f'Error: {e}')

