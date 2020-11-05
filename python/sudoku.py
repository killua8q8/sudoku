import threading, time
import numpy as np


class Sudoku:
    """Class to represent a sudoku. New pattern will be generated each time a new
    instance of this class is instantiated.

    Kwargs:
        dummy (optional): If set to True, a dummy grid will be created (all 0s).
            Defaults False.
    """
    def __init__(self, dummy: bool=False) -> None:
        self.grid = np.array([0] * 81).reshape(9, 9)
        if not dummy:
            self.generate()
        self.solution = self.grid.copy()
        self.ready = True

    def __repr__(self) -> str:
        """Make this sudoku representable."""
        return self.to_text(self)

    @property
    def solved(self) -> bool:
        """Getter to retrieve a boolean to indicate if current sudoku is fully solved."""
        return (self.grid != 0).all()

    def generate(self) -> bool:
        """Method to recursively fill in a sudoku grid with backtracking to check
        all possible combinations until the grid is valid.

        Returns:
            True if the grid is completely filled.
        """
        numbers = np.arange(1, 10)
        for i in range(0, 81):
            row, col = i // 9, i % 9
            if self.grid[row, col] == 0:
                np.random.shuffle(numbers)
                for number in numbers:
                    if self.__check_cell(self.grid, row, col, number):
                        self.grid[row, col] = number
                        if self.solved:
                            return True
                        elif self.generate():
                            return True
                break
        self.grid[row, col] = 0

    def leveling(self, level: int=3, attempts: int=5) -> None:
        """Method to level current sudoku. Random cell will be cleared one by one,
        up to the `level` specific cells.

        Kwargs:
            level (optional): A number to indicate the range of cells will cleared.
                Defaults 3.
            attempts (optional): Maximum attempts for removing cell from the sudoku.
                Defaults 5.
        """
        max_zeros = {
            1: np.random.randint(20, 30),
            3: np.random.randint(30, 45),
            5: np.random.randint(45, 65),
        }
        if level not in max_zeros:
            level = 3
        self.ready = False
        while attempts > 0:
            row, col = np.random.randint(0, [9, 9])
            while self.grid[row, col] == 0:
                row, col = np.random.randint(0, [9, 9])
            cell_value = self.grid[row, col]
            self.grid[row, col] = 0

            copy = self.grid.copy()
            solved_count = self.__solve_grid(copy)
            if solved_count != 1:
                self.grid[row, col] = cell_value
                attempts -= 1
            if np.count_nonzero(self.grid == 0) >= max_zeros[level]:
                break
        self.ready = True

    @staticmethod
    def to_text(sudoku: 'Sudoku') -> str:
        """Static method to generate a text to represent the given sudoku.

        Args:
            sudoku: An instance of :class:`Sudoku`.

        Returns:
            String format of the sudoku.
        """
        text = []
        brt = '┏━━━┯━━━┯━━━┳━━━┯━━━┯━━━┳━━━┯━━━┯━━━┓'
        hrl = '┠───┼───┼───╂───┼───┼───╂───┼───┼───┨'
        hrb = '┣━━━┿━━━┿━━━╋━━━┿━━━┿━━━╋━━━┿━━━┿━━━┫'
        brb = '┗━━━┷━━━┷━━━┻━━━┷━━━┷━━━┻━━━┷━━━┷━━━┛'
        text.append(brt)
        for r in range(0, 9):
            row = '┃'
            for c in range(0, 9):
                if not sudoku.ready:
                    char = sudoku.grid[r, c] and '░' or ' '
                else:
                    char = sudoku.grid[r, c] or ' '
                row += f" {char} {c % 3 == 2 and '┃' or '│'}"
            text.append(row)
            r < 8 and text.append(r % 3 == 2 and hrb or hrl)
        text.append(brb)
        return '\n'.join(text)

    @staticmethod
    def draw(sudoku: 'Sudoku') -> None:
        """Static method to draw (output) the rendered sudoku into console.

        Args:
            sudoku: An instance of :class:`Sudoku`.
        """
        print(Sudoku.to_text(sudoku))

    def check_cell(self, row: int, col: int, number: int) -> bool:
        """Method to check the given `number` is valid in [`row`, `col`].

        Args:
            row: Row number for the cell.
            col: Column number for the cell.
            number: Number to check validity.

        Returns:
            True if `number` is valid in [`row`, `col`]. False otherwise.
        """
        return self.__check_cell(self.grid, row, col, number)

    def __check_cell(self, grid: np.ndarray, row: int, col: int, number: int) -> bool:
        """Private method to check the given `number` is valid in [`row`, `col`]
        in a given `grid`.

        Args:
            grid: A 9 by 9 sudoku grid.
            row: Row number for the cell.
            col: Column number for the cell.
            number: Number to check validity.

        Returns:
            True if cell (`row`, `col`) is valid to put in `number`. False otherwise.
        """
        # If `number` already be used on current row
        in_row = (grid[row] == number).any()
        # If `number` already be used on current column
        in_col = (grid.T[col] == number).any()
        # If `number` already be used on current block
        in_blk = (grid[row // 3 * 3:row // 3 * 3 + 3].T[col // 3 * 3:col // 3 * 3 + 3] == number).any()
        return not (in_row or in_col or in_blk)

    def __solve_grid(self, grid: np.ndarray) -> int:
        """Private method to solve a given `grid` with backtracking. This method
        solves for all solution, and will return the number of solutions it found.
        If `max_solved` is specfied, it will stop solving for more solutions when
        solved count reaches `max_solved`.

        Args:
            grid: A 9 by 9 sudoku grid.

        Kwargs:
            max_solved (optional): Max number of solution to throttle with.
                Defaults None.

        Returns:
            Number of the solutions.
        """
        solved = 0
        for i in range(0, 81):
            row, col = i // 9, i % 9
            if grid[row, col] == 0:
                for number in range(1, 10):
                    if self.__check_cell(grid, row, col, number):
                        grid[row, col] = number
                        if (grid != 0).all():
                            solved += 1
                            break
                        else:
                            solved += self.__solve_grid(grid)
                break
        grid[row, col] = 0
        return solved

    @staticmethod
    def solve(sudoku: 'Sudoku') -> None:
        t = threading.currentThread()
        if getattr(t, 'exit', False):
            return True
        numbers = np.arange(1, 10)
        for i in range(0, 81):
            row, col = i // 9, i % 9
            if sudoku.grid[row, col] == 0:
                np.random.shuffle(numbers)
                for number in numbers:
                    if sudoku.check_cell(row, col, number):
                        sudoku.grid[row, col] = number
                        time.sleep(0.05)    # Add delay for visualization
                        if sudoku.solved:
                            return True
                        elif Sudoku.solve(sudoku):
                            return True
                break
        sudoku.grid[row, col] = 0
