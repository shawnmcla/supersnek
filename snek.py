"""
> S U P E R S N E K V1.0
> Description: A wee little console based Snake game
> Author: Shawn McLaughlin <shawnmcdev@gmail.com>
> Source: <<REPO LINK HERE>>
> License: MIT
"""

import colorama, time, sys, os, random
from msvcrt import getch, kbhit
from collections import deque

DEBUG = False
COLOR_ENABLED = True

GRID_WIDTH = 30
GRID_HEIGHT = 20
STEP_TIME = 0.15
DIFFICULTY_MULTIPLIER = 2

LEFT = 1
RIGHT = 2
UP = 3
DOWN = 4

DEATH_ANIM_TIME = 1.0

UP_ARROW = 72
RIGHT_ARROW = 77
DOWN_ARROW = 80
LEFT_ARROW = 75

DIRECTION_MAP = {
    UP_ARROW: UP,
    DOWN_ARROW: DOWN,
    RIGHT_ARROW: RIGHT,
    LEFT_ARROW: LEFT
}

colorama.init()

SYMBOLS = {
    "SNAKE": "o",
    "SNAKE_HEAD": "O",
    "APPLE": "@",
    "EMPTY": " "
}

SYMBOLS_COLOR = {
    "SNAKE": colorama.Fore.LIGHTGREEN_EX + "o" + colorama.Fore.RESET,
    "SNAKE_HEAD": colorama.Fore.LIGHTYELLOW_EX + "O" + colorama.Fore.RESET,
    "APPLE": colorama.Fore.LIGHTRED_EX + "@" + colorama.Fore.RESET,
    "EMPTY": " "
}

DEATH_MESSAGE = "Oh no! Snek is dead (x_x)"
DEATH_MESSAGE_COLOR = f"Oh no! Snek is {colorama.Fore.LIGHTRED_EX}dead\
{colorama.Fore.RESET} (x_x)"

BANNER = """\
   _____ _    _ _____  ______ _____   _____ _   _ ______ _  __ 
  / ____| |  | |  __ \|  ____|  __ \ / ____| \ | |  ____| |/ / 
 | (___ | |  | | |__) | |__  | |__) | (___ |  \| | |__  | ' / 
  \___ \| |  | |  ___/|  __| |  _  / \___ \| . ` |  __| |  < 
  ____) | |__| | |    | |____| | \ \ ____) | |\  | |____| . \ 
 |_____/ \____/|_|    |______|_|  \_\_____/|_| \_|______|_|\_\ 
 """

# Shout out http://www.patorjk.com/software/taag/ for the text generator<3


class Game:
    """Core Game class, manages the game and all its components."""

    def __init__(self):
        self.board = Board(GRID_WIDTH, GRID_HEIGHT)
        self.snake = Snake(GRID_WIDTH, GRID_HEIGHT)
        self.border_top = " " + "_" * (GRID_WIDTH * 2 - 1)
        self.border_bottom = " " + "¯" * (GRID_WIDTH * 2 - 1)
        self.buffer = [BANNER, self.border_top, self.border_bottom,
                       "Press Any Key to Begin!".center(58, " ")]
        self.draw()
        getch()
        self.set_status_message("Eat the apples, snek!")
        self.update()

    def update(self):
        """Core game loop.

        Checks for input, updates game objects and calls draw methods.
        """

        while kbhit():  # Loop until there are no keypresses to process
            key = ord(getch())
            if key == 224:  # Special keys
                key = ord(getch())
                self.snake.set_direction(DIRECTION_MAP[key])
        if not self.snake.update() or not self.board.update(self.snake):
            self.set_status_message(DEATH_MESSAGE)
            for _ in self.snake.death_anim():
                self.draw()
            self.draw()
            return
        self.set_status_message(self.get_stats())
        self.draw()
        time.sleep(STEP_TIME)
        self.update()

    def set_status_message(self, msg):
        """Set the status message (last line of buffer) to string."""

        self.buffer[-1] = msg.center(58, " ")

    def get_stats(self):
        return f"Snek head: {self.snake.get_head()} Q"\
            f"{self.board.get_quadrant(self.snake.get_head())} |"\
            f"Apples Nom'd: {self.snake.apples_eaten} |"\
            f"Snek length: {len(self.snake.segments)}"

    def draw(self):
        """Clear the screen and re-draw game elements."""
        os.system('cls')
        self.board.draw(self.snake)
        self.buffer[2:-2] = [f"|{' '.join(row)}|" for row in self.board]
        sys.stdout.write('\n'.join(self.buffer) + "\n")


