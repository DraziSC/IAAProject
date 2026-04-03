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
def free_directions(game_state):
    #returns the directions that pacman can move to that does not have a ghost
    directions = []
    if not pacman_perceptions.ghost_up(game_state):
        directions.append(up)
    if not pacman_perceptions.ghost_down(game_state):
        directions.append(down)
    if not pacman_perceptions.ghost_left(game_state):
        directions.append(left)
    if not pacman_perceptions.ghost_right(game_state):
        directions.append(right)
    return directions

def checkforWalls(game_state,directions):
    for direction in directions:
        if direction == up:
            if pacman_perceptions.wall_up(game_state):
                directions.remove(up)
        elif direction == down:
            if pacman_perceptions.wall_down(game_state):
                directions.remove(down)
        elif direction == left:
            if pacman_perceptions.wall_left(game_state):
                directions.remove(left)
        elif direction == right:
            if pacman_perceptions.wall_right(game_state):
                directions.remove(right)
    return directions


def pacman_reactive_agent(game_state):
    # if there is  ghost in the up direction, move down, if there is a ghost in the down direction, move up, 
    # if there is a ghost in the left directi
    
    
    directions = checkforWalls(game_state, free_directions(game_state))
    if len(directions) == 0:
        random.choice([up, down, left, right])(game_state)
        return
       
    direction = random.choice(directions)(game_state)

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
    #     
    # First attempt simple rules
    # Rule 1 : If ghost above, move down. If ghost below, move up. If ghost left, move right. If ghost right, move left.
    # Rule 2 : If no ghosts around, move towards the closest food

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

def pacman_reactive_agent_no_random_mark1(game_state):
    # same as no random but better checking for multiple ghosts in multiple directions. 
    # If there are ghosts in multiple directions, move in the direction with the most free spaces and no ghosts. 
    # This is a simple way to try to avoid getting trapped by multiple ghosts.
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

def pacman_reactive_agent_no_random_mark_defunct(game_state):
    # Similar to pacman_reactive_agent_no_random but with a more sophisticated Ghost chasing strategy that considers mobility and 
    # dead ends and avoids local loops.

    pacman = game_state['pacman']
    grid = game_state['grid']
    grid_size = game_state['grid_size']

    current_pos = (pacman['x'], pacman['y'])
    legal_dirs = game_engine.get_valid_directions(current_pos, grid, grid_size)

    # Short position memory to discourage local loops.
    recent_positions = pacman.setdefault('_mark2_recent_positions', [])
    recent_positions.append(current_pos)
    if len(recent_positions) > 10:
        recent_positions.pop(0)

    # Progress watchdog: count consecutive steps without score increase.
    current_score = game_state.get('score', 0)
    last_score = pacman.setdefault('_mark2_last_score', current_score)
    stall_steps = pacman.setdefault('_mark2_stall_steps', 0)
    if current_score > last_score:
        stall_steps = 0
    else:
        stall_steps += 1
    pacman['_mark2_last_score'] = current_score
    pacman['_mark2_stall_steps'] = stall_steps

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
        # Stall breaker: if we have not improved score for a while, pick least-visited move.
        if stall_steps >= 18 and len(legal_dirs) > 1:
            alive_ghost_positions = {
                (g['x'], g['y']) for g in game_state['ghosts'] if g['alive'] and not g['scared']
            }

            safe_dirs = [
                d for d in legal_dirs
                if game_engine.compute_new_pos(current_pos, d) not in alive_ghost_positions
            ]
            breaker_dirs = safe_dirs if safe_dirs else legal_dirs

            # Prefer moves to less-visited positions; break ties by mobility.
            min_revisit = min(
                recent_positions.count(game_engine.compute_new_pos(current_pos, d))
                for d in breaker_dirs
            )
            least_visited_dirs = [
                d for d in breaker_dirs
                if recent_positions.count(game_engine.compute_new_pos(current_pos, d)) == min_revisit
            ]

            best_mobility = max(
                len(game_engine.get_valid_directions(game_engine.compute_new_pos(current_pos, d), grid, grid_size))
                for d in least_visited_dirs
            )
            candidates = [
                d for d in least_visited_dirs
                if len(game_engine.get_valid_directions(game_engine.compute_new_pos(current_pos, d), grid, grid_size)) == best_mobility
            ]

            dir_to_action[random.choice(candidates)](game_state)
            return

        # No immediate ghost threat, move towards closest food while considering mobility and dead ends.
        food_legal_dirs = legal_dirs.copy()
        op = game_engine.opposite_direction(pacman['direction'])

        # Prevent reversing direction unless it's the only option to encourage exploration and reduce oscillation.
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
      
        nearest_food = min(food_positions, key=lambda fp: game_engine.manhattan_distance(current_pos, fp))
        best_dir = food_legal_dirs[0]
        # Evaluate candidate moves based on distance to food and mobility (number of escape routes) to avoid dead ends and local loops.
        # start with the first legal direction as the best and then compare with others. This ensures we always have a valid move.
        best_pos = game_engine.compute_new_pos(current_pos, best_dir)
        # Distance to food.
        best_dist = game_engine.manhattan_distance(best_pos, nearest_food)  
        # Mobility (number of valid moves from the new position) as a tie-breaker to prefer paths with more escape routes 
        # when distances are equal, which can help avoid dead ends and local loops.
        best_mobility = len(game_engine.get_valid_directions(best_pos, grid, grid_size))   

        # Tie-break by mobility to prefer paths with more escape routes when distances are equal, which can help avoid dead ends and local loops.
        for d in food_legal_dirs:
            cand_pos = game_engine.compute_new_pos(current_pos, d)
            cand_dist = game_engine.manhattan_distance(cand_pos, nearest_food)
            cand_mobility = len(game_engine.get_valid_directions(cand_pos, grid, grid_size))

            # Prefer less recently visited positions when distance/mobility are close.
            best_revisit = recent_positions.count(best_pos)
            cand_revisit = recent_positions.count(cand_pos)

            if (
                (cand_dist < best_dist) or
                (cand_dist == best_dist and cand_mobility > best_mobility) or
                (cand_dist == best_dist and cand_mobility == best_mobility and cand_revisit < best_revisit)
            ):
                best_dist = cand_dist
                best_pos = cand_pos
                best_dir = d
                best_mobility = cand_mobility

        dir_to_action[best_dir](game_state)


