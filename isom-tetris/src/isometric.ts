import * as PIXI from 'pixi.js';

const BOARD_WIDTH = 10;
const BOARD_HEIGHT = 20;
const TILE_W = 30;
const TILE_H = 15;

interface Theme {
  background: number;
  wall: number;
  floor: number;
  pieceColors: Record<string, number>;
}

const ThemeManager = {
  themes: {
    synthwave: {
      background: 0x2f3640,
      wall: 0xe1007d,
      floor: 0xb30063,
      pieceColors: {
        I: 0x3dc1d3,
        O: 0xfed330,
        T: 0xa55eea,
        L: 0xf0932b,
        J: 0x3b5998,
        S: 0x20bf6b,
        Z: 0xeb4d4b,
        BOMB: 0xffffff,
      },
    } as Theme,
    classic: {
      background: 0xddeeff,
      wall: 0x90a4ae,
      floor: 0x78909c,
      pieceColors: {
        I: 0x00ffff,
        O: 0xffff00,
        T: 0x800080,
        L: 0xffa500,
        J: 0x0000ff,
        S: 0x00ff00,
        Z: 0xff0000,
        BOMB: 0x333333,
      },
    } as Theme,
    mono: {
      background: 0x222222,
      wall: 0x555555,
      floor: 0x444444,
      pieceColors: {
        I: 0xeeeeee,
        O: 0xbbbbbb,
        T: 0xdddddd,
        L: 0xcccccc,
        J: 0xeeeeee,
        S: 0xbbbbbb,
        Z: 0xdddddd,
        BOMB: 0xff0000,
      },
    } as Theme,
  } as Record<string, Theme>,
  current: 'synthwave',
  setTheme(name: string) {
    if (this.themes[name]) {
      this.current = name;
      applyTheme();
      document.querySelectorAll('.theme-switcher button').forEach((btn) => {
        btn.classList.remove('active');
      });
      const el = document.getElementById(`theme-${name}`);
      if (el) el.classList.add('active');
    }
  },
  getPieceColor(piece: string) {
    return this.themes[this.current].pieceColors[piece];
  },
};

const TETROMINOES: Record<string, number[][]> = {
  I: [[1, 1, 1, 1]],
  O: [
    [1, 1],
    [1, 1],
  ],
  T: [
    [0, 1, 0],
    [1, 1, 1],
  ],
  L: [
    [0, 0, 1],
    [1, 1, 1],
  ],
  J: [
    [1, 0, 0],
    [1, 1, 1],
  ],
  S: [
    [0, 1, 1],
    [1, 1, 0],
  ],
  Z: [
    [1, 1, 0],
    [0, 1, 1],
  ],
};

function shade(col: number, amt: number) {
  const r = Math.min(255, Math.max(0, ((col >> 16) & 0xff) + amt));
  const g = Math.min(255, Math.max(0, ((col >> 8) & 0xff) + amt));
  const b = Math.min(255, Math.max(0, (col & 0xff) + amt));
  return (r << 16) + (g << 8) + b;
}

type Cell = string | 0;

class Piece {
  shape: number[][];
  type: string;
  x: number;
  y: number;
  constructor(type: string, shape: number[][]) {
    this.type = type;
    this.shape = shape.map((row) => [...row]);
    this.x = Math.floor(BOARD_WIDTH / 2) - Math.ceil(this.shape[0].length / 2);
    this.y = BOARD_HEIGHT - 1;
  }
}

class Game {
  app: PIXI.Application;
  board: Cell[][] = [];
  active: Piece | null = null;
  graphics = new PIXI.Graphics();
  dropTimer = 0;
  fallSpeed = 0.8;
  lines = 0;
  constructor(app: PIXI.Application) {
    this.app = app;
    this.board = Array.from({ length: BOARD_HEIGHT }, () => Array<Cell>(BOARD_WIDTH).fill(0));
    app.stage.addChild(this.graphics);
    this.spawn();
  }

  spawn() {
    const types = Object.keys(TETROMINOES);
    let type: string;
    let shape: number[][];
    if (Math.random() < 0.15) {
      type = 'BOMB';
      shape = [[1]];
    } else {
      type = types[Math.floor(Math.random() * types.length)];
      shape = TETROMINOES[type];
    }
    this.active = new Piece(type, shape);
    if (!this.isValid(this.active, this.active.x, this.active.y)) {
      showGameOver();
    }
  }

