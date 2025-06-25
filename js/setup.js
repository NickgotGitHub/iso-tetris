const app = new PIXI.Application({
    width: window.innerWidth,
    height: window.innerHeight,
    backgroundColor: 0x1a1a1a,
    resizeTo: window
});

document.body.appendChild(app.view);

const TILE_SIZE = 32;
const BOARD_WIDTH = 10;
const BOARD_HEIGHT = 20;

const board = Array.from({ length: BOARD_HEIGHT }, () => Array(BOARD_WIDTH).fill(0));
