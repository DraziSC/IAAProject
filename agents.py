import game_engine
import pygame
import pacman_perceptions
import random
import numpy as np

def keyboard_controller(game_state):
    direction = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_state['running'] = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                direction = 'up'
            elif event.key == pygame.K_DOWN:
                direction = 'down'
            elif event.key == pygame.K_LEFT:
                direction = 'left'
            elif event.key == pygame.K_RIGHT:
                direction = 'right'
                
    pacman = game_state['pacman']
    grid = game_state['grid']
    grid_size = game_state['grid_size']
    
    if (direction is None and not game_engine.PACMAN_CONTINUOUS_MOTION) or direction in game_engine.get_valid_directions((pacman['x'],pacman['y']), grid, grid_size):
        pacman['previous_direction'] = pacman['direction']
        pacman['direction'] = direction
            
    elif direction is not None and direction not in game_engine.get_valid_directions((pacman['x'],pacman['y']), grid, grid_size):
        #pacman['previous_direction'] = pacman['direction']
        pacman['next_direction'] = direction
        
    elif direction is None and game_engine.PACMAN_CONTINUOUS_MOTION and pacman['next_direction'] in game_engine.get_valid_directions((pacman['x'],pacman['y']), grid, grid_size):
        pacman['previous_direction'] = pacman['direction']

        pacman['direction'] = pacman['next_direction']
        pacman['next_direction'] = None
        
def random_walk(agent, game_state):
    grid = game_state['grid']
    grid_size = game_state['grid_size']
    directions = game_engine.get_valid_directions((agent['x'],agent['y']), grid, grid_size)
    if len(directions)>1 and agent['direction'] is not None and game_engine.opposite_direction(agent['direction']) in directions:
        directions.remove(game_engine.opposite_direction(agent['direction']))

    agent['direction'] = random.choice(directions)
    

def stationary_agent(ghost, game_state):
    pass
    
#ACTIONS
def up(game_state):
    game_engine.set_pacman_direction(game_state,'up')
    
def down(game_state):
    game_engine.set_pacman_direction(game_state,'down')
    
def left(game_state):
    game_engine.set_pacman_direction(game_state,'left')
    
def right(game_state):
    game_engine.set_pacman_direction(game_state,'right')
    
##---TP1---  
# 

def pacman_reactive_agent_random(game_state):
    ##TODO: Implement the reactive agent
  
    random.choice([up, down, left, right])(game_state)

def pacman_reactive_agent_no_ramdon_legal(game_state):
    # Copy of pacman_reactive_agent_no_random, but legal directions use wall perceptions.
    pacman = game_state['pacman']

    if pacman['direction'] == 'up':
        opposite_dir = 'down'
    elif pacman['direction'] == 'down':
        opposite_dir = 'up'
    elif pacman['direction'] == 'left':
        opposite_dir = 'right'
    elif pacman['direction'] == 'right':
        opposite_dir = 'left'

    # using range = 2 to check for ghosts in adacent cells as 1 just does current cell and we want to check for ghosts
    # in the adjacent cells as well.
    # This is because the ghosts can move into the current cell in the next turn.
    if pacman_perceptions.ghost_up(game_state,2) and not pacman_perceptions.wall_down(game_state):
        down(game_state)
        #print("Moving down to avoid ghost above")
    elif pacman_perceptions.ghost_down(game_state,2) and not pacman_perceptions.wall_up(game_state):
        up(game_state)
        #print("Moving up to avoid ghost below")
    elif pacman_perceptions.ghost_left(game_state,2) and not pacman_perceptions.wall_right(game_state):
        right(game_state)
        #print("Moving right to avoid ghost on the left")
    elif pacman_perceptions.ghost_right(game_state,2) and not pacman_perceptions.wall_left(game_state):
        left(game_state)
        #print("Moving left to avoid ghost on the right")
    else:
        if pacman_perceptions.dot_up(game_state,2) and not pacman_perceptions.wall_up(game_state):
            up(game_state)
            #print("Moving up towards food")
        elif pacman_perceptions.dot_down(game_state,2) and not pacman_perceptions.wall_down(game_state):
            down(game_state)
            #print("Moving down towards food")
        elif pacman_perceptions.dot_left(game_state,2) and not pacman_perceptions.wall_left(game_state):
            left(game_state)
            #print("Moving left towards food")
        elif pacman_perceptions.dot_right(game_state,2) and not pacman_perceptions.wall_right(game_state):
            right(game_state)
            #print("Moving right towards food")
        # If no ghost or food perceived, just pick the first legal direction based on wall perceptions.
        else:
            if not pacman_perceptions.wall_up(game_state) and opposite_dir != 'up':
                up(game_state)
            elif not pacman_perceptions.wall_down(game_state) and opposite_dir != 'down':
                down(game_state)
            elif not pacman_perceptions.wall_left(game_state) and opposite_dir != 'left':
                left(game_state)
            elif not pacman_perceptions.wall_right(game_state) and opposite_dir != 'right':
                right(game_state)

