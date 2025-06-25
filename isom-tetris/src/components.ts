// @ts-nocheck
export const Position = (x, y) => ({ name: 'position', x, y });
export const Renderable = (sprite) => ({ name: 'renderable', sprite });
export const Tetromino = (shape, type) => ({ name: 'tetromino', shape, type });
export const Velocity = (vx, vy) => ({ name: 'velocity', vx, vy });
export const Controllable = () => ({ name: 'controllable' });
