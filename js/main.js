const linesEl = document.getElementById('lines');
const gameOverModal = document.getElementById('game-over-modal');
const restartButton = document.getElementById('restart-button');

world.addSystem(renderSystem);
world.addSystem(gravitySystem);

app.ticker.add(delta => {
    world.update(delta);
});

const ThemeManager = {
    themes: {
        'synthwave': {
            background: 0x2f3640,
            pieceColors: {
                'I': 0x3dc1d3, 'O': 0xfed330, 'T': 0xa55eea, 'L': 0xf0932b,
                'J': 0x3b5998, 'S': 0x20bf6b, 'Z': 0xeb4d4b
            }
        },
        'classic': {
            background: 0xddeeff,
            pieceColors: {
                'I': 0x00ffff, 'O': 0xffff00, 'T': 0x800080, 'L': 0xffa500,
                'J': 0x0000ff, 'S': 0x00ff00, 'Z': 0xff0000
            }
        },
        'mono': {
            background: 0x222222,
            pieceColors: {
                'I': 0xeeeeee, 'O': 0xbbbbbb, 'T': 0xdddddd, 'L': 0xcccccc,
                'J': 0xeeeeee, 'S': 0xbbbbbb, 'Z': 0xdddddd
            }
        }
    },
    currentTheme: 'synthwave',
    setTheme(name) {
        this.currentTheme = name;
        app.renderer.backgroundColor = this.themes[name].background;
        document.querySelectorAll('.theme-switcher button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.getElementById(`theme-${name}`).classList.add('active');
    }
};

document.getElementById('theme-synthwave').addEventListener('click', () => ThemeManager.setTheme('synthwave'));
document.getElementById('theme-classic').addEventListener('click', () => ThemeManager.setTheme('classic'));
document.getElementById('theme-mono').addEventListener('click', () => ThemeManager.setTheme('mono'));

restartButton.addEventListener('click', () => {
    gameOverModal.style.display = 'none';
});

ThemeManager.setTheme('synthwave');

const createTetromino = (shape, type) => {
    const entity = world.createEntity();
    const color = ThemeManager.themes[ThemeManager.currentTheme].pieceColors[type];
    const graphics = new PIXI.Graphics();
    graphics.beginFill(color);
    graphics.drawRect(0, 0, TILE_SIZE, TILE_SIZE);
    graphics.endFill();

    world.addComponent(entity, Position(0, 0));
    world.addComponent(entity, Renderable(new PIXI.Sprite(app.renderer.generateTexture(graphics))));
    world.addComponent(entity, Tetromino(shape, type));
    world.addComponent(entity, Velocity(0, 1));

    app.stage.addChild(entity.components.renderable.sprite);
};

createTetromino([[1, 1, 1, 1]], 'I');
