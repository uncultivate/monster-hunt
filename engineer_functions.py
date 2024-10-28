import random
from typing import Tuple, List, Dict, Optional

Position = Tuple[int, int]
Direction = Optional[str]

def rapid_ryan(self_pos: Position, beast_pos: List[Position], other_engineers: List[Position], grid_size: Tuple[int, int]) -> Direction:
    MOVE_OPTIONS = {
        (0, 0): None,
        (0, -1): "up",
        (0, 1): "down",
        (-1, 0): "left",
        (1, 0): "right"
    }

    def is_valid_position(pos: Position) -> bool:
        x, y = pos
        grid_width, grid_height = grid_size
        return 0 <= x < grid_width and 0 <= y < grid_height

    add_pos = lambda p1, p2: tuple(map(sum, zip(p1, p2)))
    get_distance = lambda p1, p2: sum(map(lambda x, y: abs(x-y), p1, p2))

    possible_destinations = {add_pos(self_pos, move_option): move_option for move_option in MOVE_OPTIONS if is_valid_position(add_pos(self_pos, move_option))}
    big_beast_pos, *zombie_pos = beast_pos

    possible_destinations_not_on_beasts = [dest for dest in possible_destinations.keys() if not any([dest == b_pos for b_pos in beast_pos])]

    possible_destinations_not_next_to_zombies = [dest for dest in possible_destinations_not_on_beasts if not any([get_distance(dest, z_pos) <= 1 for z_pos in zombie_pos])]
    # all possible dests not on zombies/beast are next to zombies -> hence allow moves next to zombies
    if not possible_destinations_not_next_to_zombies:
        possible_destinations_not_next_to_zombies = possible_destinations_not_on_beasts
    
    # all possible dests are on zombies/beasts -> give up
    if not possible_destinations_not_next_to_zombies:
        return None

    furtherest_dest = max(possible_destinations_not_next_to_zombies, key=lambda dest_pos: get_distance(dest_pos, big_beast_pos))
    return MOVE_OPTIONS[possible_destinations[furtherest_dest]]

def saboteur(self_pos: Position, beast_positions: List[Position], other_engineers: List[Position], grid_size: Tuple[int, int]) -> Direction:
    import numpy as np

    beast_vector = [self_pos[0] - sum([pos[0] for pos in beast_positions]), self_pos[1] - sum([pos[1] for pos in beast_positions])] 
    beast_dist =  np.linalg.norm(beast_vector)
    beast_vector = beast_vector / beast_dist
    
    eng_vector = [self_pos[0] - sum([pos[0] for pos in other_engineers]), self_pos[1] - sum([pos[1] for pos in other_engineers])] 
    eng_dist =  np.linalg.norm(eng_vector)
    eng_vector = eng_vector / eng_dist

    threshold = 4
    
    direction = None
    if (beast_dist <= threshold) & (len(other_engineers) == 0):  # If the beast is close and no one else is around
        ### Run away from the beast ###
        vector = beast_vector
        if (self_pos[0] == 0) | (self_pos[0] == grid_size[0]-1):
            vector[0] = 0
        if (self_pos[1] == 0) | (self_pos[1] == grid_size[1]-1):
            vector[1] = 0  
    elif (beast_dist <= threshold) & (len(other_engineers) != 0): # If the beast is close and there are others around
        ### Run towards the other engineers ###
        vector = eng_vector * -1
    elif beast_dist > threshold: # If outside of the range of the beast
        ### Run towards the beast ###
        vector = beast_vector * -1
    
    if abs(vector[0]) > abs(vector[1]): # Move L/R
        if vector[0] < 0:
            direction = 'left'
        elif vector[0] > 0:
            direction = 'right'
    elif abs(vector[0]) < abs(vector[1]): # Move U/D
        if vector[1] < 0:
            direction = 'up'
        elif vector[1] > 0:
            direction = 'down'
    elif abs(vector[0]) == abs(vector[1]): # Pick randomly
        if (vector[0] > 0) & (vector[1] > 0):
            direction = random.choice(['right', 'down'])
        elif (vector[0] > 0) & (vector[1] < 0):
            direction = random.choice([ 'right', 'up'])
        elif (vector[0] < 0) & (vector[1] > 0):
            direction = random.choice(['left', 'down'])
        elif (vector[0] < 0) & (vector[1] < 0):
            direction = random.choice(['left', 'up'])
      
    return direction


