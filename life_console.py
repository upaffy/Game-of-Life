import argparse
import curses
import curses.ascii
import pathlib

from life import GameOfLife
from ui import UI


class Console(UI):
    def __init__(self, life: GameOfLife) -> None:
        self.life = life
        self.rows = self.life.rows
        self.cols = self.life.cols
        super().__init__(life)

    def draw_borders(self, screen) -> None:
        """ Отобразить рамку. """
        screen.border(0)

    def draw_grid(self, screen) -> None:
        """ Отобразить состояние клеток. """
        grid = self.life.curr_generation
        for row in range(self.rows):
            for col in range(self.cols):
                if grid[row][col] == 1:
                    screen.addch(row + 1, col + 1, "*")
                else:
                    screen.addch(row + 1, col + 1, " ")
                    # +1 необходимо, так как рамка проходит по всем (0,n) и (m,0), где m и n изменяются
                    # в диапазоне от 0 до значений длины столбцов и длины строк соответственно,
                    # перекрывая тем самым стоящие на этих позициях символы, обозначающие живые и мертвые клетки

    def run(self) -> None:
        """
        esc - выйти из игры
        space - поставить игру на паузу / снять игру с паузы
        TAB - сохранить игру в файл
        """
        curses.initscr()
        screen = curses.newwin(self.rows + 2, self.cols + 2)
        # +2 необходимо добавить к ширине и высоте окна, так как рамка
        # перекрывает символы по причинам, аналогичным тем, которые описаны выше в пояснении
        curses.noecho()
        screen.keypad(True)
        screen.timeout(250)

        key = 666
        esc_from_pause = 0

        while key != curses.ascii.ESC and esc_from_pause != 1:
            if self.life.is_changing and not self.life.is_max_generations_exceeded:

                self.draw_grid(screen)
                self.life.step()
                self.draw_borders(screen)

                prev_key = key
                event = screen.getch()

                if event == curses.ascii.TAB:
                    self.life.save(pathlib.Path(arguments.to_file))

                if event != -1:
                    key = event
                if key == curses.ascii.SP:
                    key = -1
                    while key != curses.ascii.SP:
                        key = screen.getch()
                        if key == curses.ascii.ESC:
                            esc_from_pause = 1
                            break
                        if key == curses.ascii.TAB:
                            self.life.save(pathlib.Path(arguments.to_file))

                    key = prev_key
            else:
                while key != curses.ascii.ESC:
                    key = screen.getch()
                    if key == curses.ascii.TAB:
                        self.life.save(pathlib.Path(arguments.to_file))
        curses.endwin()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Game of Life arguments")
    parser.add_argument("--rows", dest="row", type=int, default="50")
    parser.add_argument("--cols", dest="col", type=int, default="100")
    parser.add_argument("--max-generations", dest="max_generations", type=int, default="200")
    parser.add_argument(
        "--from-file", dest="from_file", type=str, default="", help="считать этот файл"
    )
    parser.add_argument(
        "--to-file", dest="to_file", type=str, default="grid.txt", help="записать в этот файл"
    )
    arguments = parser.parse_args()
    if arguments.from_file == "":
        life = GameOfLife((arguments.row, arguments.col), max_generations=arguments.max_generations)
    else:
        life = GameOfLife.from_file(pathlib.Path(arguments.from_file))
    game = Console(life)
    game.run()
