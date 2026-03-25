import random

import game_engine
import agents
import numpy as np

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
    scores = np.zeros(100)
    for i in range(100):
        #pacman_policy = agents.pacman_reactive_agent 
        pacman_policy = agents.pacman_reactive_agent_random
        #pacman_policy = agents.keyboard_controller   
        ghost_policies = [agents.blinky_agent, agents.pinky_agent, agents.inky_agent, agents.clyde_agent] 
        frightened_ghost_policies = [agents.run_away_from_pacman for _ in range(4)]
        scores[i] = game_engine.main(pacman_policy, ghost_policies, frightened_ghost_policies, map_file='maps/originalClassic.txt')
    print("Average score: ", np.mean(scores), "Standard deviation: ", np.std(scores))
