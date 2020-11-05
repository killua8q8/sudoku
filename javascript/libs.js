'use strict';

Array.prototype.shuffle = function () {
  for (let i = 0; i < this.length; i++) {
    let a = Math.floor(Math.random() * Math.floor(9));
    let b = Math.floor(Math.random() * Math.floor(9));
    let temp = this[a];
    this[a] = this[b]
    this[b] = temp;
  }
};

const digits = ['', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '*️⃣'];

const newRenderWorker = (onmessage) => {
  function renderWorker () {
    let sudokuGrid = undefined;
    self.addEventListener('message', (e) => {
      sudokuGrid = new Int32Array(e.data);
      setInterval(() => {
        [...Array(81).keys()].forEach(idx => {
          const row = Math.floor(idx / 9);
          const col = idx % 9;
          self.postMessage({ row, col, val: Atomics.load(sudokuGrid, idx) });
        });
      }, 1000 / 10);
    });
  }
  const worker = new Worker(URL.createObjectURL(new Blob([`(${renderWorker.toString()})()`], { type: 'text/javascript' })));
  worker.onmessage = onmessage;
  return worker;
};

const newGridSolverWorker = (onmessage) => {
  function solverWorker () {
    Array.prototype.shuffle = function () {
      for (let i = 0; i < this.length; i++) {
        let a = Math.floor(Math.random() * Math.floor(9));
        let b = Math.floor(Math.random() * Math.floor(9));
        let temp = this[a];
        this[a] = this[b]
        this[b] = temp;
      }
    };
    let sudokuGrid = undefined;
    const check_cell = (grid, row, col, number) => {
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
    };
    const solve = (grid) => {
      let row = 0;
      let col = 0;
      let numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9];
      for (let i = 0; i < 81; i++) {
        row = Math.floor(i / 9);
        col = i % 9;
        if (Atomics.load(grid, i) === 0) {
          numbers.shuffle();
          for (let number of numbers) {
            if (check_cell(grid, row, col, number)) {
              Atomics.store(grid, i, number);
              const now = Date.now();
              while (Date.now() - now < 10) {}
              if (grid.every(x => x !== 0)) {
                return true;
              } else if (solve(grid)) {
                return true;
              }
            }
          }
          break;
        }
      }
      Atomics.store(grid, row * 9 + col, 0);
    };
    self.addEventListener('message', (e) => {
      sudokuGrid = new Int32Array(e.data);
      solve(sudokuGrid);
      self.postMessage({ done: true });
    });
  }
  const worker = new Worker(URL.createObjectURL(new Blob([`(${solverWorker.toString()})()`], { type: 'text/javascript' })));
  worker.onmessage = onmessage;
  return worker;
};