def pacman_reactive_agent_random(game_state):
    ##TODO: Implement the reactive agent
  
    random.choice([up, down, left, right])(game_state)

def pacman_risk_aware_agent(game_state):
    """
    Risk-aware policy for Pacman.
    Scores each legal move using immediate ghost danger, predicted ghost movement,
    local mobility (escape routes), food reward, and scared-ghost opportunities.
    Uses memory of recent positions to discourage local loops and a stall counter to encourage exploration if stuck.
    Uses a weighted scoring system to balance safety and progress toward winning.

    Current weights and what they do (very risk averse):

        Immediate collision with active ghost: -10000
        Predicted deterministic ghost next tile: -300
        Predicted random ghost next tile: -120
        Distance from nearest active ghost: +8 × min_dist
        Scared-ghost chase term: +35 - 7 × min_scared_dist
        Landing directly on scared ghost: +500
        Dot reward: +25
        Power pellet reward: +90
        Global food attraction: +40 - 2 × nearest_food_dist
        Mobility reward: +6 × number_of_future_dirs
        Dead-end penalty under nearby threat: -200
        Reverse-direction penalty: -10
        Recent-position revisit penalty: -18 × revisit_count

    Use this moderate riskier preset first:

        Keep death collision at -10000
        Deterministic next-tile risk: -180
        Random next-tile risk: -70
        Active-ghost distance bonus: +4
        Scared chase: +55 - 10d
        Eat scared ghost bonus: +700
        Dot: +35
        Pellet: +130
        Food pull: +55 - 1d
        Mobility: +3
        Dead-end under threat: -90
        Reverse: -5
        Revisit: -8

    Aggressive riskier preset:

        Keep death collision at -10000
        Deterministic next-tile risk: -120
        Random next-tile risk: -40
        Active-ghost distance bonus: +2
        Scared chase: +80 - 12d
        Eat scared ghost bonus: +1000
        Dot: +40
        Pellet: +180
        Food pull: +70 - 1d
        Mobility: +2
        Dead-end under threat: -40
        Reverse: -2
        Revisit: -4

    Production rules for Risk-Aware policy:
    ID      Priority  Condition (informal)                                      Action (informal)
    R1      1         Candidate move lands on active ghost                      Apply very large penalty (effectively reject)
    R2      2         Candidate move is in likely next ghost positions           Apply strong risk penalties
    R3      3         Active ghosts exist                                        Prefer moves with larger distance to nearest active ghost
    R4      4         Scared ghosts exist                                        Prefer moves that reduce distance to scared ghosts; bonus if edible now
    R5      5         Candidate cell has food or power pellet                    Add immediate reward for collecting it
    R6      6         Food remains on board                                      Prefer moves that reduce distance to nearest remaining food
    R7      7         Candidate has higher future mobility                       Prefer more escape routes; penalize dead-end under threat
    R8      8         Candidate reverses current direction                       Apply small anti-oscillation penalty
    R9      9         Candidate revisits recent positions                        Apply revisit penalty to break local loops
    R10     10        After all rule scores are combined                         Choose legal move with maximum total score
    """
    pacman = game_state['pacman']
    grid = game_state['grid']
    grid_size = game_state['grid_size']

    current_pos = (pacman['x'], pacman['y'])
    legal_dirs = game_engine.get_valid_directions(current_pos, grid, grid_size)
    if not legal_dirs:
        return

    # Keep a short movement history to discourage local loops.
    recent_positions = pacman.setdefault('_recent_positions', [])
    recent_positions.append(current_pos)
    if len(recent_positions) > 12:
        recent_positions.pop(0)

    # Build a list of remaining food positions for global guidance.
    food_positions = []
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == game_engine.DOT or cell == game_engine.POWER_PELLET:
                food_positions.append((x, y))

    dir_to_action = {
        'up': up,
        'down': down,
        'left': left,
        'right': right,
    }

    alive_ghosts = [g for g in game_state['ghosts'] if g['alive'] and not g['scared']]
    scared_ghosts = [g for g in game_state['ghosts'] if g['alive'] and g['scared']]

    # Build likely ghost-next positions.
    deterministic_next = set()
    random_next = set()

    for ghost in alive_ghosts:
        gpos = (ghost['x'], ghost['y'])
        gdirs = game_engine.get_valid_directions(gpos, grid, grid_size)
        if not gdirs:
            continue

        # Mirror random_walk behavior: avoid reversing if there are alternatives.
        if ghost['direction'] is not None:
            opp = game_engine.opposite_direction(ghost['direction'])
            if len(gdirs) > 1 and opp in gdirs:
                gdirs.remove(opp) # S

        if ghost['name'] == 'Inky':
            for d in gdirs:
                random_next.add(game_engine.compute_new_pos(gpos, d))
        else:
            # Approximate deterministic ghosts by selecting chase move toward current Pacman.
            best = gdirs[0]
            best_pos = game_engine.compute_new_pos(gpos, best)
            best_dist = game_engine.manhattan_distance(best_pos, current_pos)
            for d in gdirs:
                cand = game_engine.compute_new_pos(gpos, d)
                cand_dist = game_engine.manhattan_distance(cand, current_pos)
                if cand_dist < best_dist:
                    best = d
                    best_pos = cand
                    best_dist = cand_dist
            deterministic_next.add(best_pos)

    best_dir = legal_dirs[0]
    best_score = -10**9

    for d in legal_dirs:
        nxt = game_engine.compute_new_pos(current_pos, d)

        score = 0

        # Immediate death risk.
        if any((g['x'], g['y']) == nxt for g in alive_ghosts):
            score -= 10000

        # Predicted ghost next-step risk.
        if nxt in deterministic_next:
            score -= 300
        if nxt in random_next:
            score -= 120

        # Keep distance from nearest active ghost.
        if alive_ghosts:
            min_dist = min(game_engine.manhattan_distance(nxt, (g['x'], g['y'])) for g in alive_ghosts)
            score += 8 * min_dist

        # Chase frightened ghosts to farm points when they are edible.
        if scared_ghosts:
            min_scared_dist = min(game_engine.manhattan_distance(nxt, (g['x'], g['y'])) for g in scared_ghosts)
            score += 35 - 7 * min_scared_dist
            if any((g['x'], g['y']) == nxt for g in scared_ghosts):
                score += 500

        # Reward food and power pellets.
        cell = grid[nxt[1]][nxt[0]]
        if cell == game_engine.DOT:
            score += 25
        elif cell == game_engine.POWER_PELLET:
            score += 90

        # Pull Pacman toward remaining food, even when nothing is nearby.
        if food_positions:
            nearest_food_dist = min(game_engine.manhattan_distance(nxt, fp) for fp in food_positions)
            score += 40 - 2 * nearest_food_dist

        # Prefer mobility and avoid dead ends under threat.
        future_dirs = game_engine.get_valid_directions(nxt, grid, grid_size)
        score += 6 * len(future_dirs)
        if len(future_dirs) <= 1 and alive_ghosts:
            min_dist = min(game_engine.manhattan_distance(nxt, (g['x'], g['y'])) for g in alive_ghosts)
            if min_dist <= 3:
                score -= 200

        # Small penalty for reversing direction to reduce oscillation.
        if pacman['direction'] is not None and d == game_engine.opposite_direction(pacman['direction']):
            score -= 10

        # Penalize revisiting very recent positions to escape corner/edge loops.
        score -= 18 * recent_positions.count(nxt)

        if score > best_score:
            best_score = score
            best_dir = d

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
            

    
    
