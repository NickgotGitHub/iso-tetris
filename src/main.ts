import * as PIXI from 'pixi.js';
import Hammer from 'hammerjs';

const WALL_WIDTH = 10;
const WALL_HEIGHT = 20;
const BLOCK_SIZE = 60;
const ISO_MATRIX = [
  [0.5, -0.5],
  [0.25, 0.25, 0],
];

function toIsometric(x: number, y: number, z: number) {
  const isoX = ISO_MATRIX[0][0] * x + ISO_MATRIX[0][1] * y;
  const isoY = ISO_MATRIX[1][0] * x + ISO_MATRIX[1][1] * y + ISO_MATRIX[1][2] * z;
  return { x: isoX, y: isoY };
}

const shapes = [
  [[1, 1, 1], [0, 1, 0]],
  [[0, 2, 2], [2, 2, 0]],
  [[3, 3, 0], [0, 3, 3]],
  [[4, 0, 0], [4, 4, 4]],
  [[0, 0, 5], [5, 5, 5]],
  [[6, 6], [6, 6]],
  [[7, 7, 7, 7]],
];

type Piece = number[][];

class Game {
  app: PIXI.Application;
  board: number[][];
  piece: Piece;
  pieceX: number = 3;
  pieceY: number = 0;
  textures: Record<number, PIXI.Texture> = {};
  container: PIXI.Container;
  fallElapsed = 0;
  fallSpeed = 0.5; // seconds

  constructor() {
    this.app = new PIXI.Application({ width: window.innerWidth, height: window.innerHeight, backgroundColor: 0xc6284e });
    document.body.appendChild(this.app.view);

    this.container = new PIXI.Container();
    this.container.x = this.app.renderer.width / 2;
    this.container.y = this.app.renderer.height / 1.5;
    this.app.stage.addChild(this.container);

    this.loadLevel('/levels/level1.json').then(() => {
      this.piece = this.randomPiece();
      this.loadTextures().then(() => {
        this.app.ticker.add((delta) => this.update(delta / 60));
      });
    });

    this.setupInput();
  }

  randomPiece(): Piece {
    const idx = Math.floor(Math.random() * shapes.length);
    return shapes[idx].map(row => row.slice());
  }

  async loadTextures() {
    const baseTexture = await PIXI.Assets.load('/assets/sprite_sheet.png');
    const frameWidth = baseTexture.width / 8;
    for (let i = 0; i < 8; i++) {
      this.textures[i + 1] = new PIXI.Texture(baseTexture, new PIXI.Rectangle(i * frameWidth, 0, frameWidth, baseTexture.height));
    }
  }

  async loadLevel(path: string) {
    const data = await (await fetch(path)).json();
    this.board = data.board;
    this.fallSpeed = data.speed ?? this.fallSpeed;
  }

  setupInput() {
    const hammer = new Hammer(document.body);
    hammer.get('swipe').set({ direction: Hammer.DIRECTION_ALL });

    hammer.on('swipeleft', () => this.movePiece(-1, 0));
    hammer.on('swiperight', () => this.movePiece(1, 0));
    hammer.on('swipedown', () => {
      while (this.validSpace(this.pieceX, this.pieceY + 1)) this.pieceY++;
      this.placePiece();
    });
    hammer.on('swipeup', () => this.rotatePiece());
  }

  movePiece(dx: number, dy: number) {
    if (this.validSpace(this.pieceX + dx, this.pieceY + dy)) {
      this.pieceX += dx;
      this.pieceY += dy;
    }
  }

  rotatePiece() {
    const rotated: Piece = this.piece[0].map((_, i) => this.piece.map(row => row[i]).reverse());
    const old = this.piece;
    this.piece = rotated;
    if (!this.validSpace(this.pieceX, this.pieceY)) {
      this.piece = old;
    }
  }

  validSpace(px: number, py: number) {
    for (let y = 0; y < this.piece.length; y++) {
      for (let x = 0; x < this.piece[y].length; x++) {
        if (!this.piece[y][x]) continue;
        const bx = px + x;
        const by = py + y;
        if (bx < 0 || bx >= WALL_WIDTH || by >= WALL_HEIGHT) return false;
        if (by >= 0 && this.board[by][bx]) return false;
      }
    }
    return true;
  }

  placePiece() {
    for (let y = 0; y < this.piece.length; y++) {
      for (let x = 0; x < this.piece[y].length; x++) {
        if (this.piece[y][x]) {
          const bx = this.pieceX + x;
          const by = this.pieceY + y;
          if (by >= 0) this.board[by][bx] = this.piece[y][x];
        }
      }
    }
    this.clearLines();
    this.piece = this.randomPiece();
    this.pieceX = 3;
    this.pieceY = 0;
    if (!this.validSpace(this.pieceX, this.pieceY)) {
      console.log('Game Over');
      this.app.ticker.stop();
    }
  }

  clearLines() {
    for (let y = WALL_HEIGHT - 1; y >= 0; y--) {
      if (this.board[y].every(v => v !== 0)) {
        for (let pull = y; pull > 0; pull--) {
          this.board[pull] = this.board[pull - 1].slice();
        }
        this.board[0] = Array(WALL_WIDTH).fill(0);
        y++;
      }
    }
  }

  update(dt: number) {
    this.fallElapsed += dt;
    if (this.fallElapsed >= this.fallSpeed) {
      this.fallElapsed = 0;
      if (this.validSpace(this.pieceX, this.pieceY + 1)) {
        this.pieceY += 1;
      } else {
        this.placePiece();
      }
    }
    this.draw();
  }

  draw() {
    this.container.removeChildren();

    const tempBoard = this.getTempBoard();
    for (let y = WALL_HEIGHT - 1; y >= 0; y--) {
      for (let x = WALL_WIDTH - 1; x >= 0; x--) {
        const val = tempBoard[y][x];
        if (!val) continue;
        const { x: isoX, y: isoY } = toIsometric(x * BLOCK_SIZE, 0, y * (BLOCK_SIZE / 2));
        const sprite = new PIXI.Sprite(this.textures[val]);
        sprite.width = BLOCK_SIZE;
        sprite.height = BLOCK_SIZE;
        sprite.x = isoX;
        sprite.y = isoY - y * (BLOCK_SIZE / 2);
        this.container.addChild(sprite);
      }
    }
  }

  getTempBoard() {
    const board = this.board.map(row => row.slice());
    for (let y = 0; y < this.piece.length; y++) {
      for (let x = 0; x < this.piece[y].length; x++) {
        if (this.piece[y][x]) {
          const bx = this.pieceX + x;
          const by = this.pieceY + y;
          if (by >= 0 && by < WALL_HEIGHT && bx >= 0 && bx < WALL_WIDTH) {
            board[by][bx] = this.piece[y][x];
          }
        }
      }
    }
    return board;
  }
}

window.addEventListener('load', () => new Game());
