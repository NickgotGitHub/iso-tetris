// @ts-nocheck
import * as PIXI from "pixi.js";
export const app = new PIXI.Application({
    width: window.innerWidth,
    height: window.innerHeight,
    backgroundColor: 0x1a1a1a,
    resizeTo: window
});

document.body.appendChild(app.view);

export const TILE_SIZE = 32;
export const BOARD_WIDTH = 10;
export const BOARD_HEIGHT = 20;

export const board = Array.from({ length: BOARD_HEIGHT }, () => Array(BOARD_WIDTH).fill(0));