def pacman_reactive_agent_no_ramdon_legal_chaseghosts(game_state):
    # Copy of pacman_reactive_agent_no_random, but legal directions use wall perceptions.
    pacman = game_state['pacman']
    
    activeghost_detection_range = 3 # How far to check for active (non-frightened) ghosts.
    frightenedghost_detection_range = 5 # How far to check for frightened ghosts. Set higher than active ghost range to try to chase them from further away.
    food_detection_range = 10 # How far to check for food. Set higher than ghost ranges to try to chase food from further away.
    
    if pacman['direction'] == 'up':
        opposite_dir = 'down'
    elif pacman['direction'] == 'down':
        opposite_dir = 'up'
    elif pacman['direction'] == 'left':
        opposite_dir = 'right'
    elif pacman['direction'] == 'right':
        opposite_dir = 'left'

    # using range = 2 to check for ghosts in adacent cells as 1 just does current cell and we want to check for ghosts
    # in the adjacent cells as well.
    # This is because the ghosts can move into the current cell in the next turn.
    if pacman_perceptions.ghost_up(game_state,activeghost_detection_range) and not pacman_perceptions.ghost_frightened_up(game_state,activeghost_detection_range) and not pacman_perceptions.wall_down(game_state):
        down(game_state)
        #print("Moving down to avoid ghost above")
    elif pacman_perceptions.ghost_down(game_state,activeghost_detection_range) and not pacman_perceptions.ghost_frightened_down(game_state,activeghost_detection_range) and not pacman_perceptions.wall_up(game_state):
        up(game_state)
        #print("Moving up to avoid ghost below")
    elif pacman_perceptions.ghost_left(game_state,activeghost_detection_range) and not pacman_perceptions.ghost_frightened_left(game_state,activeghost_detection_range) and not pacman_perceptions.wall_right(game_state):
        right(game_state)
        #print("Moving right to avoid ghost on the left")
    elif pacman_perceptions.ghost_right(game_state,activeghost_detection_range) and not pacman_perceptions.ghost_frightened_right(game_state,activeghost_detection_range) and not pacman_perceptions.wall_left(game_state):
        left(game_state)
        #print("Moving left to avoid ghost on the right")
    # if scared ghost perceived, move towards it to try to eat it for points.
    else:
        if(pacman_perceptions.ghost_frightened_up(game_state,frightenedghost_detection_range) and not pacman_perceptions.wall_up(game_state)):
            up(game_state)
        elif(pacman_perceptions.ghost_frightened_down(game_state,frightenedghost_detection_range) and not pacman_perceptions.wall_down(game_state)):
            down(game_state)
        elif(pacman_perceptions.ghost_frightened_left(game_state,frightenedghost_detection_range) and not pacman_perceptions.wall_left(game_state)):
            left(game_state)
        elif(pacman_perceptions.ghost_frightened_right(game_state,frightenedghost_detection_range) and not pacman_perceptions.wall_right(game_state)):
            right(game_state)
        else:
            if pacman_perceptions.dot_up(game_state,food_detection_range) and not pacman_perceptions.wall_up(game_state):
                up(game_state)
                #print("Moving up towards food")
            elif pacman_perceptions.dot_down(game_state,food_detection_range) and not pacman_perceptions.wall_down(game_state):
                down(game_state)
                #print("Moving down towards food")
            elif pacman_perceptions.dot_left(game_state,food_detection_range) and not pacman_perceptions.wall_left(game_state):
                left(game_state)
                #print("Moving left towards food")
            elif pacman_perceptions.dot_right(game_state,food_detection_range) and not pacman_perceptions.wall_right(game_state):
                right(game_state)
                #print("Moving right towards food")
            # If no ghost or food perceived, just pick the first legal direction based on wall perceptions.
            else:
                if not pacman_perceptions.wall_up(game_state) and opposite_dir != 'up':
                    up(game_state)
                elif not pacman_perceptions.wall_down(game_state) and opposite_dir != 'down':
                    down(game_state)
                elif not pacman_perceptions.wall_left(game_state) and opposite_dir != 'left':
                    left(game_state)
                elif not pacman_perceptions.wall_right(game_state) and opposite_dir != 'right':
                    right(game_state)


