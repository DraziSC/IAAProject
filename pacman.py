import os
import random
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context

import numpy as np

# Headless mode avoids opening many windows when benchmarking in parallel.
#os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import game_engine
import agents


def _run_one_game(seed):
    random.seed(seed)
    np.random.seed(seed)

    #pacman_policy = agents.pacman_risk_aware_agent
    #pacman_policy = agents.pacman_reactive_agent_no_random
    #acman_policy = agents.pacman_reactive_agent_random
    pacman_policy = agents.pacman_reactive_agent_no_random
    ghost_policies = [agents.blinky_agent, agents.pinky_agent, agents.inky_agent, agents.clyde_agent]
    frightened_ghost_policies = [agents.run_away_from_pacman for _ in range(4)]

    return game_engine.main(
        pacman_policy,
        ghost_policies,
        frightened_ghost_policies,
        map_file='maps/originalClassic.txt',
    )


def run_benchmark(num_games=100, num_workers=1, base_seed=42):
    seeds = [base_seed + i for i in range(num_games)]

    if num_workers <= 1:
        scores = np.array([_run_one_game(s) for s in seeds], dtype=float)
    else:
        # Use spawn for safer multiprocessing with pygame state.
        ctx = get_context('spawn')
        with ProcessPoolExecutor(max_workers=num_workers, mp_context=ctx) as pool:
            scores = np.array(list(pool.map(_run_one_game, seeds)), dtype=float)

    print('Games:', num_games, 'Workers:', num_workers)
    print('Average score:', float(np.mean(scores)), 'Standard deviation:', float(np.std(scores)))

    return scores

pacman_policy = agents.keyboard_controller
if __name__ == "__main__":
    #ghost order: 'Blinky', 'Pinky', 'Inky', 'Clyde'

    # set the seed for reproducibility
    #np.random.seed(42)
    # set seed
    random.seed(42)
    '''
    pacman_policy = agents.pacman_reactive_agent_random
    pacman_policy = agents.keyboard_controller #use the arrow keys to control pacman
    ghost_policies = [agents.random_walk for _ in range(4)] 
    frightened_ghost_policies = [agents.random_walk for _ in range(4)]
    game_engine.main(pacman_policy, ghost_policies, frightened_ghost_policies, map_file='maps/originalClassic.txt')
    '''
    #---TP1---
    # Use os.cpu_count() to utilize all cores, or set a fixed integer.
    #workers = max(1, (os.cpu_count() or 1) - 1)
    workers = 1
    run_benchmark(num_games=100, num_workers=workers, base_seed=42)
