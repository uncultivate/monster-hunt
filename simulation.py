import random
from typing import List, Tuple, Dict
import math
from enum import Enum, auto
from dataclasses import dataclass, field
import time
import csv
import os
from outputs import save_results_to_csv
from engineer_functions import *

# Game constants
GRID_WIDTH, GRID_HEIGHT = 12, 10
NUM_ENGINEERS = 5
ENGINEER_EMOJIS = ['🥺', '😈', '🦾', '🦹‍♂️', '🎃', '🐔', '☘️', '🦤', '💃', '😨']
ENGINEER_NAMES = ['rapid ryan', 'Saboteur', 'Random Savage', 'Mr Sinister', 'mui_shaggy', 'Leeroy', 'Leprechaun', 'Brave Sir Robin', 'Edgy Engineer', 'Aaahhhhh']
ZOMBIE_EMOJI = '🧟'
BEAST_EMOJI = '🐺'
BEAST_DETECTION_RADIUS = 5
ZOMBIE_DETECTION_RADIUS = 5
BEAST_APPEARS = 4
BEAST_MOVEMENT = [6, 8, 10]
END_GAME_TURNS = 50
BEAST_BEAST_MODE = True

class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

class EntityType(Enum):
    BEAST = auto()
    ENGINEER = auto()
    ZOMBIE = auto()

class GamePhase(Enum):
    SETUP = auto()
    BEAST_HIDDEN = auto()
    BEAST_VISIBLE = auto()
    GAME_OVER = auto()

Position = Tuple[int, int]

@dataclass
class DetectedEngineer:
    name: str
    position: Position
    detected_turn: int

@dataclass
class Entity:
    position: Position
    emoji: str
    name: str
    entity_type: EntityType
    alive: bool = True
    last_moved: int = 0
    targeted_by: str = None
    ai_function: callable = None
    score: int = 0
    detected_engineers: List[DetectedEngineer] = field(default_factory=list)


@dataclass
class Grid:
    width: int
    height: int

    def is_valid_position(self, pos: Position) -> bool:
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def move(self, pos: Position, direction: Direction) -> Position:
        x, y = pos
        if direction == Direction.UP:
            new_pos = (x, y - 1)
        elif direction == Direction.DOWN:
            new_pos = (x, y + 1)
        elif direction == Direction.LEFT:
            new_pos = (x - 1, y)
        elif direction == Direction.RIGHT:
            new_pos = (x + 1, y)
        else:
            return pos # Default case if an invalid direction
        
        return new_pos if self.is_valid_position(new_pos) else pos

    @staticmethod
    def distance(pos1: Position, pos2: Position) -> float:
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    