def randomy_savage(self_pos: Position, beast_pos: List[Position], other_engineers: List[Dict], grid_size: Tuple[int, int]) -> Direction:
    direction = random.choice(['up', 'down', 'left', 'right'])
    return direction

def mr_sinister(self_pos: Position, beast_pos: List[Position], other_engineers: List[Dict], grid_size: Tuple[int, int]) -> Direction | None:
    BEAST_DETECTION_RANGE = 5
    SAFE_DISTANCE = 5

    def distance(pos1: Position, pos2: Position) -> float:
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

    def is_valid_move(pos: Position) -> bool:
        return 0 <= pos[0] < grid_size[0] and 0 <= pos[1] < grid_size[1]

    moves = [
        ('up', (self_pos[0], self_pos[1] - 1)),
        ('right', (self_pos[0] + 1, self_pos[1])),
        ('down', (self_pos[0], self_pos[1] + 1)),
        ('left', (self_pos[0] - 1, self_pos[1])),
        (None, self_pos)  # Option to stay in place
    ]

    valid_moves = [(direction, pos) for direction, pos in moves if is_valid_move(pos)]

    if not valid_moves:
        return None  # This should never happen as staying in place is always valid

    if len(beast_pos) == 0:
        return 'down'  # Default movement when no beast is present

    closest_beast = min(beast_pos, key=lambda beast: distance(self_pos, beast))
    distance_to_beast = distance(self_pos, closest_beast)

    # Phase 1: Move within detection range of the beast
    if distance_to_beast > BEAST_DETECTION_RANGE:
        best_move = min(valid_moves, key=lambda move: abs(distance(move[1], closest_beast) - BEAST_DETECTION_RANGE))
        return best_move[0]

    # Phase 2: Move towards another engineer while maintaining safe distance from beast
    if other_engineers:
        nearest_engineer = min(other_engineers, key=lambda eng: distance(self_pos, eng))
        
        def score_move(move):
            dist_to_engineer = distance(move[1], nearest_engineer)
            dist_to_beast = distance(move[1], closest_beast)
            safety_score = abs(dist_to_beast - SAFE_DISTANCE)
            return dist_to_engineer + safety_score * 2  # Prioritize safety

        best_move = min(valid_moves, key=lambda move: score_move(move))
        
        if distance(best_move[1], closest_beast) >= SAFE_DISTANCE:
            return best_move[0]
    
    # If no suitable move is found, try to maintain safe distance from beast
    safe_moves = [move for move in valid_moves if distance(move[1], closest_beast) >= SAFE_DISTANCE]
    if safe_moves:
        return random.choice(safe_moves)[0]
    
    # If no safe move is available, choose the move that maximizes distance from beast
    return max(valid_moves, key=lambda move: distance(move[1], closest_beast))[0]
    