  rotate() {
    if (!this.active || this.active.type === 'BOMB') return;
    const orig = this.active.shape;
    const rotated = orig[0].map((_, i) => orig.map((row) => row[i]).reverse());
    const old = this.active.shape;
    this.active.shape = rotated;
    if (!this.isValid(this.active, this.active.x, this.active.y)) {
      this.active.shape = old;
    }
  }

  move(dx: number) {
    if (!this.active) return;
    const nx = this.active.x + dx;
    if (this.isValid(this.active, nx, this.active.y)) {
      this.active.x = nx;
    }
  }

  drop() {
    if (!this.active) return;
    while (this.isValid(this.active, this.active.x, this.active.y - 1)) {
      this.active.y -= 1;
    }
    this.lock();
  }

  tick(dt: number) {
    if (!this.active) return;
    this.dropTimer += dt;
    const step = this.fallSpeed;
    if (this.dropTimer > step) {
      this.dropTimer = 0;
      if (this.isValid(this.active, this.active.x, this.active.y - 1)) {
        this.active.y -= 1;
      } else {
        this.lock();
      }
    }
  }

  lock() {
    if (!this.active) return;
    const p = this.active;
    p.shape.forEach((row, r) => {
      row.forEach((val, c) => {
        if (val) {
          const bx = p.x + c;
          const by = p.y - r;
          if (bx >= 0 && bx < BOARD_WIDTH && by >= 0 && by < BOARD_HEIGHT) {
            this.board[by][bx] = p.type;
          }
        }
      });
    });
    if (p.type === 'BOMB') {
      this.bomb(p.x, p.y);
    }
    this.clearLines();
    this.spawn();
  }

  bomb(x: number, y: number) {
    const radius = 2;
    for (let i = -radius; i <= radius; i++) {
      for (let j = -radius; j <= radius; j++) {
        const bx = x + j;
        const by = y - i;
        if (bx >= 0 && bx < BOARD_WIDTH && by >= 0 && by < BOARD_HEIGHT) {
          if (Math.sqrt(i * i + j * j) <= radius) {
            this.board[by][bx] = 0;
          }
        }
      }
    }
  }

  clearLines() {
    let lines = 0;
    for (let r = 0; r < BOARD_HEIGHT; r++) {
      if (this.board[r].every((c) => c !== 0)) {
        this.board.splice(r, 1);
        this.board.push(Array<Cell>(BOARD_WIDTH).fill(0));
        lines++;
      }
    }
    if (lines > 0) {
      this.lines += lines;
      updateLines(this.lines);
      this.fallSpeed = Math.max(0.1, this.fallSpeed - 0.05 * lines);
    }
  }

  isValid(piece: Piece, nx: number, ny: number) {
    for (let r = 0; r < piece.shape.length; r++) {
      for (let c = 0; c < piece.shape[r].length; c++) {
        if (piece.shape[r][c]) {
          const bx = nx + c;
          const by = ny - r;
          if (bx < 0 || bx >= BOARD_WIDTH || by < 0) return false;
          if (by < BOARD_HEIGHT && this.board[by][bx]) return false;
        }
      }
    }
    return true;
  }

