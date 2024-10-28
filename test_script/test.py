import random
import time
from typing import Tuple, List
from enum import Enum

# Game constants
GRID_WIDTH, GRID_HEIGHT = 10, 10
BEAST_DETECTION_RADIUS = 5
BEAST_EXTRA_MOVE_INTERVAL = 5

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

Position = Tuple[int, int]

class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

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
            return pos
        
        return new_pos if self.is_valid_position(new_pos) else pos

    @staticmethod
    def distance(pos1: Position, pos2: Position) -> float:
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5

class GameState:
    def __init__(self):
        self.grid = Grid(GRID_WIDTH, GRID_HEIGHT)
        self.beast_pos = self.random_position()
        self.engineer_pos = self.random_position()
        self.turn_counter = 0

    def random_position(self) -> Position:
        return (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    def update(self, engineer_ai):
        # Engineer's turn
        engineer_direction = engineer_ai(self.engineer_pos, [self.beast_pos], [], (GRID_WIDTH, GRID_HEIGHT))
        if isinstance(engineer_direction, str):
            engineer_direction = Direction[engineer_direction.upper()]
        self.engineer_pos = self.grid.move(self.engineer_pos, engineer_direction)

        # Beast's turn
        self.move_beast()

        # Extra move for the beast every 5 turns
        if self.turn_counter % BEAST_EXTRA_MOVE_INTERVAL == 0:
            self.move_beast()
            print("Beast gets an extra move!")

        self.turn_counter += 1

    def move_beast(self):
        if self.grid.distance(self.beast_pos, self.engineer_pos) <= BEAST_DETECTION_RADIUS:
            beast_direction = self.chase_engineer()
        else:
            beast_direction = self.random_move()
        self.beast_pos = self.grid.move(self.beast_pos, beast_direction)

    def chase_engineer(self) -> Direction:
        dx = self.engineer_pos[0] - self.beast_pos[0]
        dy = self.engineer_pos[1] - self.beast_pos[1]

        if abs(dx) > abs(dy):
            return Direction.RIGHT if dx > 0 else Direction.LEFT
        else:
            return Direction.DOWN if dy > 0 else Direction.UP

    def random_move(self) -> Direction:
        return random.choice(list(Direction))

    def is_game_over(self) -> bool:
        return self.engineer_pos == self.beast_pos

    def print_board(self):
        print(f"Turn: {self.turn_counter}")
        for y in range(GRID_HEIGHT):
            row = ""
            for x in range(GRID_WIDTH):
                if (x, y) == self.beast_pos:
                    row += "B"
                elif (x, y) == self.engineer_pos:
                    row += "E"
                else:
                    row += "."
            print(row)
        print()

def run_simulation(engineer_ai, max_turns=100):
    game = GameState()
    
    while not game.is_game_over() and game.turn_counter < max_turns:
        game.print_board()
        game.update(engineer_ai)
        time.sleep(1)  # Add a 1-second delay between turns

    game.print_board()
    if game.is_game_over():
        print(f"Game Over! The engineer was caught on turn {game.turn_counter}.")
    else:
        print(f"The engineer survived for {max_turns} turns!")

# Example engineer AI function
def example_engineer_ai(self_pos: Position, beast_pos: List[Position], other_engineers: List[Position], grid_size: Tuple[int, int]) -> Direction:
    return random.choice([Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT])

# Run the simulation
if __name__ == "__main__":
    run_simulation(example_engineer_ai)