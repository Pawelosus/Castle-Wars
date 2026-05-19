import os
import signal
from tqdm import tqdm
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

def _worker_init():
    """Make workers ignore SIGINT so the main process handles it cleanly."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def print_summary(num_games: int) -> None:
    completed = sum(game_results.values())
    win_rate  = (game_results['wins']   / completed) * 100 if completed else 0
    draw_rate = (game_results['draws']  / completed) * 100 if completed else 0
    loss_rate = 100 - win_rate - draw_rate

    print(f'\n{"Summary":-^30}')
    print(f'Total Requested: {num_games:>6}')
    print(f'Completed:       {completed:>6}')
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
    game_instance.apply_move(move=move, logger=logger)

def play_game(player1_type: type, player2_type: type, player1_deck: str, player2_deck: str, enable_logs: bool) -> int:
    config = Config()
    game_instance = Game()
    player_names = [config.default_cpu_name + '1', config.default_cpu_name + '2']
    logger = GameLogger() if enable_logs else None

    game_instance.setup_cpu_only(
        default_player_names=player_names,
        player1_type=player1_type,
        player2_type=player2_type,
        player1_deck=player1_deck,
        player2_deck=player2_deck,
    )
    while game_instance.game_status == 0:
        handle_turn(game_instance, logger)
    if logger is not None:
        logger.close()

    return game_instance.game_status

def run_game_simulation(game_params: tuple) -> int:
    player1_type, player2_type, player1_deck, player2_deck, enable_logs = game_params
    return play_game(player1_type, player2_type, player1_deck, player2_deck, enable_logs)

def simulate_games(
    num_games: int,
    player1_type: type,
    player2_type: type,
    player1_deck: str,
    player2_deck: str,
    enable_logs: bool,
    parallel: bool,
) -> None:
    game_params = [(player1_type, player2_type, player1_deck, player2_deck, enable_logs)] * num_games

    bar = tqdm(total=num_games, desc='Simulating', unit='game', colour='green')
    try:
        if num_games == 1 or not parallel:
            for params in game_params:
                handle_game_result(run_game_simulation(params))
                bar.update(1)
        else:
            if NUM_THREADS is None:
                raise ValueError('Number of threads is unknown')
            num_workers = min(num_games, NUM_THREADS // 2)
            with Pool(processes=num_workers, initializer=_worker_init) as pool:
                for result in pool.imap_unordered(run_game_simulation, game_params):
                    handle_game_result(result)
                    bar.update(1)
    except KeyboardInterrupt:
        print('\nInterrupted - stopping workers...')
        if 'pool' in dir():
            pool.terminate()
            pool.join()
    finally:
        bar.close()

    print_summary(num_games)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-num_games',    type=int, default=10,            help='number of games to simulate')
    parser.add_argument('-player1_type', type=str, default='BasicAIPlayer', help='AI model for player1')
    parser.add_argument('-player2_type', type=str, default='BasicAIPlayer', help='AI model for player2')
    parser.add_argument('-player1_deck', type=str, default='default_deck',  help='name of the player1 deck')
    parser.add_argument('-player2_deck', type=str, default='default_deck',  help='name of the player2 deck')
    parser.add_argument('--enable_logs', action='store_true', help='enable game state logging')
    parser.add_argument('--parallel',    action='store_true', help='run games in parallel')
    args = parser.parse_args()

    try:
        player1_type = player_types[args.player1_type]
        player2_type = player_types[args.player2_type]
        args.player1_deck += '.json'
        args.player2_deck += '.json'

        simulate_games(
            num_games=args.num_games,
            player1_type=player1_type,
            player2_type=player2_type,
            player1_deck=args.player1_deck,
            player2_deck=args.player2_deck,
            enable_logs=args.enable_logs,
            parallel=args.parallel,
        )
    except (ValueError, KeyError) as e:
        print(f'Error: {e}')