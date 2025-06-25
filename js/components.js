const Position = (x, y) => ({ name: 'position', x, y });
const Renderable = (sprite) => ({ name: 'renderable', sprite });
const Tetromino = (shape, type) => ({ name: 'tetromino', shape, type });
const Velocity = (vx, vy) => ({ name: 'velocity', vx, vy });
const Controllable = () => ({ name: 'controllable' });