class Snake:
    """The Snake is the player controlled character.

    This class encapsulates its data such as his position, his
    segments, direction, etc.
    """

    def __init__(self, board_width: int, board_height: int):
        self.board_width = board_width
        self.board_height = board_height
        self.segments = deque()
        self.direction = LEFT
        self.last_direction = None
        self.apples_eaten = 0
        self.reset()

    def reset(self) -> None:
        """Set the segments deque to contain the three starting segments."""
        starting_point = (self.board_width//2, self.board_height//2)
        self.segments.append((starting_point[0], starting_point[1]))
        self.segments.append((starting_point[0]+1, starting_point[1]))
        self.segments.append((starting_point[0]+2, starting_point[1]))

    def set_direction(self, direction: int) -> None:
        """Triggered by input, set the direction.

        We do not validate the direction in this method since this
        in theory could be called tens or hundreds of times before the
        next frame.
        """
        self.direction = direction

    def move(self) -> bool:
        """'Move' the snake based on the set direction.

        This is done by removing (popping) the last segment,
        and appending a new segment according to the direction,
        relative to the start(head) of the snake.
        """

        self.segments.pop()
        head = self.segments[0]
        new_segment = (0, 0)
        if self.direction == UP:
            new_segment = (head[0], head[1]-1)
        elif self.direction == DOWN:
            new_segment = (head[0], head[1]+1)
        elif self.direction == LEFT:
            new_segment = (head[0]-1, head[1])
        elif self.direction == RIGHT:
            new_segment = (head[0]+1, head[1])
        else:
            raise ValueError

            # Check if snake is out of bounds
        if new_segment[0] < 0 or new_segment[0] >= GRID_WIDTH or\
                new_segment[1] < 0 or new_segment[1] >= GRID_HEIGHT:
            return False

        self.segments.appendleft(new_segment)
        return True

    def grow(self, amount: int) -> None:
        """Add new segments to the snake."""

        self.apples_eaten += 1
        tail = self.segments.pop()
        self.segments.append(tail)
        for i in range(amount):
            self.segments.append(tail)

    def get_head(self) -> tuple:
        """Get an (x,y) tuple of the position of the snake's head."""
        return self.segments[0] if len(self.segments) else (0, 0)

    def validate_direction(self) -> None:
        """Check that the direction if valid, if not correct it.

        The player can only move at 90 degree angles, therefor if the snake
        is going down, we can't go up. If the snake is going left, we can't
        go right, etc.
        """

        if self.direction == UP and self.last_direction == DOWN:
            self.direction = DOWN
        elif self.direction == DOWN and self.last_direction == UP:
            self.direction = UP
        elif self.direction == LEFT and self.last_direction == RIGHT:
            self.direction = RIGHT
        elif self.direction == RIGHT and self.last_direction == LEFT:
            self.direction = LEFT

        self.last_direction = self.direction

    def update(self) -> bool:
        """Run all methods to simulate one frame of game."""
        self.validate_direction()
        return self.move()

    def death_anim(self):
        """Delete segments from the snake, one by one."""

        total_segments = len(self.segments)
        sleep_per_segment = DEATH_ANIM_TIME/total_segments
        for i in range(total_segments):
            yield
            self.segments.pop()
            time.sleep(sleep_per_segment)

    def __iter__(self):
        return iter(self.segments)


class Board:
    """Holds the game board data and its contents and manages it."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        halfwidth = width//2
        halfheight = height//2
        # Top left and bottom right corners of quadrants
        self.quadrants = [
            # 0 -> Top Left
            ((0, 0), (halfwidth-1, halfheight-1)),
            # 1 -> Top Right
            ((halfwidth, 0), (self.width-1, halfheight-1)),
            # 2 -> Bottom Right
            ((halfwidth, halfheight), (self.width-1, self.height-1)),
            # 3 -> Bottom Left
            ((0, halfheight), (halfwidth, self.height-1))
        ]
        self.grid = []
        self.apples = [(1, 1), (10, 10)]
        self.reset()

    def reset(self) -> None:
        """Clear the grid."""

        self.grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(SYMBOLS['EMPTY'])
            self.grid.append(row)

    def update(self, snake: Snake) -> bool:
        """Update the grid.

        Places the items on the grid (snake segments, apples, etc.)
        Returns false if the player loses
        """

        segments = list(snake.segments)
        snake_head = snake.get_head()

        # Check if snake is colliding with an apple
        for apple in self.apples:
            if apple == snake_head:
                self.apples.remove(apple)
                snake.grow(2)
                if not len(self.apples):
                    self.spawn_new_apple(snake_head)

        # Check if snake is colliding with itself (dies) x.x
        if segments.count(snake_head) != 1:
            return False

        return True

    def spawn_new_apple(self, snake_head: tuple) -> None:
        """Add an apple to the board in one of the vacant quadrants."""

        snake_quadrant = self.get_quadrant(snake_head)
        possible_quadrants = [0,1,2,3]
        possible_quadrants.remove(snake_quadrant)
        apple_quadrant = self.quadrants[random.choice(possible_quadrants)]
        apple_x = random.randint(apple_quadrant[0][0], apple_quadrant[1][0])
        apple_y = random.randint(apple_quadrant[0][1], apple_quadrant[1][1])
        self.apples.append((apple_x, apple_y))

    def get_quadrant(self, coords):
        """Return the quadrant index for the specify coordinates"""

        for i in range(len(self.quadrants)):
            quad = self.quadrants[i]
            if coords[0] >= quad[0][0] and\
               coords[0] <= quad[1][0] and\
               coords[1] >= quad[0][1] and\
               coords[1] <= quad[1][1]:
                return i
        raise Exception("Invalid coordinates")

    def draw(self, snake):
        """Add the game objects onto the board."""

        self.reset()
        segments = list(snake.segments)
        if not len(segments):
            return
        for apple in self.apples:
            self.grid[apple[1]][apple[0]] = SYMBOLS["APPLE"]
        head = snake.segments[0]
        self.grid[head[1]][head[0]] = SYMBOLS["SNAKE_HEAD"]
        for seg in segments[1:]:
            self.grid[seg[1]][seg[0]] = SYMBOLS["SNAKE"]
        # Debug: Draw quadrant markers
        if DEBUG:
            for quad in self.quadrants:
                self.grid[quad[0][1]][quad[0][0]] = "0"
                self.grid[quad[1][1]][quad[1][0]] = "1"

    def __iter__(self):
        return iter(self.grid)


def main():
    global SYMBOLS
    global DEATH_MESSAGE
    if COLOR_ENABLED:
        SYMBOLS = SYMBOLS_COLOR
        DEATH_MESSAGE = DEATH_MESSAGE_COLOR
    game = Game()


if __name__ == "__main__":
    if "-d" in sys.argv:
        DEBUG = True
    if "-nc" in sys.argv:
        COLOR_ENABLED = False
    # TODO: Proper getopt parsing
    main()

"""
TODO:
[*] Add support for non-windows
"""