############################################################################################################################
#
#
#  Aditional agents below show what is possible to do achieve i.e. high win rate or high score by implementing
#  more complex behaviors and using more techniques such as pathfinding, advanced ghost prediction, dead end detection, etc. 
#  These however use data that is not in perceptions and should not be available to pacman. They are included to show
#  what is possible with more complex behaviors and more information, but are not meant to be used as part of the main benchmark 
#  as they are not comparable to the other agents that only use perceptions.
#
#
#############################################################################################################################

def pacman_reactive_agent_no_random(game_state):
    # Whats this doing in English? 
    '''
   Rules R1–R4 handle the most critical case: when a non-scared ghost is on the same tile,
     the agent immediately moves in the opposite direction to avoid danger. 
     Rules R5–R8 extend this behavior to adjacent tiles, ensuring the agent proactively 
     escapes nearby threats. If no ghost is detected, 
     Rule R9 activates a goal-oriented behavior: the agent selects a 
     legal direction (excluding reversal) and moves toward the nearest food source.
    '''

    # List Perceptions and Actions
    # Perceptions                                            Actions
    # Ghost up	                                             Move down
    # Ghost down	                                         Move up
    # Ghost left	                                         Move right
    # Ghost right	                                         Move left
    # No ghost	                                             Move towards closest food (using Manhattan distance) by direction
    # Legal Directions
    # Opposite Direction
    # nearest food using Manhattan distance
     
    # Production rules(table):
    # ID	    Perception	                                                                                    Action
    # R1		Non‑scared ghost on current tile AND ghost up AND legal direction	                            Move Down.
    # R2        Non‑scared ghost on current tile AND ghost down	AND legal direction	                            Move Up.
    # R3        Non‑scared ghost on current tile AND ghost left	AND legal direction	                            Move Right.
    # R4        Non‑scared ghost on current tile AND ghost right AND Legal direction	                        Move Left.
    # R5        Non‑scared ghost in any adjacent tile AND ghost up AND Legal direction                          Move Down.
    # R6        Non‑scared ghost in any adjacent tile AND ghost down AND Legal direction	                    Move Up.
    # R7        Non‑scared ghost in any adjacent tile AND ghost left AND Legal direction	                    Move Right.
    # R8        Non‑scared ghost in any adjacent tile AND ghost right AND Legal direction	                    Move Left.
    # R9		No Ghost detected AND get legal directions AND NOT opposite AND nearest food direction	        Move toward nearest food
    #    

    # Issues: 
    # 1. Nieve ghost check only checks for a single ghost and does not consider if ghost in new direction after move.
    # 2. Hunt for food is greedy and can lead to cycles/local loops
    # 3. Does not consider scared ghosts or power pellets at all.
    # 4. Does not consider mobility or dead ends at all.
    # 5. Does not consider predicted ghost movement at all.
     
    pacman = game_state['pacman']
    grid = game_state['grid']
    grid_size = game_state['grid_size']

    current_pos = (pacman['x'], pacman['y'])
    legal_dirs = game_engine.get_valid_directions(current_pos, grid, grid_size)

    if not legal_dirs:
        return

    dir_to_action = {
        'up': up,
        'down': down,
        'left': left,
        'right': right,
    }
    
    # using range = 2 to check for ghosts in adacent cells as 1 just does current cell and we want to check for ghosts 
    # in the adjacent cells as well.
    # This is because the ghosts can move into the current cell in the next turn.
    if pacman_perceptions.ghost_up(game_state,2) and 'down' in legal_dirs:
        down(game_state)
        print("Moving down to avoid ghost above")
    elif pacman_perceptions.ghost_down(game_state,2) and 'up' in legal_dirs:
        up(game_state)
        print("Moving up to avoid ghost below")
    elif pacman_perceptions.ghost_left(game_state,2) and 'right' in legal_dirs:
        right(game_state)
        print("Moving right to avoid ghost on the left")
    elif pacman_perceptions.ghost_right(game_state,2) and 'left' in legal_dirs:
        left(game_state)
        print("Moving left to avoid ghost on the right")
    else:
        food_legal_dirs = legal_dirs.copy()
        # Avoid reversing direction unless forced, to prevent oscillation.
        op = game_engine.opposite_direction(pacman['direction'])
        # Only remove the opposite direction if there are other options, otherwise we might end up with no legal moves.
        if len(food_legal_dirs) > 1 and op in food_legal_dirs:
            food_legal_dirs.remove(op)

        # If removing the opposite direction leaves us with no options, we have to allow it to prevent getting stuck.
        if not food_legal_dirs:
            food_legal_dirs = legal_dirs

        # No immediate ghost threat, move towards closest food
        # print('No immediate ghost threat, moving towards closest food' )
        food_positions = []

        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell == game_engine.DOT or cell == game_engine.POWER_PELLET:
                    food_positions.append((x, y))
        if not food_positions:
            return
        
        nearest_food = min(food_positions, key=lambda fp: game_engine.manhattan_distance(current_pos, fp))
        best_dir = food_legal_dirs[0]
        best_pos = game_engine.compute_new_pos(current_pos, best_dir)
        best_dist = game_engine.manhattan_distance(best_pos, nearest_food)
        
        # Greedily choose the move that minimizes distance to the nearest food. This can lead to local loops, but is a simple starting point.
        for d in food_legal_dirs:
            cand_pos = game_engine.compute_new_pos(current_pos, d)
            cand_dist = game_engine.manhattan_distance(cand_pos, nearest_food)
            if cand_dist < best_dist:
                best_dist = cand_dist
                best_pos = cand_pos
                best_dir = d
        dir_to_action[best_dir](game_state)

