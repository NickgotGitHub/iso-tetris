# Isometric Tetris

This project is a work in progress implementation of an isometric Tetris game written in **TypeScript** using **PixiJS**. It targets mobile devices with touch controls and can be bundled as a hybrid app using Capacitor.

## Features

- PixiJS WebGL renderer for fast 2D graphics
- Touch gestures handled with Hammer.js
- Simple level system loaded from JSON
- Example sprite atlas included in `assets/`

## Development

Install dependencies with npm and start the Vite dev server:

```bash
npm install
npm run start
```

The entry point is `src/main.ts` and the dev server will serve `index.html`.

## Building

```
npm run build
```

This will output a production build in the `dist/` folder.
