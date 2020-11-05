'use strict';

class Sudoku {

  constructor (dummy=false) {
    this.buffer = new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 81);
    this.grid = new Int32Array(this.buffer);
    !dummy && this.generate();
    this.ready = true;
  }

  get solved () {
    return [...Array(81).keys()].map(idx => {
      const backup = this.grid[idx];
      this.grid[idx] = 0;
      const result = this._check_cell(this.grid, Math.floor(idx / 9), idx % 9, backup);
      this.grid[idx] = backup;
      return result;
    }).every(x => x === true);
  }

  get filled () {
    return this.grid.every(x => x !== 0);
  }

  getCellValue (row, col) {
    return this.grid[row * 9 + col];
  }

  toString () {
    const text = [];
    const brt = '┏━━━┯━━━┯━━━┳━━━┯━━━┯━━━┳━━━┯━━━┯━━━┓';
    const hrl = '┠───┼───┼───╂───┼───┼───╂───┼───┼───┨';
    const hrb = '┣━━━┿━━━┿━━━╋━━━┿━━━┿━━━╋━━━┿━━━┿━━━┫';
    const brb = '┗━━━┷━━━┷━━━┻━━━┷━━━┷━━━┻━━━┷━━━┷━━━┛';
    text.push(brt);
    [...Array(9).keys()].forEach(r => {
      let row = '┃' + [...Array(9).keys()].map(c => {
        let idx = r * 9 + c;
        let char = this.ready ? (this.grid[idx] || ' ') : (this.grid[idx] ? '░' : ' ');
        return ` ${char} ${c % 3 === 2 ? '┃' : '│'}`
      }).join('');
      text.push(row);
      r < 8 && text.push(r % 3 == 2 ? hrb : hrl);
    });
    text.push(brb);
    return text.join('\n');
  }

  generate () {
    let row = 0;
    let col = 0;
    let numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9];
    for (let i of [...Array(81).keys()]) {
      row = Math.floor(i / 9);
      col = i % 9;
      if (this.grid[i] === 0) {
        numbers.shuffle();
        for (let number of numbers) {
          if (this._check_cell(this.grid, row, col, number)) {
            this.grid[i] = number;
            if (this.filled) {
              return true;
            } else if (this.generate()) {
              return true;
            }
          }
        }
        break;
      }
    }
    this.grid[row * 9 + col] = 0;
  }

  leveling (level, attempts=5) {
    const max_zeros = {
      1: Math.floor(Math.random() * 10 + 20),
      3: Math.floor(Math.random() * 15 + 30),
      5: Math.floor(Math.random() * 20 + 45),
    }
    let _level = level;
    if (!(_level in max_zeros)) {
      _level = 3;
    }
    this.ready = false;
    while (attempts > 0) {
      let row = Math.floor(Math.random() * 9);
      let col = Math.floor(Math.random() * 9);
      while (this.grid[row * 9 + col] === 0) {
        row = Math.floor(Math.random() * 9);
        col = Math.floor(Math.random() * 9);
      }
      let cell_value = this.grid[row * 9 + col];
      this.grid[row * 9 + col] = 0;

      let copy = [...this.grid];
      let solved_count = this._solve_grid(copy);
      if (solved_count !== 1) {
        this.grid[row * 9 + col] = cell_value;
        attempts--;
      }
      if (this.grid.filter(x => x === 0).length >= max_zeros[_level]) {
        break;
      }
    }
    this.ready = true;
  }

  _check_cell (grid, row, col, number) {
    if (grid.slice(row * 9, row * 9 + 9).some(x => x === number)) {
      return false;
    } else if ([...Array(9).keys()].map(r => grid[r * 9 + col]).some(x => x === number)) {
      return false;
    } else {
      const blk_row = Math.floor(row / 3) * 3;
      const blk_col = Math.floor(col / 3) * 3;
      for (let r = blk_row; r < blk_row + 3; r++) {
        for (let c = blk_col; c < blk_col + 3; c++) {
          if (grid[r * 9 + c] === number) {
            return false;
          }
        }
      }
      return true;
    }
  }

  _solve_grid (grid) {
    let solved = 0;
    let row = 0;
    let col = 0;
    for (let i = 0; i < 81; i++) {
      row = Math.floor(i / 9);
      col = i % 9;
      if (grid[i] === 0) {
        for (let n = 1; n < 10; n++) {
          if (this._check_cell(grid, row, col, n)) {
            grid[i] = n;
            if (grid.every(n => n !== 0)) {
              solved++;
              break;
            } else {
              solved += this._solve_grid(grid);
            }
          }
        }
        break;
      }
    }
    grid[row * 9 + col] = 0;
    return solved;
  }

  static solve (sudoku) {
    if (sudoku.ready) {
      return true;
    }
    let row = 0;
    let col = 0;
    let numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9];
    for (let i = 0; i < 81; i++) {
      row = Math.floor(i / 9);
      col = i % 9;
      if (sudoku.grid[i] === 0) {
        numbers.shuffle();
        for (let number of numbers) {
          if (sudoku._check_cell(sudoku.grid, row, col, number)) {
            sudoku.grid[i] = number;
            const now = Date.now();
            while (Date.now() - now < 100) {}
            if (sudoku.filled) {
              return true;
            } else if (Sudoku.solve(sudoku)) {
              return true;
            }
          }
        }
        break;
      }
    }
    sudoku.grid[row * 9 + col] = 0;
  }

}