class GameState:
    def __init__(self):
        self.grid = Grid(GRID_WIDTH, GRID_HEIGHT)
        self.engineers = self.create_engineers()
        self.beast = self.create_beast()
        self.turn_counter = 0
        self.zombie_order = []
        self.phase = GamePhase.SETUP
        self.entities = [self.beast] + self.engineers
        self.current_turn_index = 0
        self.last_update_time = time.time()
        self.update_interval = 0.1
        self.beast_target = {}
        self.spiral_direction = Direction.RIGHT
        self.spiral_steps = 1
        self.steps_taken = 0
        self.score_counter = 1
        self.game_over = False
        self.csv_results = []
        self.end_game_turns = END_GAME_TURNS
        
    
    def create_beast(self) -> Entity:
        while True:
            position = self.random_position()
            if not any(engineer.position == position for engineer in self.engineers):
                return Entity(
                    position=position,
                    emoji=BEAST_EMOJI,
                    name='Beast',
                    entity_type=EntityType.BEAST,
                    ai_function=self.beast_ai
                )

    def create_engineers(self) -> List[Entity]:
        ai_functions = [rapid_ryan, saboteur, randomy_savage, mr_sinister, mui_shaggy, leeroy, leprechaun, brave_sir_robin, edgy_engineer, aaahhhhh]
        return [
            Entity(
                position=self.random_position(),
                emoji=emoji,
                name=name,
                entity_type=EntityType.ENGINEER,
                ai_function=ai_func
            )
            for emoji, name, ai_func in zip(ENGINEER_EMOJIS, ENGINEER_NAMES, ai_functions)
        ]


    def random_position(self) -> Position:
        return (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    def update(self) -> bool:
        current_time = time.time()
        print(self.phase)
        if current_time - self.last_update_time < self.update_interval:
            return False
        
        if self.phase == GamePhase.GAME_OVER:
            if not self.game_over:
                self.end_game()
            return False

        self.update_current_entity()
        self.check_collisions()
        self.update_game_phase()
        self.advance_turn()

        self.last_update_time = current_time
        return True
    
    def end_game(self):
        self.calculate_final_scores()
        print('game ended!')
        self.game_over = True
        self.csv_results = save_results_to_csv(self)

    def update_current_entity(self):
        entity = self.entities[self.current_turn_index]
        if entity.entity_type == EntityType.BEAST:
            self.update_beast()
        elif entity.entity_type == EntityType.ENGINEER:
            self.update_engineer(entity)
        elif entity.entity_type == EntityType.ZOMBIE:
            self.update_zombie(entity)

    def get_beast_move_frequency(self) -> int:
        if self.turn_counter < BEAST_MOVEMENT[1]:
            return 2
        elif self.turn_counter < BEAST_MOVEMENT[2]:
            return 3
        else:
            return 1

    def update_engineer(self, engineer: Entity):
        if not engineer.alive:
            return

        other_engineers = [e.position for e in self.engineers if e != engineer]
        beast_positions = [self.beast.position] + [e.position for e in self.entities if e.entity_type == EntityType.ZOMBIE]
        if engineer.name == 'Leeroy':
            direction = engineer.ai_function(engineer.position, beast_positions, 
            other_engineers, (GRID_WIDTH, GRID_HEIGHT), self.turn_counter)
        elif engineer.name == 'Aaahhhhh':
            direction = engineer.ai_function(engineer.position, beast_positions, 
            other_engineers, (GRID_WIDTH, GRID_HEIGHT), self.turn_counter)
        else:
            direction = engineer.ai_function(engineer.position, beast_positions, 
            other_engineers, (GRID_WIDTH, GRID_HEIGHT))
        
        if isinstance(direction, Direction):
            engineer.position = self.grid.move(engineer.position, direction)
        elif direction == None:
            engineer.position = self.grid.move(engineer.position, None)
        elif isinstance(direction, str):
            direction_enum = self.string_to_direction(direction)
            if direction_enum:
                engineer.position = self.grid.move(engineer.position, direction_enum)
            else:
                print(f"Warning: Invalid direction string '{direction}' returned by AI for engineer {engineer.name}")
        else:
            print(f"Warning: Invalid direction type returned by AI for engineer {engineer.name}")

    def update_beast(self):
        if self.turn_counter < BEAST_MOVEMENT[0]:
            return
        move_frequency = self.get_beast_move_frequency()
        if self.turn_counter % move_frequency == 0:
            if self.turn_counter % 5 == 3:
                direction = random.choice(list(Direction))
            else:
                direction = self.beast_ai(self.beast)
            self.beast.position = self.grid.move(self.beast.position, direction)
        
        if self.turn_counter % 5 == 0:
            direction = self.beast_ai(self.beast)
            self.beast.position = self.grid.move(self.beast.position, direction)

        if BEAST_BEAST_MODE:
            if self.turn_counter % 5 == 2:
                direction = self.beast_ai(self.beast)
                self.beast.position = self.grid.move(self.beast.position, direction)


        if self.turn_counter >= BEAST_APPEARS:
            self.phase = GamePhase.BEAST_VISIBLE

    def update_zombie(self, zombie: Entity):
        if self.turn_counter - zombie.last_moved >= 2:
            direction = self.beast_ai(zombie)
            zombie.position = self.grid.move(zombie.position, direction)
            zombie.last_moved = self.turn_counter

    def check_collisions(self):
        for engineer in self.engineers:
            if engineer.alive and engineer.entity_type == EntityType.ENGINEER:
                if engineer.position == self.beast.position and self.phase == GamePhase.BEAST_VISIBLE:
                    self.turn_engineer_into_zombie(engineer)
                elif any(zombie.position == engineer.position for zombie in self.entities if zombie.entity_type == EntityType.ZOMBIE):
                    self.turn_engineer_into_zombie(engineer)




    def update_game_phase(self):
        if self.turn_counter == BEAST_APPEARS:
            self.phase = GamePhase.BEAST_VISIBLE
        elif all(eng.entity_type == EntityType.ZOMBIE or not eng.alive for eng in self.engineers) or \
            self.turn_counter >= END_GAME_TURNS or \
            sum(1 for eng in self.engineers if eng.entity_type == EntityType.ENGINEER and eng.alive) <= 1:
                self.phase = GamePhase.GAME_OVER
                self.end_game()




    def turn_engineer_into_zombie(self, engineer: Entity):
        engineer.entity_type = EntityType.ZOMBIE
        engineer.emoji = ZOMBIE_EMOJI
        engineer.ai_function = self.beast_ai
        self.zombie_order.append(engineer.name)
        engineer.score = self.score_counter
        self.score_counter += 1



    def calculate_final_scores(self):
        for eng in self.engineers:
            if eng.entity_type == EntityType.ENGINEER:
                eng.score += self.score_counter
                eng.score += 2  # Bonus points for surviving

    def advance_turn(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.entities)
        if self.current_turn_index == 0:
            self.turn_counter += 1
    def get_nearby_engineers(self, entity: Entity, radius: int) -> List[DetectedEngineer]:
        nearby = []
        for eng in self.engineers:
            if eng.entity_type == EntityType.ENGINEER and eng.alive and self.grid.distance(entity.position, eng.position) <= radius:
                detected_eng = next((de for de in entity.detected_engineers if de.name == eng.name), None)
                if detected_eng:
                    detected_eng.position = eng.position
                else:
                    detected_eng = DetectedEngineer(eng.name, eng.position, self.turn_counter)
                    entity.detected_engineers.append(detected_eng)
                nearby.append(detected_eng)
            else:
                entity.detected_engineers = [de for de in entity.detected_engineers if de.name != eng.name]

        return sorted(nearby, key=lambda x: x.detected_turn, reverse=True)

    def beast_ai(self, entity: Entity) -> Direction:
        nearby_engineers = self.get_nearby_engineers(entity, BEAST_DETECTION_RADIUS if entity.entity_type == EntityType.BEAST else ZOMBIE_DETECTION_RADIUS)
        
        if nearby_engineers:
            print('--------')
            print(entity.name)
            print(nearby_engineers)
            target_eng = nearby_engineers[0]
            self.beast_target[entity.name] = target_eng.name
            target_pos = target_eng.position

            dx = target_pos[0] - entity.position[0]
            dy = target_pos[1] - entity.position[1]

            if abs(dx) > abs(dy):
                return Direction.RIGHT if dx > 0 else Direction.LEFT
            else:
                return Direction.DOWN if dy > 0 else Direction.UP
        
        # If no engineers are nearby, use a spiral search pattern
        next_position = self.get_next_spiral_position(entity.position)
        while not self.grid.is_valid_position(next_position):
            self.update_spiral_direction()
            next_position = self.get_next_spiral_position(entity.position)

        self.steps_taken += 1
        if self.steps_taken == self.spiral_steps:
            self.update_spiral_direction()

        self.beast_target[entity.name] = None
        return self.spiral_direction

    def get_next_spiral_position(self, current_position: Position) -> Position:
        x, y = current_position
        if self.spiral_direction == Direction.RIGHT:
            return (x + 1, y)
        elif self.spiral_direction == Direction.DOWN:
            return (x, y + 1)
        elif self.spiral_direction == Direction.LEFT:
            return (x - 1, y)
        else:  # Direction.UP
            return (x, y - 1)

    def update_spiral_direction(self):
        self.steps_taken = 0
        if self.spiral_direction == Direction.RIGHT:
            self.spiral_direction = Direction.DOWN
        elif self.spiral_direction == Direction.DOWN:
            self.spiral_direction = Direction.LEFT
            self.spiral_steps += 1
        elif self.spiral_direction == Direction.LEFT:
            self.spiral_direction = Direction.UP
        else:  # Direction.UP
            self.spiral_direction = Direction.RIGHT
            self.spiral_steps += 1

    @staticmethod
    def string_to_direction(direction_str: str) -> Direction:
        direction_map = {
            'up': Direction.UP,
            'down': Direction.DOWN,
            'left': Direction.LEFT,
            'right': Direction.RIGHT
        }
        return direction_map.get(direction_str.lower(), None)

    def to_dict(self) -> Dict:
        return {
            'beast': self.beast.position if self.phase == GamePhase.BEAST_VISIBLE else None,
            'engineers': [
                {
                    'position': eng.position,
                    'emoji': eng.emoji,
                    'name': eng.name,
                    'alive': eng.alive,
                    'is_zombie': eng.entity_type == EntityType.ZOMBIE,
                    'last_moved': eng.last_moved,
                    'targeted_by': eng.targeted_by
                }
                for eng in self.engineers
            ],
            'turn_counter': self.turn_counter,
            'grid_size': (self.grid.width, self.grid.height),
            'game_over': self.phase == GamePhase.GAME_OVER,
            'zombie_order': self.zombie_order,
            'beast_hidden': self.phase == GamePhase.BEAST_HIDDEN,
            'current_turn_entity': self.entities[self.current_turn_index].name,
            'beast_target': self.beast_target,
            'detected_engineers': {
                entity.name: [
                    {'name': de.name, 'position': de.position, 'detected_turn': de.detected_turn}
                    for de in entity.detected_engineers
                ]
                for entity in [self.beast] + [e for e in self.engineers if e.entity_type == EntityType.ZOMBIE]
            },
            'csv_results': self.csv_results,
            'end_game_turns': self.end_game_turns,
        }

    def reset(self):
        self.__init__()
