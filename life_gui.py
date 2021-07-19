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
        # количество ячеек по горизонтали
        self.cell_width = self.life.cols
        # количество ячеек по вертикали
        self.cell_height = self.life.rows
        # ширина окна
        self.width = self.cell_width * cell_size
        # высота окна
        self.height = self.cell_height * cell_size
        # размер клетки
        self.cell_size = cell_size
        # скорость
        self.speed = speed
        # размеры окна
        self.screen_size = self.width, self.height
        # создание нового окна
        self.screen = pygame.display.set_mode(self.screen_size)
        super().__init__(life)

    def draw_lines(self) -> None:
        """ Отрисовать сетку """
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (0, y), (self.width, y))

    def draw_grid(self) -> None:
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
        """ "
        space - поставить на паузу / снять с паузы
        нажатие ЛКМ по квадратику меняет его цвет
        s - сохранить файл
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
        Изменить цвет квадратика сразу после нажатия
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
        Поставить игру на паузу
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
        "--from-file", dest="from_file", type=str, default="", help="считать этот файл"
    )
    parser.add_argument(
        "--to-file", dest="to_file", type=str, default="grid.txt", help="записать в этот файл"
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
    game = GUI(life)
    game.run()
