import * as PIXI from 'pixi.js';
import Hammer from 'hammerjs';

// Application setup
const app = new PIXI.Application({
    backgroundColor: 0xc6284e,
    resizeTo: window
});
document.body.appendChild(app.view);

// grid constants
const WALL_WIDTH = 10;
const WALL_HEIGHT = 20;
const BLOCK_SIZE = 30; // smaller blocks for mobile
const ISO_MATRIX = [ [0.5, -0.5], [0.25, 0.25, 0] ];

function toIsometric(x:number, y:number, z:number){
    const isoX = ISO_MATRIX[0][0] * x + ISO_MATRIX[0][1] * y;
    const isoY = ISO_MATRIX[1][0] * x + ISO_MATRIX[1][1] * y + ISO_MATRIX[1][2] * z;
    return {x: isoX, y: isoY};
}

// board and shapes
const board:number[][] = [];
for(let y=0;y<WALL_HEIGHT;y++){
    board[y] = new Array(WALL_WIDTH).fill(0);
}

const shapes:number[][][] = [
    [[1,1,1],[0,1,0]],
    [[0,2,2],[2,2,0]],
    [[3,3,0],[0,3,3]],
    [[4,0,0],[4,4,4]],
    [[0,0,5],[5,5,5]],
    [[6,6],[6,6]],
    [[7,7,7,7]]
];

let currentPiece = shapes[Math.floor(Math.random()*shapes.length)];
let currentX = 3;
let currentY = 0;
let time = 0;
let fallSpeed = 500; // ms

// load sprites
const spriteSheet = PIXI.Texture.from('assets/sprite_sheet.png');
const blockTextures: {[key:number]: PIXI.Texture} = {};
for(let i=0;i<8;i++){
    const frame = new PIXI.Rectangle(i * spriteSheet.width / 8, 0, spriteSheet.width / 8, spriteSheet.height);
    blockTextures[i+1] = new PIXI.Texture({ source: spriteSheet.baseTexture, frame });
}

const container = new PIXI.Container();
container.position.set(window.innerWidth/2.5, window.innerHeight/1.5);
app.stage.addChild(container);

function drawBoard(tempBoard:number[][]){
    container.removeChildren();
    for(let y=WALL_HEIGHT-1; y>=0; y--){
        for(let x=WALL_WIDTH-1; x>=0; x--){
            const blockValue = tempBoard[WALL_HEIGHT-1 - y][x];
            if(blockValue){
                const {x:isoX, y:isoY} = toIsometric(x*BLOCK_SIZE,0,y*BLOCK_SIZE/2);
                const sprite = new PIXI.Sprite(blockTextures[blockValue]);
                sprite.width = BLOCK_SIZE;
                sprite.height = BLOCK_SIZE;
                sprite.x = isoX;
                sprite.y = isoY - y*(BLOCK_SIZE/2);
                container.addChild(sprite);
            }
        }
    }
}

function getTemporaryBoard():number[][]{
    const temp = board.map(row=>row.slice());
    for(let y=0; y<currentPiece.length; y++){
        for(let x=0; x<currentPiece[y].length; x++){
            if(currentPiece[y][x]){
                const bx = currentX + x;
                const by = currentY + y;
                if(by >= 0 && by < WALL_HEIGHT && bx >=0 && bx < WALL_WIDTH){
                    temp[by][bx] = currentPiece[y][x];
                }
            }
        }
    }
    return temp;
}

function rotate(shape:number[][]){
    return shape[0].map((_,i)=> shape.map(row=> row[i]).reverse());
}

function validSpace(shape:number[][], posX:number, posY:number){
    for(let y=0; y<shape.length; y++){
        for(let x=0; x<shape[y].length; x++){
            if(shape[y][x]){
                const bx = posX + x;
                const by = posY + y;
                if(bx<0 || bx>=WALL_WIDTH || by>=WALL_HEIGHT) return false;
                if(by>=0 && board[by][bx]) return false;
            }
        }
    }
    return true;
}

function placePiece(){
    for(let y=0; y<currentPiece.length; y++){
        for(let x=0; x<currentPiece[y].length; x++){
            if(currentPiece[y][x]){
                board[currentY + y][currentX + x] = currentPiece[y][x];
            }
        }
    }
}

function tick(ticker: PIXI.Ticker){
    const delta = ticker.deltaTime;
    time += delta;
    if(time>fallSpeed){
        time=0;
        if(validSpace(currentPiece,currentX,currentY+1)){
            currentY +=1;
        }else{
            placePiece();
            currentPiece = shapes[Math.floor(Math.random()*shapes.length)];
            currentX = 3; currentY = 0;
        }
    }
    drawBoard(getTemporaryBoard());
}

app.ticker.add(tick);

// Touch controls using Hammer.js
const hammer = new Hammer.Manager(app.view);
hammer.add(new Hammer.Swipe({ direction: Hammer.DIRECTION_ALL, threshold: 20 }));
let pan = new Hammer.Pan({ direction: Hammer.DIRECTION_ALL, threshold: 10 });
hammer.add(pan);

hammer.on('swipeup',()=>{
    const rotated = rotate(currentPiece);
    if(validSpace(rotated, currentX, currentY)) currentPiece = rotated;
});
hammer.on('swipedown',()=>{
    while(validSpace(currentPiece, currentX, currentY+1)) currentY++;
});

tapArea(app.view).addEventListener('click', (event)=>{
    // simple left/right tap
});

hammer.on('panleft',()=>{
    if(validSpace(currentPiece,currentX-1,currentY)) currentX--;
});
hammer.on('panright',()=>{
    if(validSpace(currentPiece,currentX+1,currentY)) currentX++;
});

function tapArea(canvas:HTMLCanvasElement){
    return canvas;
}