def mui_shaggy(self_pos: Position, beast_pos: List[Position], other_engineers: List[Position], grid_size: Tuple[int, int]) -> Direction:

  def distance(pos1, pos2):
    return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5

  left_pos = (self_pos[0] - 1, self_pos[1])
  right_pos = (self_pos[0] + 1, self_pos[1])
  up_pos = (self_pos[0], self_pos[1] - 1)
  down_pos = (self_pos[0], self_pos[1] + 1)

  left_space = self_pos[0]
  right_space = 9 - self_pos[0]
  up_space = self_pos[1]
  down_space = 9 - self_pos[1]

  left_zombie = 9
  right_zombie = 9
  up_zombie = 9
  down_zombie = 9
  
  for z in range(len(beast_pos)):
    if z > 0:
      zombie_pos = beast_pos[z]
      left_zombie = min(left_zombie,distance(left_pos,zombie_pos))
      right_zombie = min(right_zombie,distance(right_pos,zombie_pos))
      up_zombie = min(up_zombie,distance(up_pos,zombie_pos))
      down_zombie = min(down_zombie,distance(down_pos,zombie_pos))

  beast_location = beast_pos[0]

  if left_space == 0 or left_zombie <= 1:
    left_len = 0
  else:
    left_len = distance(left_pos,beast_location)

  if right_space == 0 or right_zombie <= 1:
    right_len = 0
  else:
    right_len = distance(right_pos,beast_location)

  if up_space == 0 or up_zombie <=1:
    up_len = 0
  else:
    up_len = distance(up_pos,beast_location)

  if down_space == 0 or down_zombie <=1:
    down_len = 0
  else:
    down_len = distance(down_pos,beast_location)

  if left_len > right_len:
    x_len = left_len
    x_dir = "left"
    x_space = left_space
  
  elif left_len < right_len:
    x_len = right_len
    x_dir = "right"
    x_space = right_space
  
  else:
    if left_space > right_space:
      x_len = left_len
      x_dir = "left"
      x_space = left_space
    else:
      x_len = right_len
      x_dir = "right"
      x_space = right_space

  if up_len > down_len:
    y_len = up_len
    y_dir = "up"
    y_space = up_space

  elif up_len < down_len:
    y_len = down_len
    y_dir = "down"
    y_space = down_space
    
  else:
    if up_space > down_space:
      y_len = up_len
      y_dir = "up"
      y_space = up_space

    else:
      y_len = down_len
      y_dir = "down"
      y_space = down_space

  if x_len <= 1 and y_len <= 1:
    print("Zoinks! I should have learned, like, Instant Transmission instead, man!")
    return x_dir

  elif x_len > y_len:
    return x_dir
  
  elif x_len < y_len:
    return y_dir
  
  else:
    if x_space > y_space:
      return x_dir
    else:
      return y_dir


def leeroy(self_pos: Position, beast_pos: List[Position], other_engineers: List[Dict], grid_size: Tuple[int, int], turn_index: int) -> Direction | None:
    if len(beast_pos) == 0:
        return 'right'
    
    def distance(pos1: Position, pos2: Position) -> float:
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

    def is_valid_move(pos: Position) -> bool:
        return 0 <= pos[0] < grid_size[0] and 0 <= pos[1] < grid_size[1]

    moves = [
        ('up', (self_pos[0], self_pos[1] - 1)),
        ('right', (self_pos[0] + 1, self_pos[1])),
        ('down', (self_pos[0], self_pos[1] + 1)),
        ('left', (self_pos[0] - 1, self_pos[1])),
        (None, self_pos)  # Option to stay in place
    ]

    valid_moves = [(direction, pos) for direction, pos in moves if is_valid_move(pos)]

    if not valid_moves:
        return None  # This should never happen as staying in place is always valid

    # Find the beast closest to Alice
    closest_beast = min(beast_pos, key=lambda beast: distance(self_pos, beast))

    # Run towards the beast crazily if turns > 10
    if turn_index < 10:
        best_move = max(valid_moves, key=lambda move: distance(move[1], closest_beast))
    else:
        best_move = min(valid_moves, key=lambda move: distance(move[1], closest_beast))
      

    return best_move[0]