def pacman_reactive_agent_no_random_perception(game_state):
    # Copy of pacman_reactive_agent_no_random, but food search uses directional dot perceptions.
    pacman = game_state['pacman']
    grid = game_state['grid']
    grid_size = game_state['grid_size']

    current_pos = (pacman['x'], pacman['y'])
    legal_dirs = game_engine.get_valid_directions(current_pos, grid, grid_size)

    if not legal_dirs:
        return

    dir_to_action = {
        'up': up,
        'down': down,
        'left': left,
        'right': right,
    }

    if pacman_perceptions.ghost_up(game_state, 2) and 'down' in legal_dirs:
        down(game_state)
        print("Moving down to avoid ghost above")
    elif pacman_perceptions.ghost_down(game_state, 2) and 'up' in legal_dirs:
        up(game_state)
        print("Moving up to avoid ghost below")
    elif pacman_perceptions.ghost_left(game_state, 2) and 'right' in legal_dirs:
        right(game_state)
        print("Moving right to avoid ghost on the left")
    elif pacman_perceptions.ghost_right(game_state, 2) and 'left' in legal_dirs:
        left(game_state)
        print("Moving left to avoid ghost on the right")
    else:
        food_legal_dirs = legal_dirs.copy()
        op = game_engine.opposite_direction(pacman['direction'])
        if len(food_legal_dirs) > 1 and op in food_legal_dirs:
            food_legal_dirs.remove(op)

        if not food_legal_dirs:
            food_legal_dirs = legal_dirs

        visibility_range = max(grid_size)

        # Measure nearest perceived dot/pellet distance per direction.
        # Check how slow this is and optimize if needed, as it does a lot of redundant checks.
        dot_distance = {d: float('inf') for d in food_legal_dirs}
        for d in food_legal_dirs:
            for r in range(1, visibility_range + 1):
                if d == 'up' and pacman_perceptions.dot_up(game_state, r):
                    dot_distance[d] = r
                    break
                if d == 'down' and pacman_perceptions.dot_down(game_state, r):
                    dot_distance[d] = r
                    break
                if d == 'left' and pacman_perceptions.dot_left(game_state, r):
                    dot_distance[d] = r
                    break
                if d == 'right' and pacman_perceptions.dot_right(game_state, r):
                    dot_distance[d] = r
                    break

        # Choose the legal direction with the shortest perceived food distance.
        nearest_dirs = [d for d in food_legal_dirs if dot_distance[d] < float('inf')]
        if nearest_dirs:
            chosen_dir = min(nearest_dirs, key=lambda d: dot_distance[d])
            dir_to_action[chosen_dir](game_state)
            return

        # If no dot is perceived in any legal direction, fall back to first legal option.
        dir_to_action[food_legal_dirs[0]](game_state)

