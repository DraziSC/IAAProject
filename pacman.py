import os
import random
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context

import numpy as np

# Headless mode avoids opening many windows when benchmarking in parallel.
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import game_engine
import agents


def _run_one_game(args):
    seed, policy = args
    random.seed(seed)
    np.random.seed(seed)

    print(f'Running game with seed {seed} and policy {policy.__name__}')

    ghost_policies = [agents.blinky_agent, agents.pinky_agent, agents.inky_agent, agents.clyde_agent]
    frightened_ghost_policies = [agents.run_away_from_pacman for _ in range(4)]

    return game_engine.main(
        policy,
        ghost_policies,
        frightened_ghost_policies,
        map_file='maps/originalClassic.txt',
    )

policyResults = [] # Store results for all policies here
USE_ORIGINAL_SEED = False # Set to False to use different seeds for each game, which can help with benchmarking but reduces reproducibility.

def run_benchmark(policy, num_games=100, num_workers=1, base_seed=42):

    if USE_ORIGINAL_SEED:
        seed_policy_pairs = [(base_seed, policy) for _ in range(num_games)]
    else:
        seeds = [base_seed + i for i in range(num_games)]
        seed_policy_pairs = [(s, policy) for s in seeds]

    if num_workers <= 1:
        scores = np.array([_run_one_game(pair) for pair in seed_policy_pairs], dtype=float)
    else:
        # Keep parallel behavior unchanged.
        #seeds = [base_seed + i for i in range(num_games)]
        # Create (seed, policy) tuples to pass to workers
        #seed_policy_pairs = [(s, policy) for s in seeds]
        # Use spawn for safer multiprocessing with pygame state.
        ctx = get_context('spawn')
        with ProcessPoolExecutor(max_workers=num_workers, mp_context=ctx) as pool:
            scores = np.array(list(pool.map(_run_one_game, seed_policy_pairs)), dtype=float)

    print('Games:', num_games, 'Workers:', num_workers)
    print('Average score:', float(np.mean(scores)), 'Standard deviation:', float(np.std(scores)))

    # Store results for later analysis
    policyResults.append((policy.__name__, scores))

    return scores

pacman_policy = agents.pacman_reactive_agent_random # Default policy, can be overridden in run_benchmark
if __name__ == "__main__":
    #ghost order: 'Blinky', 'Pinky', 'Inky', 'Clyde'

    # set the seed for reproducibility
    #np.random.seed(42)
    # set seed
    random.seed(42)
    RunAllPolicies = False
    #policies = [agents.pacman_reactive_agent_random, agents.pacman_reactive_agent_no_random, agents.pacman_reactive_agent_no_random_mark1,
    #            agents.pacman_reactive_agent_no_random_mark2, agents.pacman_risk_aware_agent]
    policies = [agents.pacman_reactive_agent_random, agents.pacman_reactive_agent_no_random_mark1,
                agents.pacman_reactive_agent_no_random_mark2, agents.pacman_risk_aware_agent]
    '''
    pacman_policy = agents.pacman_reactive_agent_random
    pacman_policy = agents.keyboard_controller #use the arrow keys to control pacman
    ghost_policies = [agents.random_walk for _ in range(4)] 
    frightened_ghost_policies = [agents.random_walk for _ in range(4)]
    game_engine.main(pacman_policy, ghost_policies, frightened_ghost_policies, map_file='maps/originalClassic.txt')
    '''
    #---TP1---
    # Use os.cpu_count() to utilize all cores, or set a fixed integer.
    workers = max(1, (os.cpu_count() or 1) - 1)
    #workers = 1
    if(RunAllPolicies):
        # Run benchmark for all policies
        # Note: This will take a long time to run with many workers, as it runs 100 games for each of the 5 policies.
        for pacman_policy in policies:
            print(f'Running benchmark for {pacman_policy.__name__}...')
            run_benchmark(pacman_policy, num_games=100, num_workers=workers, base_seed=42)

        # After running all policies, print a summary of results
        print("\nSummary of Results:")
        for policy_name, scores in policyResults:
            avg = np.mean(scores)
            std = np.std(scores)
            print(f'Policy: {policy_name}, Average Score: {avg}, Standard Deviation: {std}')
    else:
        policy = policies[1] # Change this index to select a different policy from the list  
        run_benchmark(policy, num_games=100, num_workers=workers, base_seed=42)
    