def leprechaun(self_pos: Position, beast_pos: List[Position], other_engineers: List[Position], grid_size: Tuple[int, int]) -> Direction:
    
    top_left_corner = (0,0)
    top_right_corner = (grid_size[0]-1, 0)
    bottom_left_corner = (0, grid_size[1]-1)
    bottom_right_corner = (grid_size[0]-1, grid_size[1]-1)
    
    K = 1
    nearest_beast = min(beast_pos, key=lambda x: abs(x[K-1] - self_pos[K-1]))
    
    dx = self_pos[0] - nearest_beast[0]
    dy = self_pos[1] - nearest_beast[1]
    
    if ((self_pos[0] - nearest_beast[0])**2 + (self_pos[1] - nearest_beast[1])**2)**0.5 <= 5: #beast has detected engineer
        if self_pos == top_left_corner:
            if abs(dx) > abs(dy):
                return "down"
            else:
                return "right"
        elif self_pos == top_right_corner:
            if abs(dx) > abs(dy):
                return "down"
            else:
                return "left"
        elif self_pos == bottom_left_corner:
            if abs(dx) > abs(dy):
                return "up"
            else:
                return "right"
        elif self_pos == bottom_right_corner:
            if abs(dx) > abs(dy):
                return "up"
            else:
                return "left"
        elif self_pos[0] < grid_size[0] -1 and self_pos[1] == 0: #engineer on top wall
            if nearest_beast[0] < self_pos[0]:  #beast on left side of engineer
                return "right"
            else:                               #beast on right side of engineer
                return "left"
        elif self_pos[0] == grid_size[0] -1 and self_pos[1] < grid_size[1]-1:   #engineer on right wall
            if nearest_beast[1] < self_pos[1]:  #beast above engineer
                return "down"
            else:
                return "up"            #beast below engineer
        elif self_pos[0] > 0 and self_pos[1] == grid_size[1]-1: #engineer on bottom wall
            if nearest_beast[0] < self_pos[0]:  #beast on left side of engineer
                return "right"
            else:
                return "left"          #beast on right side of engineer
        elif self_pos[0] == 0 and self_pos[1] > 0:  #engineer on right wall
            if nearest_beast[1] < self_pos[1]:  #beast above engineer
                return "down"
            else:                               #beast below engineer
                return "up"
        elif abs(dx) > abs(dy):                 #beast has more horizontal distance difference than vertical
            if dy > 0:                          #beast is above engineer
                return "down"
            else:                               #beast is below engineer
                return "up"
        elif abs(dy) >= abs(dx):                #beast has more vertical distance difference than horizontal
            if dx > 0:                          #beast is left of engineer
                return "right"
            else:
                return "left"           #beast is right of engineer
    elif self_pos[0] < grid_size[0] -1 and self_pos[1] == 0:
        if dx > 0:
            return "right"
        else:
            return "left"
    elif self_pos[0] == grid_size[0] -1 and self_pos[1] < grid_size[1]-1:
        if dy > 0:
            return "down"
        else:
            return "up"
    elif self_pos[0] > 0 and self_pos[1] == grid_size[1]-1:
        if dx > 0:
            return "right"
        else:
            return "left"
    elif self_pos[0] == 0 and self_pos[1] > 0:
        if dy > 0:
            return "down"
        else:
            return "up"
    elif abs(dx) > abs(dy):
        if dy > 0:
            return "down"
        else:
            return "up"
    elif abs(dy) >= abs(dx):
        if dx > 0:
            return "right"
        else:
            return "left"
        
def brave_sir_robin(self_pos, beast_positions, other_engineers, grid_size):
    import math
    """""
    Brave Sir Robin ran away.
    Bravely ran away away.
    When danger reared it's ugly head,
    He bravely turned his tail and fled.
    Yes, brave Sir Robin turned about
    And gallantly he chickened out.
    Swiftly taking to his feet,
    He beat a very brave retreat.
    Bravest of the brave, Sir Robin!

    -Jacob
    """""
    def distance(pos1, pos2):
        """""Returns the distance between two positions."""""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def valid_move(new_pos):
        """Checks if the new position is within the grid boundaries."""
        return 0 <= new_pos[0] < grid_size[0] and 0 <= new_pos[1] < grid_size[1]

    def total_distance_from_beasts(pos, beasts):
        """"Calculates the sum of distances to all beasts from a given position."""
        return sum(distance(pos, beast) for beast in beasts)

    def nearest_entity(pos, entities):
        """"Finds the nearest entity (either beast or engineer) to a given position."""
        return min(entities, key=lambda entity_pos: distance(pos, entity_pos))

    # Define possible moves and their corresponding coordinate changes
    moves = {
        "up": (0, -1),
        "down": (0, 1),
        "left": (-1, 0),
        "right": (1, 0)
    }

    # If there are no other engineers, we are the last one alive
    if not other_engineers:
        # Focus purely on maximizing the distance from all beasts
        max_total_distance_from_beasts = -1
        best_move = None
        for direction, (dx, dy) in moves.items():
            new_pos = (self_pos[0] + dx, self_pos[1] + dy)
            if valid_move(new_pos):
                new_total_distance_from_beasts = total_distance_from_beasts(new_pos, beast_positions)
                if new_total_distance_from_beasts > max_total_distance_from_beasts:
                    max_total_distance_from_beasts = new_total_distance_from_beasts
                    best_move = direction
        return best_move if best_move else None

    # Normal behavior when there are other engineers around
    closest_beast = nearest_entity(self_pos, beast_positions)
    my_distance_to_closest_beast = distance(self_pos, closest_beast)

    # Determine if any engineer is closer to any beast than I am
    engineers_closer_to_any_beast = [
        eng for eng in other_engineers if any(distance(eng, beast) < distance(self_pos, beast) for beast in beast_positions)
    ]

    # Find the closest engineer to me
    closest_engineer = nearest_entity(self_pos, other_engineers)
    my_distance_to_closest_engineer = distance(self_pos, closest_engineer)

    max_total_distance_from_beasts = -1
    best_move = None

    # Iterate through all possible moves to evaluate the best direction
    for direction, (dx, dy) in moves.items():
        new_pos = (self_pos[0] + dx, self_pos[1] + dy)

        if valid_move(new_pos):
            # Calculate the total distance from all beasts at the new position
            new_total_distance_from_beasts = total_distance_from_beasts(new_pos, beast_positions)

            # Calculate the new distance to the closest engineer if I move
            new_distance_to_engineer = distance(new_pos, closest_engineer) if closest_engineer else float('inf')

            # If I am the closest to all beasts, move toward the nearest engineer for safety
            if not engineers_closer_to_any_beast:
                if new_distance_to_engineer < my_distance_to_closest_engineer:
                    best_move = direction
            else:
                # If other engineers are closer to any beast, maximize the total distance from all beasts
                if new_total_distance_from_beasts > max_total_distance_from_beasts:
                    max_total_distance_from_beasts = new_total_distance_from_beasts
                    best_move = direction

    return best_move if best_move else None


