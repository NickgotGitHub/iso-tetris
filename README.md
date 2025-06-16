# Isometric Tetris (PixiJS)

This project is a starter template for building an isometric Tetris game using **TypeScript** and **PixiJS**. It includes touch controls via **Hammer.js** and is structured for easy extension with levels, maps and other game systems.

## Tech Stack
- **PixiJS** for WebGL rendering
- **Hammer.js** for touch gestures
- **TypeScript** compiled to plain JavaScript

## Development
Install dependencies:
```bash
npm install
```

Build the project:
```bash
npm run build
```
which simply runs `tsc` to compile files to the `dist/` folder.

Start a development server:
```bash
bun run dev:web
```
This builds the project and serves `index.html` on a local web server for easy testing.

Open `index.html` in a browser to test the game. The basic implementation draws an isometric board and allows swipe gestures to rotate or move the current piece.

## Folder Structure
```
assets/            Sprite sheets and other assets
src/               TypeScript source
  main.ts          Game entry point
index.html         Web page that loads the game
```

This codebase is intentionally simple. It serves as a foundation for experimenting with additional features like map variety, level progression and mobile deployment using solutions such as Capacitor.
