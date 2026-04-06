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

def displayAllResults(results):
    import matplotlib.pyplot as plt

    # Extract data for plotting
    policy_names = [name for name, _, _ in results]
    average_scores = [np.mean(scores) for _, scores, _ in results]
    std_devs = [np.std(scores) for _, scores, _ in results]
    wins = [winners for _, _, winners in results]   
    max_scores = [np.max(scores) for _, scores, _ in results]
    min_scores = [np.min(scores) for _, scores, _ in results]

    # Create bar chart for average scores with error bars for standard deviation
    plt.figure(figsize=(10, 6))
    plt.bar(policy_names, average_scores, yerr=std_devs, capsize=5, color='skyblue')
    plt.ylabel('Average Score')
    plt.title('Average Scores of Pacman Policies with Standard Deviation')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Create bar chart for average score max score min score and wins
    plt.figure(figsize=(10, 6))
    plt.bar(policy_names, average_scores, color='skyblue', label='Average Score')  
    plt.bar(policy_names, max_scores, color='lightgreen', label='Max Score', alpha=0.7)
    plt.bar(policy_names, min_scores, color='lightcoral', label='Min Score', alpha=0.7) 
    plt.bar(policy_names, wins, color='salmon', label='Wins', alpha=0.7)
    plt.ylabel('Count')
    plt.title('Average, Max and Min Scores and Wins of Pacman Policies')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # create similiar bar chart as above but have seperate bars for each metric instead of stacked bars
    plt.figure(figsize=(10, 6))
    x = np.arange(len(policy_names))
    width = 0.2
    plt.bar(x - width, average_scores, width, color='skyblue', label='Average Score')  
    plt.bar(x, max_scores, width, color='lightgreen', label='Max Score', alpha=0.7)
    plt.bar(x + width, min_scores, width, color='lightcoral', label='Min Score', alpha=0.7)
    plt.bar(x + 2*width, wins, width, color='salmon', label='Wins', alpha=0.7)
    plt.ylabel('Count')
    plt.title('Average, Max and Min Scores and Wins of Pacman Policies')
    plt.xticks(x, policy_names, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()




policyResults = [] # Store results for all policies here
USE_ORIGINAL_SEED = False # Set to False to use different seeds for each game, 
#which can help with benchmarking but reduces reproducibility.

def run_benchmark(policy, num_games=100, num_workers=1, base_seed=42):

    if USE_ORIGINAL_SEED:
        seed_policy_pairs = [(base_seed, policy) for _ in range(num_games)]
    else:
        seeds = [base_seed + i for i in range(num_games)]
        seed_policy_pairs = [(s, policy) for s in seeds]

    if num_workers <= 1:
        results = [_run_one_game(pair) for pair in seed_policy_pairs]
    else:
        # Keep parallel behavior unchanged.
        #seeds = [base_seed + i for i in range(num_games)]
        # Create (seed, policy) tuples to pass to workers
        #seed_policy_pairs = [(s, policy) for s in seeds]
        # Use spawn for safer multiprocessing with pygame state.
        ctx = get_context('spawn')
        with ProcessPoolExecutor(max_workers=num_workers, mp_context=ctx) as pool:
            results = list(pool.map(_run_one_game, seed_policy_pairs))

    scores = np.array([score for score, _ in results], dtype=float)
    wins = np.array([won for _, won in results], dtype=bool)
    winners = int(np.sum(wins))

    print('Games:', num_games, 'Workers:', num_workers)
    print('Average score:', float(np.mean(scores)), 'Standard deviation:', float(np.std(scores)))
    print('Wins:', winners)

    # Store results for later analysis
    policyResults.append((policy.__name__, scores, winners))

    return scores, wins

pacman_policy = agents.pacman_reactive_agent_random # Default policy, can be overridden in run_benchmark
if __name__ == "__main__":
    #ghost order: 'Blinky', 'Pinky', 'Inky', 'Clyde'

    # set the seed for reproducibility
    #np.random.seed(42)
    # set seed
    random.seed(42)
    RunAllPolicies = True # Set to True to run benchmark for all policies, or False to run a single policy.
    #policies = [agents.pacman_reactive_agent_no_ramdon_legal, agents.pacman_reactive_agent_random, agents.pacman_reactive_agent_no_random, agents.pacman_reactive_agent_no_random_mark1,
    #            agents.pacman_reactive_agent_no_random_mark2, agents.pacman_reactive_agent_no_random_mark3, agents.pacman_risk_aware_agent]
    policies = policies = [agents.pacman_reactive_agent_no_ramdon_legal, agents.pacman_reactive_agent_no_ramdon_legal_chaseghosts]
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
        for policy_name, scores, winners in policyResults:
            max = np.max(scores)
            min = np.min(scores)
            avg = np.mean(scores)
            std = np.std(scores)
            print(f'Policy: {policy_name}, Max Score: {max}, Min Score: {min}, Average Score: {avg}, Standard Deviation: {std}, Wins: {winners}')
    else:
        policy = policies[1] # Change this index to select a different policy from the list  
        run_benchmark(policy, num_games=100, num_workers=workers, base_seed=42)
        for policy_name, scores, winners in policyResults:
            max = np.max(scores)
            min = np.min(scores)
            avg = np.mean(scores)
            std = np.std(scores)
            print(f'Policy: {policy_name}, Max Score: {max}, Min Score: {min}, Average Score: {avg}, Standard Deviation: {std}, Wins: {winners}')
        
    displayAllResults(policyResults)





