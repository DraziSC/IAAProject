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
        op = game_engine.opposite_direction(pacman['direction'])
        if len(food_legal_dirs) > 1 and op in food_legal_dirs:
            food_legal_dirs.remove(op)

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
        
        for d in food_legal_dirs:
            cand_pos = game_engine.compute_new_pos(current_pos, d)
            cand_dist = game_engine.manhattan_distance(cand_pos, nearest_food)
            if cand_dist < best_dist:
                best_dist = cand_dist
                best_pos = cand_pos
                best_dir = d
        dir_to_action[best_dir](game_state)
        
def pacman_reactive_agent_random(game_state):
    ##TODO: Implement the reactive agent
  
    random.choice([up, down, left, right])(game_state)

def pacman_risk_aware_agent(game_state):
    """
    Risk-aware policy for Pacman.
    Scores each legal move using immediate ghost danger, predicted ghost movement,
    local mobility (escape routes), food reward, and scared-ghost opportunities.
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
                gdirs.remove(opp)

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
            

    
    