def pacman_reactive_agent_no_random_mark1(game_state):
    # same as no random but better checking for multiple ghosts in multiple directions. 
    # If there are ghosts in multiple directions, move in the direction with the most free spaces and no ghosts. 
    # This is a simple way to try to avoid getting trapped by multiple ghosts.
    # Also uses maze distance instead of Manhattan distance to food to better navigate around walls.
    """
    Production rules for Mark1:
    ID	    Perception	                                    Action
    R1		Non‑scared ghost on current tile	            Choose a direction that does not have a ghost and has the most free spaces (highest mobility) and is furthest away from a ghost. 
                                                            Avoid reversing direction unless forced.
    R2		Non‑scared ghost in any adjacent tile	        Choose a direction that does not have a ghost and has the most free spaces (highest mobility) and is furthest away from a ghost.
                                                            Avoid reversing direction unless forced.
    R3		No Ghost detected 	                            Move forward nearest food

    """

    pacman = game_state['pacman']
    grid = game_state['grid']
    grid_size = game_state['grid_size']
    current_pos = (pacman['x'], pacman['y'])
    legal_dirs = game_engine.get_valid_directions(current_pos, grid, grid_size)
    if not legal_dirs:
        return
    dir_to_action = {
        'up': up,
        'down': down,
        'left': left,
        'right': right,
    }

    # Check all directions for ghosts first.
    ghost_seen = {
        'up': pacman_perceptions.ghost_up(game_state, 2),
        'down': pacman_perceptions.ghost_down(game_state, 2),
        'left': pacman_perceptions.ghost_left(game_state, 2),
        'right': pacman_perceptions.ghost_right(game_state, 2),
    }

    if any(ghost_seen.values()):
        # 1) Avoid directions where a ghost is seen.
        candidate_dirs = [d for d in legal_dirs if not ghost_seen[d]]
        # all legal firections have ghosts so we are basically forced to move towards a ghost. 
        # In this case we will just pick the direction with the most free spaces and hope to outrun the ghost.
        if not candidate_dirs:
            candidate_dirs = legal_dirs.copy()

        # 2) Prefer not to reverse unless forced.
        if pacman['direction'] is not None:
            op = game_engine.opposite_direction(pacman['direction'])
            if len(candidate_dirs) > 1 and op in candidate_dirs:
                candidate_dirs.remove(op)

        # 3) Prefer moves with higher mobility (more future exits).
        max_mobility = max(
            len(game_engine.get_valid_directions(game_engine.compute_new_pos(current_pos, d), grid, grid_size))
            for d in candidate_dirs
        )
        mobility_dirs = [
            d for d in candidate_dirs
            if len(game_engine.get_valid_directions(game_engine.compute_new_pos(current_pos, d), grid, grid_size)) == max_mobility
        ]

        # 4) If still tied, choose the move that maximizes distance to the closest ghost.
        alive_ghost_positions = [(g['x'], g['y']) for g in game_state['ghosts'] if g['alive']]
        if alive_ghost_positions:
            best_dir = mobility_dirs[0]
            best_min_dist = min(
                game_engine.maze_distance(game_engine.compute_new_pos(current_pos, best_dir), gp, grid, grid_size)
                for gp in alive_ghost_positions
            )
            for d in mobility_dirs:
                cand_pos = game_engine.compute_new_pos(current_pos, d)
                cand_min_dist = min(game_engine.maze_distance(cand_pos, gp, grid, grid_size) for gp in alive_ghost_positions)
                if cand_min_dist > best_min_dist:
                    best_min_dist = cand_min_dist
                    best_dir = d
        else:
            best_dir = mobility_dirs[0]

        dir_to_action[best_dir](game_state)
        return

    if not any(ghost_seen.values()):
        # No immediate ghost threat, move towards closest food
        food_legal_dirs = legal_dirs.copy()
        op = game_engine.opposite_direction(pacman['direction'])
        if len(food_legal_dirs) > 1 and op in food_legal_dirs:
            food_legal_dirs.remove(op)

        if not food_legal_dirs:
            food_legal_dirs = legal_dirs

        food_positions = []
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell == game_engine.DOT or cell == game_engine.POWER_PELLET:
                    food_positions.append((x, y))
        if not food_positions:
            return
        
        nearest_food = min(food_positions, key=lambda fp: game_engine.maze_distance(current_pos, fp, grid, grid_size))
        best_dir = food_legal_dirs[0]
        best_pos = game_engine.compute_new_pos(current_pos, best_dir)
        best_dist = game_engine.maze_distance(best_pos, nearest_food, grid, grid_size)
        
        for d in food_legal_dirs:
            cand_pos = game_engine.compute_new_pos(current_pos, d)
            cand_dist = game_engine.maze_distance(cand_pos, nearest_food, grid, grid_size)
            if cand_dist < best_dist:
                best_dist = cand_dist
                best_pos = cand_pos
                best_dir = d
        dir_to_action[best_dir](game_state)

