import argparse
import pathlib
import typing as tp

import pygame
from pygame.locals import *

from life import GameOfLife
from ui import UI


class GUI(UI):
    def __init__(self, life: GameOfLife, cell_size: int = 10, speed: int = 10) -> None:
        self.life = life
        # number of cells horizontally
        self.cell_width = self.life.cols
        # number of cells vertically
        self.cell_height = self.life.rows
        # window width
        self.width = self.cell_width * cell_size
        # window height
        self.height = self.cell_height * cell_size

        self.cell_size = cell_size
        self.speed = speed

        self.screen_size = self.width, self.height
        # creating a new window
        self.screen = pygame.display.set_mode(self.screen_size)
        super().__init__(life)

    def draw_lines(self) -> None:
        """Drawing grid lines"""
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (0, y), (self.width, y))

    def draw_grid(self) -> None:
        """Filling the grid with colors"""
        grid = self.life.curr_generation
        for row in range(self.cell_height):
            for column in range(self.cell_width):
                if grid[row][column] == 1:
                    color = "green"
                else:
                    color = "white"
                pygame.draw.rect(
                    self.screen,
                    pygame.Color(color),
                    (column * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size),
                )

    def run(self) -> None:
        """
        Pressing "space" button - pause/play
        Pressing the left mouse button - change the color of the square
        Pressing "s" button - save file
        """
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption("Game of Life GUI")
        self.screen.fill(pygame.Color("white"))

        running = True
        while running:
            if self.life.is_changing and not self.life.is_max_generations_exceeded:
                for event in pygame.event.get():
                    if event.type == QUIT:  # type: ignore
                        running = False
                    if event.type == KEYDOWN:  # type: ignore
                        if event.key == K_SPACE:  # type: ignore
                            running = self.is_paused()
                        if event.key == K_s:  # type: ignore
                            self.life.save(pathlib.Path(arguments.to_file))
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:  # type: ignore
                        self.draw_update_grid(event.pos)
                self.draw_grid()
                self.life.step()
                self.draw_lines()

                pygame.display.flip()
                clock.tick(self.speed)
            else:
                self.life.max_generations = float("inf")
                running = self.is_paused()
        pygame.quit()

    def draw_update_grid(self, mouse_pos: tp.Tuple[int, int]) -> None:
        """
        Change square color
        """
        width, height = mouse_pos
        row = height // self.cell_size
        col = width // self.cell_size
        if self.life.curr_generation[row][col] == 1:
            self.life.curr_generation[row][col] = 0
            colour = "white"
        else:
            self.life.curr_generation[row][col] = 1
            colour = "green"

        pygame.draw.rect(
            self.screen,
            pygame.Color(colour),
            (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size),
        )
        self.draw_lines()
        pygame.display.flip()

    def is_paused(self) -> bool:
        """
        Pause the game
        """
        pause = True
        while pause:
            for event in pygame.event.get():
                if event.type == QUIT:  # type: ignore
                    return False
                    pause = False
                if event.type == KEYDOWN:  # type: ignore
                    if event.key == K_SPACE:  # type: ignore
                        pause = False
                    if event.key == K_s:  # type: ignore
                        self.life.save(pathlib.Path(arguments.to_file))
                if event.type == MOUSEBUTTONDOWN and event.button == 1:  # type: ignore
                    self.draw_update_grid(event.pos)
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Game of Life arguments")
    parser.add_argument("--height", dest="height", type=int, default="500")
    parser.add_argument("--width", dest="width", type=int, default="500")
    parser.add_argument("--max-generations", dest="max_generations", type=int, default="200")
    parser.add_argument(
        "--from-file", dest="from_file", type=str, default="", help="read from this file"
    )
    parser.add_argument(
        "--to-file", dest="to_file", type=str, default="grid.txt", help="write to this file"
    )
    parser.add_argument("--cell-size", dest="cell_size", type=int, default="10")
    parser.add_argument("--speed", dest="speed", type=int, default="10")

    arguments = parser.parse_args()
    if arguments.from_file == "":
        life = GameOfLife(
            (arguments.height // arguments.cell_size, arguments.width // arguments.cell_size),
            max_generations=arguments.max_generations,
        )
    else:
        life = GameOfLife.from_file(pathlib.Path(arguments.from_file))
    game = GUI(life, arguments.cell_size, arguments.speed)
    game.run()
