import atexit, curses, sys, time, threading
from sudoku import Sudoku


class Game:
    """Class to create a simple Sudoku game with minimal menu supports.
    """
    game_menu = {
        'S': [
            dict(value=1, label='New Game'),
            dict(value=0, label='Exit'),
        ],
        'N': [
            dict(value=1, label='Beginner'),
            dict(value=3, label='Normal'),
            dict(value=5, label='Hard'),
            dict(value=0, label='Exit'),
        ],
        'G': [
            dict(value=1, label='Solve For Me'),
            dict(value=2, label='New Game'),
            dict(value=0, label='Exit'),
        ],
        'R': [
            dict(value=1, label='Stop'),
        ],
    }

    def __init__(self) -> None:
        self.sudoku = Sudoku(dummy=True)
        self.state = 'S'
        self.menu_selection = 0
        self._debug_texts = ['Debug Log', '', '']
        self.init_screens()

    def init_screens(self) -> None:
        """Method to initialize screen with curses.
        If screen is too small to initialize, render warning then exit.
        """
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.curs_set(0)

        scrrows, scrcols = self.stdscr.getmaxyx()
        minrows, mincols = 28, 37
        if scrrows < minrows or scrcols < mincols:
            self.stdscr.addstr(scrrows // 2, max(scrcols - 24, 0) // 2, 'Screen size is too small')
            self.stdscr.addstr(scrrows // 2 + 2, max(scrcols - 28, 0) // 2, 'Change the size and try again')
            self.stdscr.getkey()
            sys.exit()

        row_offset = (scrrows - minrows) // 2
        self._gridscr = self.stdscr.subwin(19, scrcols, row_offset, 0)
        self._menuscr = self.stdscr.subpad(6, scrcols, row_offset + 20, 0)
        self._debugsrc = self.stdscr.subwin(3, scrcols, scrrows - 3, 0)

        self._menuscr.keypad(True)
        # self._menuscr.nodelay(True)

        @atexit.register
        def goodbye() -> None:
            curses.endwin()

    def transit(self, new_state: str) -> None:
        """Method to make game state transition.

        Args:
            new_state: Game state to transit to.
        """
        self.state = new_state
        self.menu_selection = 0

    def start(self) -> None:
        """Method to start the game threads."""
        self.running = True
        renderer_thread = threading.Thread(target=self.renderer)
        menu_thread = threading.Thread(target=self.menu_select)
        renderer_thread.start()
        menu_thread.start()
        menu_thread.join()
        renderer_thread.join()

    def renderer(self, fps: int=30) -> None:
        """Game-thread method to draw and render frames.

        Kwargs:
            fps (optional): Frame per seconds. Defaults 30.
        """
        while self.running:
            time.sleep(1 / fps)
            self.draw_grid()
            self.draw_menu()
            self.draw_debug()
            curses.doupdate()

    def menu_select(self) -> None:
        """Game-thread method for menu control."""
        while self.running:
            current_menu = self.game_menu[self.state]
            current_selected = current_menu[self.menu_selection % len(current_menu)]
            key = self._menuscr.getch()
            self._debug_texts[1] = f'Key Raw: {key}'
            if key == 258:
                self._debug_texts[1] = 'Key: DOWN'
                self.menu_selection += 1
            elif key == 259:
                self._debug_texts[1] = 'Key: UP'
                self.menu_selection -= 1
            elif key == 27:
                self._debug_texts[1] = 'Key: Esc'
                self.running = False
                break
            elif key == 10:
                self._debug_texts[1] = 'Key: Enter'
                option = current_selected['value']
                if option == 0:
                    self.running = False
                    break
                elif self.state == 'S':
                    if option == 1:
                        self.transit('N')
                elif self.state == 'N':
                    self.sudoku = Sudoku()
                    self.sudoku.leveling(level=option)
                    self.transit('G')
                elif self.state == 'G':
                    if option == 1:
                        if not self.sudoku.solved:
                            self.transit('R')
                            threading.Thread(target=self.solve_sudoku).start()
                    elif option == 2:
                        self.transit('N')
                elif self.state == 'R':
                    if option == 1:
                        self.transit('G')
            self._debug_texts[2] = f'Menu Selected: {current_selected}'

    def solve_sudoku(self) -> None:
        """Game-thread method to create a solver thread to solve current sudoku.
        If current game state is transited from 'R', terminate the solver thread
        then exit.
        """
        solver_thread = threading.Thread(target=Sudoku.solve, args=(self.sudoku,))
        solver_thread.start()
        solved_time = time.monotonic()
        while solver_thread.is_alive():
            self._debug_texts[1] = f'Solver Alive: {solver_thread.is_alive()} | Time: {time.monotonic() - solved_time}'
            if self.state != 'R':
                solver_thread.exit = True
                solver_thread.join()
                break
        self.transit('S')

    def draw_grid(self) -> None:
        """Method to draw the grid on screen."""
        self._gridscr.erase()
        y, x = self._gridscr.getmaxyx()
        x_offset = max(x - 37, 0) // 2
        for row, line in enumerate(str(self.sudoku).split('\n')):
            self._gridscr.addstr(row, x_offset, line)
        self._gridscr.noutrefresh()

    def draw_menu(self) -> None:
        """Method to draw the menu on screen. Underlines the current selection."""
        self._menuscr.erase()
        y, x = self._menuscr.getmaxyx()
        current_menu = self.game_menu[self.state]
        current_selected = current_menu[self.menu_selection % len(current_menu)]
        for idx, option in enumerate(current_menu):
            x_offset = max(x - len(option['label']), 0) // 2
            self._menuscr.addstr(idx, x_offset, option['label'], option['value'] == current_selected['value'] and curses.A_UNDERLINE)
        self._menuscr.noutrefresh()

    def draw_debug(self) -> None:
        """Method to draw the debug area on screen."""
        self._debugsrc.erase()
        for idx, text in enumerate(self._debug_texts):
            self._debugsrc.addstr(idx, 0, str(text), idx and curses.A_DIM or curses.A_BOLD)
        self._debugsrc.noutrefresh()