def pacman_reactive_agent_no_random_mark2(game_state):
    # Similiar to pacman_reactive_agent_no_random_mark1 but now chase scared ghosts when they are nearby.
    """
    Production rules for Mark2:
    ID	    Perception	                                    Action
    R1		If scared ghosts exist	                        Choose a direction that moves closer to the nearest scared ghost.
    R2      Non‑scared ghost on current tile	            Choose a direction that does not have a ghost and has the most free spaces (highest mobility) and is furthest away from a ghost.
    R3      Non‑scared ghost in any adjacent tile	        Choose a direction that does not have a ghost and has the most free spaces (highest mobility) and is furthest away from a ghost.
    R4      No Ghost detected 	                            Move forward nearest food
    """
    pacman = game_state['pacman']
    grid = game_state['grid']
    grid_size = game_state['grid_size']
    current_pos = (pacman['x'], pacman['y'])
    legal_dirs = game_engine.get_valid_directions(current_pos, grid, grid_size)
    if not legal_dirs:
        return
    dir_to_action = {
        'up': up,
        'down': down,
        'left': left,
        'right': right,
    }
    scared_ghosts = [g for g in game_state['ghosts'] if g['alive'] and g['scared']]
    if scared_ghosts:
        # Chase scared ghosts to farm points when they are edible.
        best_dir = legal_dirs[0]
        best_pos = game_engine.compute_new_pos(current_pos, best_dir)
        best_dist = min(game_engine.maze_distance(best_pos, (g['x'], g['y']), grid, grid_size) for g in scared_ghosts)
        for d in legal_dirs:
            cand_pos = game_engine.compute_new_pos(current_pos, d)
            cand_dist = min(game_engine.maze_distance(cand_pos, (g['x'], g['y']), grid, grid_size) for g in scared_ghosts)
            if cand_dist < best_dist:
                best_dist = cand_dist
                best_pos = cand_pos
                best_dir = d
        dir_to_action[best_dir](game_state)
    else:
        pacman_reactive_agent_no_random_mark1(game_state)