  render() {
    this.graphics.clear();
    const theme = ThemeManager.themes[ThemeManager.current];
    this.app.renderer.background.color = theme.background;
    const offsetX = this.app.screen.width / 2;
    const offsetY = 60;
    const drawCell = (c: number, r: number, color: number) => {
      const posX = offsetX + (c - r) * TILE_W;
      const posY = offsetY + (c + r) * TILE_H;
      const top = shade(color, 40);
      const left = shade(color, -20);
      const right = shade(color, -40);
      // top
      this.graphics.beginFill(top);
      this.graphics.moveTo(posX, posY - TILE_H);
      this.graphics.lineTo(posX + TILE_W, posY);
      this.graphics.lineTo(posX, posY + TILE_H);
      this.graphics.lineTo(posX - TILE_W, posY);
      this.graphics.endFill();
      // left
      this.graphics.beginFill(left);
      this.graphics.moveTo(posX - TILE_W, posY);
      this.graphics.lineTo(posX, posY + TILE_H);
      this.graphics.lineTo(posX, posY + TILE_H * 2);
      this.graphics.lineTo(posX - TILE_W, posY + TILE_H);
      this.graphics.endFill();
      // right
      this.graphics.beginFill(right);
      this.graphics.moveTo(posX + TILE_W, posY);
      this.graphics.lineTo(posX, posY + TILE_H);
      this.graphics.lineTo(posX, posY + TILE_H * 2);
      this.graphics.lineTo(posX + TILE_W, posY + TILE_H);
      this.graphics.endFill();
    };

    for (let r = 0; r < BOARD_HEIGHT; r++) {
      for (let c = 0; c < BOARD_WIDTH; c++) {
        const cell = this.board[r][c];
        if (cell) {
          const col = ThemeManager.getPieceColor(cell);
          drawCell(c, BOARD_HEIGHT - 1 - r, col);
        }
      }
    }

    if (this.active) {
      this.active.shape.forEach((row, r) => {
        row.forEach((val, c) => {
          if (val) {
            const col = ThemeManager.getPieceColor(this.active!.type);
            const cx = this.active!.x + c;
            const cy = this.active!.y - r;
            drawCell(cx, BOARD_HEIGHT - 1 - cy, col);
          }
        });
      });
    }
  }
}

const app = new PIXI.Application({
  width: window.innerWidth,
  height: window.innerHeight,
  backgroundColor: 0x000000,
  antialias: true,
});
(document.getElementById('game-container') as HTMLElement).appendChild(app.view as HTMLCanvasElement);

let game = new Game(app);

function resize() {
  app.renderer.resize(window.innerWidth, window.innerHeight);
}
window.addEventListener('resize', resize);

const controls = {
  left: document.getElementById('left-btn')!,
  right: document.getElementById('right-btn')!,
  rotate: document.getElementById('rotate-btn')!,
  drop: document.getElementById('drop-btn')!,
  down: document.getElementById('down-btn')!,
};

controls.left.addEventListener('click', () => game.move(-1));
controls.right.addEventListener('click', () => game.move(1));
controls.rotate.addEventListener('click', () => game.rotate());
controls.drop.addEventListener('click', () => game.drop());
controls.down.addEventListener('mousedown', () => (game.fallSpeed = 0.05));
controls.down.addEventListener('mouseup', () => (game.fallSpeed = 0.8));
controls.down.addEventListener('mouseleave', () => (game.fallSpeed = 0.8));
controls.down.addEventListener('touchstart', (e) => {
  e.preventDefault();
  game.fallSpeed = 0.05;
});
controls.down.addEventListener('touchend', () => (game.fallSpeed = 0.8));

window.addEventListener('keydown', (e) => {
  switch (e.key) {
    case 'ArrowLeft':
    case 'a':
    case 'A':
      game.move(-1);
      break;
    case 'ArrowRight':
    case 'd':
    case 'D':
      game.move(1);
      break;
    case 'ArrowUp':
    case 'w':
    case 'W':
      game.rotate();
      break;
    case 'ArrowDown':
    case 's':
    case 'S':
      game.fallSpeed = 0.05;
      break;
    case ' ':
      game.drop();
      break;
  }
});
window.addEventListener('keyup', (e) => {
  if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') {
    game.fallSpeed = 0.8;
  }
});

document.getElementById('restart-button')?.addEventListener('click', () => {
  document.getElementById('game-over-modal')!.style.display = 'none';
  game = new Game(app);
});

function showGameOver() {
  document.getElementById('game-over-modal')!.style.display = 'block';
}

function updateLines(v: number) {
  const el = document.getElementById('lines');
  if (el) el.textContent = v.toString();
}

function applyTheme() {
  const theme = ThemeManager.themes[ThemeManager.current];
  (document.body as HTMLElement).style.backgroundColor = `#${theme.background.toString(16).padStart(6, '0')}`;
  game.render();
}

ThemeManager.setTheme('synthwave');

document.getElementById('theme-synthwave')?.addEventListener('click', () => ThemeManager.setTheme('synthwave'));
document.getElementById('theme-classic')?.addEventListener('click', () => ThemeManager.setTheme('classic'));
document.getElementById('theme-mono')?.addEventListener('click', () => ThemeManager.setTheme('mono'));

let last = 0;
app.ticker.add(() => {
  const now = app.ticker.lastTime / 1000;
  const dt = now - last;
  last = now;
  game.tick(dt);
  game.render();
});