def edgy_engineer(self_pos: Position, beast_pos: List[Position], other_engineers: List[Position], grid_size: Tuple[int, int]) -> Direction:
    max_x = grid_size[0] - 1
    max_y = grid_size[1] - 1

    curr_x = self_pos[0]
    curr_y = self_pos[1]

    # If not at any border, go down to the bottom border
    if curr_x != 0 and curr_x != max_x and curr_y != 0 and curr_y != max_y: return "down"

    # If at the bottom border, but not on the right border, go right
    elif curr_y == max_y and curr_x != max_x: return "right"

    # If on the right border, but not at the top, go up
    elif curr_x == max_x and curr_y != 0: return "up"

    # If on the top border, but not at the left border, go left
    elif curr_y == 0 and curr_x != 0: return "left"

    # If on the left border, but not at the bottom border, go down
    elif curr_x == 0 and curr_y != max_y: return "down"

def aaahhhhh(self_pos, beast_positions, other_engineers, grid_size, time):

    # Helper function to check if a move is valid
    def is_valid_move(pos: Position, grid_size: Tuple[int, int]) -> bool:
        x, y = pos
        width, height = grid_size
        return 0 <= x < width and 0 <= y < height

    # Define possible new positions for each direction
    directions = {
        'left': (self_pos[0] - 1, self_pos[1]),
        'right': (self_pos[0] + 1, self_pos[1]),
        'up': (self_pos[0], self_pos[1] - 1),
        'down': (self_pos[0], self_pos[1] + 1)
    }

    # Count engineers in each direction (based on x and y coordinates)
    engineers_left = sum(1 for engineer in other_engineers if self_pos[0] > engineer[0])
    engineers_right = sum(1 for engineer in other_engineers if self_pos[0] < engineer[0])
    engineers_above = sum(1 for engineer in other_engineers if self_pos[1] > engineer[1])
    engineers_below = sum(1 for engineer in other_engineers if self_pos[1] < engineer[1])

    # Initialize direction choice
    direction = None

    # Check even or odd time step
    if time % 2 == 0:  # On even turns, choose between left and right
        if engineers_left > engineers_right:
            direction = 'right'
        elif engineers_left < engineers_right:
            direction = 'left'
        else:
            direction = random.choice(['left', 'right'])
    else:  # On odd turns, choose between up and down
        if engineers_above > engineers_below:
            direction = 'down'
        elif engineers_above < engineers_below:
            direction = 'up'
        else:
            direction = random.choice(['up', 'down'])

    # Get the new position based on the chosen direction
    new_pos = directions[direction]

    # is the move is valid; if not, try to pick another valid direction
    if not is_valid_move(new_pos, grid_size):
        for alt_dir in directions.keys():
            alt_pos = directions[alt_dir]
            if is_valid_move(alt_pos, grid_size):
                return alt_dir  # Return the first valid alternative direction
    
    return direction if is_valid_move(new_pos, grid_size) else None