def pacman_reactive_agent_no_random_mark3(game_state):
    # Mark3: keep Mark1 safety behavior, and only chase scared ghosts when nearby and safe.
    """
    Production rules for Mark3:
    ID	    Perception	                                                                Action
    R1		If scared ghosts exist AND close AND no active ghosts nearby	            Choose a direction that moves closer to the nearest scared ghost.
    R2      Non‑scared ghost on current tile        	                                Choose a direction that does not have a ghost and has the most free spaces (highest mobility) and is furthest away from a ghost.
    R3      Non‑scared ghost in any adjacent tile	                                    Choose a direction that does not have a ghost and has the most free spaces (highest mobility) and is furthest away from a ghost.
    R4      No Ghost detected 	                                                        Move forward nearest food
    """
     
    pacman = game_state['pacman']
    grid = game_state['grid']
    grid_size = game_state['grid_size']
    current_pos = (pacman['x'], pacman['y'])
    legal_dirs = game_engine.get_valid_directions(current_pos, grid, grid_size)
    if not legal_dirs:
        return

    dir_to_action = {
        'up': up,
        'down': down,
        'left': left,
        'right': right,
    }

    scared_ghosts = [g for g in game_state['ghosts'] if g['alive'] and g['scared']]
    active_ghosts = [g for g in game_state['ghosts'] if g['alive'] and not g['scared']]

    if not scared_ghosts:
        pacman['_mark3_stall_steps'] = 0
        pacman['_mark3_last_scared_dist'] = None
        pacman_reactive_agent_no_random_mark1(game_state)
        return

    # Keep the immediate local threat checks from Mark1 as the top priority.
    ghost_seen = {
        'up': pacman_perceptions.ghost_up(game_state, 2),
        'down': pacman_perceptions.ghost_down(game_state, 2),
        'left': pacman_perceptions.ghost_left(game_state, 2),
        'right': pacman_perceptions.ghost_right(game_state, 2),
    }
    if any(ghost_seen.values()):
        pacman_reactive_agent_no_random_mark1(game_state)
        return

    nearest_scared_dist = min(
        game_engine.maze_distance(current_pos, (g['x'], g['y']), grid, grid_size)
        for g in scared_ghosts
    )

    # Stall breaker with tolerance: only break chase after several non-improving steps.
    stall_limit = 3
    last_scared_dist = pacman.setdefault('_mark3_last_scared_dist', None)
    stall_steps = pacman.setdefault('_mark3_stall_steps', 0)
    if last_scared_dist is not None and nearest_scared_dist >= last_scared_dist:
        stall_steps += 1
    else:
        stall_steps = 0
    pacman['_mark3_stall_steps'] = stall_steps
    pacman['_mark3_last_scared_dist'] = nearest_scared_dist

    if stall_steps >= stall_limit:
        pacman['_mark3_stall_steps'] = 0
        pacman['_mark3_last_scared_dist'] = None
        pacman_reactive_agent_no_random_mark1(game_state)
        return

    # Only switch to chase mode when a scared ghost is reasonably close.
    if nearest_scared_dist > 6:
        pacman_reactive_agent_no_random_mark1(game_state)
        return

    candidates = []
    for d in legal_dirs:
        nxt = game_engine.compute_new_pos(current_pos, d)

        # Avoid moves that would put us in the same cell as an active ghost.
        if any((g['x'], g['y']) == nxt for g in active_ghosts):
            continue

        # Also avoid moves that would put us within a certain distance of active ghosts, even if not in the same cell, to reduce risk while chasing.
        min_active_dist = float('inf')
        if active_ghosts:
            min_active_dist = min(
                game_engine.maze_distance(nxt, (g['x'], g['y']), grid, grid_size)
                for g in active_ghosts
            )
            if min_active_dist < 2:
                continue

        # Consider mobility as a tie-breaker to prefer paths with more escape routes, which can help avoid getting trapped by active ghosts while chasing scared ones.
        mobility = len(game_engine.get_valid_directions(nxt, grid, grid_size))
        if active_ghosts and mobility <= 1:
            continue

        # Finally, consider distance to scared ghosts to prioritize chasing the closest one.
        min_scared_dist = min(
            game_engine.maze_distance(nxt, (g['x'], g['y']), grid, grid_size)
            for g in scared_ghosts
        )

        # Sort key: closer scared ghost first, then higher mobility, then farther from danger.
        # choose the move that gets closest to a scared ghost, while also preferring more open positions and safer positions away from active ghosts.
        candidates.append((min_scared_dist, -mobility, -min_active_dist, d))

    if not candidates:
        pacman_reactive_agent_no_random_mark1(game_state)
        return

    _, _, _, best_dir = min(candidates)
    dir_to_action[best_dir](game_state)

