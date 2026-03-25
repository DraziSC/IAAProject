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
def pacman_reactive_agent(game_state):
    ##TODO: Implement the reactive agent
    random.choice([up, down, left, right])(game_state)

    
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
            

    
    