def blinky_agent(ghost, game_state):
    #moves towards pacman
    pacman = game_state['pacman']
    grid = game_state['grid']
    grid_size = game_state['grid_size']


    directions = game_engine.get_valid_directions((ghost['x'],ghost['y']), grid, grid_size)    
    op = game_engine.opposite_direction(ghost['direction'])
    if len(directions)>1 and op in directions:    
        directions.remove(op)
    
    curr_pos = (ghost['x'],ghost['y'])
    best_pos = game_engine.compute_new_pos(curr_pos, directions[0])
    best_dist = game_engine.manhattan_distance(best_pos, (pacman['x'],pacman['y']))
    best_dir = directions[0]
    
    for dir in directions:
        cand_pos = game_engine.compute_new_pos(curr_pos, dir)
        cand_dist = game_engine.manhattan_distance(cand_pos, (pacman['x'],pacman['y']))
        
        if cand_dist < best_dist:
            best_dist = cand_dist
            best_pos = cand_pos
            best_dir = dir
    ghost['direction'] = best_dir
    
    
def pinky_agent(ghost, game_state):
    #moves to 4 cells in front of pacman
    pacman = game_state['pacman']
    grid = game_state['grid']
    grid_size = game_state['grid_size']

    target_pos = game_engine.compute_new_pos((pacman['x'],pacman['y']), pacman['direction'], 4)

    directions = game_engine.get_valid_directions((ghost['x'],ghost['y']), grid, grid_size)    
    op = game_engine.opposite_direction(ghost['direction'])
    if len(directions)>1 and op in directions:    
        directions.remove(op)
    
    curr_pos = (ghost['x'],ghost['y'])
    best_pos = game_engine.compute_new_pos(curr_pos, directions[0])
    best_dist = game_engine.manhattan_distance(best_pos, target_pos)
    best_dir = directions[0]
    
    for dir in directions:
        cand_pos = game_engine.compute_new_pos(curr_pos, dir)
        cand_dist = game_engine.manhattan_distance(cand_pos, target_pos)
        
        if cand_dist < best_dist:
            best_dist = cand_dist
            best_pos = cand_pos
            best_dir = dir
    ghost['direction'] = best_dir

    
def inky_agent(ghost, game_state):
    random_walk(ghost, game_state)
    
def clyde_agent(ghost, game_state):
    #moves towards pacman if far, otherwise moves randomly
    pacman = game_state['pacman']
    dist = game_engine.manhattan_distance((ghost['x'],ghost['y']), (pacman['x'],pacman['y']))
    if dist > 5:
        blinky_agent(ghost, game_state)
    else:
        random_walk(ghost, game_state)
    


def run_away_from_pacman(ghost, game_state):
    pacman = game_state['pacman']
    grid = game_state['grid']
    grid_size = game_state['grid_size']


    directions = game_engine.get_valid_directions((ghost['x'],ghost['y']), grid, grid_size)    
    op = game_engine.opposite_direction(ghost['direction'])
    if len(directions)>1 and op in directions:    
        directions.remove(op)
        
    curr_pos = (ghost['x'],ghost['y'])
    best_pos = game_engine.compute_new_pos(curr_pos, directions[0])
    best_dist = game_engine.manhattan_distance(best_pos, (pacman['x'],pacman['y']))
    best_dir = directions[0]
    
    for dir in directions:
        cand_pos = game_engine.compute_new_pos(curr_pos, dir)
        cand_dist = game_engine.manhattan_distance(cand_pos, (pacman['x'],pacman['y']))
        
        if cand_dist > best_dist:
            best_dist = cand_dist
            best_pos = cand_pos
            best_dir = dir
    ghost['direction'] = best_dir
    
    


def get_neighbours(s, valid_positions):
    valid_neighbours = []
    xs, ys = valid_positions[s]
    for x in (xs-1, xs, xs+1):
        for y in (ys-1, ys, ys+1):
            if (x, y) in valid_positions:
                valid_neighbours.append(valid_positions.index((x,y)))
    return valid_neighbours
            

    
    
