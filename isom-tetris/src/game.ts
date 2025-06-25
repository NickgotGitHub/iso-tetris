// @ts-nocheck
export function initGame() {
        // ===================================================================
        // === THEME MANAGER ===
        // ===================================================================
        const ThemeManager = {
            themes: {
                'synthwave': {
                    background: 0x2f3640,
                    wall: 0xE1007D,
                    floor: 0xB30063,
                    pieceColors: {
                        'I': 0x3dc1d3, 'O': 0xfed330, 'T': 0xa55eea, 'L': 0xf0932b,
                        'J': 0x3b5998, 'S': 0x20bf6b, 'Z': 0xeb4d4b, 'BOMB': 0xffffff
                    }
                },
                'classic': {
                    background: 0xddeeff,
                    wall: 0x90a4ae,
                    floor: 0x78909c,
                    pieceColors: {
                        'I': 0x00ffff, 'O': 0xffff00, 'T': 0x800080, 'L': 0xffa500,
                        'J': 0x0000ff, 'S': 0x00ff00, 'Z': 0xff0000, 'BOMB': 0x333333
                    }
                },
                'mono': {
                    background: 0x222222,
                    wall: 0x555555,
                    floor: 0x444444,
                    pieceColors: {
                        'I': 0xeeeeee, 'O': 0xbbbbbb, 'T': 0xdddddd, 'L': 0xcccccc,
                        'J': 0xeeeeee, 'S': 0xbbbbbb, 'Z': 0xdddddd, 'BOMB': 0xff0000
                    }
                }
            },
            currentThemeName: 'synthwave',
            
            setTheme(name) {
                if (this.themes[name]) {
                    this.currentThemeName = name;
                    applyCurrentTheme();
                    
                    document.querySelectorAll('.theme-switcher button').forEach(btn => {
                        btn.classList.remove('active');
                    });
                    document.getElementById(`theme-${name}`).classList.add('active');
                }
            },
            
            get(key) {
                return this.themes[this.currentThemeName][key];
            },

            getPieceColor(pieceType) {
                return this.themes[this.currentThemeName].pieceColors[pieceType];
            }
        };


        // ===================================================================
        // === MODULAR POWER-UP ARCHITECTURE (MPA) ===
        // ===================================================================

        const PowerUpManager = {
            registry: {},
            activeAnimations: [],
            register(powerUp) { this.registry[powerUp.type] = powerUp; },
            get(type) { return this.registry[type]; },
            activate(type, x, y, game) {
                const powerUp = this.get(type);
                if (powerUp && powerUp.activate) powerUp.activate(x, y, game);
            },
            updateAnimations(deltaTime, game) {
                for (let i = this.activeAnimations.length - 1; i >= 0; i--) {
                    const anim = this.activeAnimations[i];
                    anim.timer += deltaTime;
                    const progress = Math.min(1, anim.timer / anim.duration);
                    anim.update(progress, game.camera, game.originalCameraPos, game.cameraFlashMesh);
                    if (progress >= 1) {
                        anim.onComplete();
                        this.activeAnimations.splice(i, 1);
                    }
                }
            }
        };

        const BOMB_POWERUP = {
            type: 'BOMB',
            texture: null, // Texture will be created dynamically
            createTexture() {
                const canvas = document.createElement('canvas');
                canvas.width = 16; canvas.height = 16;
                const context = canvas.getContext('2d');
                context.fillStyle = ThemeManager.getPieceColor('Z'); // Use a base color from theme
                context.fillRect(0, 0, 16, 16);
                context.fillStyle = '#111';
                const p = 2;
                context.fillRect(p*2, p*1, p*4, p*1); context.fillRect(p*1, p*2, p*6, p*1);
                context.fillRect(p*2, p*3, p*4, p*2); context.fillRect(p*3, p*5, p*2, p*1);
                context.fillRect(p*1, p*6, p*2, p*1); context.fillRect(p*5, p*6, p*2, p*1);
                const texture = new THREE.CanvasTexture(canvas);
                texture.magFilter = THREE.NearestFilter;
                texture.minFilter = THREE.NearestFilter;
                this.texture = texture;
            },
            activate(x, y, game) {
                const radius = 2;
                for (let i = -radius; i <= radius; i++) {
                    for (let j = -radius; j <= radius; j++) {
                        const checkX = x + j;
                        const checkY = y + i;
                        if (checkX >= 0 && checkX < BOARD_WIDTH && checkY >= 0 && checkY < BOARD_HEIGHT) {
                            if (Math.sqrt(i*i + j*j) <= radius && game.gameBoard[checkY][checkX] !== 0) {
                                game.gameBoard[checkY][checkX] = 0;
                            }
                        }
                    }
                }
                const explosionSphere = new THREE.Mesh( new THREE.SphereGeometry(1, 32, 32), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true }));
                const startPos = getCubePosition(x, y);
                explosionSphere.position.set(startPos.x, startPos.y, startPos.z);
                game.scene.add(explosionSphere);
                PowerUpManager.activeAnimations.push({
                    timer: 0, duration: 0.4, update: (p) => { explosionSphere.scale.setScalar(p * (radius + 1) * 2); explosionSphere.material.opacity = 1.0 - p; },
                    onComplete: () => { game.scene.remove(explosionSphere); this.startCameraShake(game); }
                });
            },
            startCameraShake(game) {
                PowerUpManager.activeAnimations.push({
                    timer: 0, duration: 0.3, update: (p, cam, origPos, flash) => {
                        const intensity = 1 - p;
                        cam.position.x = origPos.x + (Math.random() - 0.5) * intensity;
                        cam.position.y = origPos.y + (Math.random() - 0.5) * intensity;
                        flash.material.opacity = (p < 0.5 ? p * 2 : (1 - p) * 2) * 0.8;
                    }, onComplete: () => {
                        game.camera.position.copy(game.originalCameraPos); game.cameraFlashMesh.material.opacity = 0;
                        game.applyGravity(); game.updateLandedVisuals(); game.spawnNewPiece();
                    }
                });
            }
        };
        PowerUpManager.register(BOMB_POWERUP);
        

        // === GAME SETUP ===
        const BOARD_WIDTH = 10; const BOARD_HEIGHT = 20; const CUBE_SIZE = 1;
        let scene, camera, renderer, composer, clock, originalCameraPos, cameraFlashMesh;
        let gameBoard = createEmptyBoard();
        let landedCubesMesh = null;
        let activePieceMesh = null; let ghostPieceMesh = null; let activePiece = null;
        let score = 0; let linesCleared = 0; let lastScore = -1;
        let gameState = 'PLAYING';
        let fallSpeed = 1.2; let fallSpeedMultiplier = 1.0;
        let animationTimer = 0; const LINE_CLEAR_ANIMATION_DURATION = 0.3; const SPAWN_ANIMATION_DURATION = 0.4;
        const LERP_FACTOR = 0.3;

        // 3D Text
        let scoreFont = null;
        let scoreTextMesh = null;
        const fontLoader = new THREE.FontLoader();

        // Camera rotation variables
        let isCameraAnimating = false;
        let currentCameraViewIndex = 0;
        const cameraViews = [
            { position: new THREE.Vector3(15, 25, 15), lookAt: new THREE.Vector3(0, 9, 0) }, // SE
            { position: new THREE.Vector3(-15, 25, 15), lookAt: new THREE.Vector3(0, 9, 0) }, // SW
            { position: new THREE.Vector3(-15, 25, -15), lookAt: new THREE.Vector3(0, 9, 0) },// NW
            { position: new THREE.Vector3(15, 25, -15), lookAt: new THREE.Vector3(0, 9, 0) }  // NE
        ];

        const TETROMINOES = {
            'I': { shape: [[1, 1, 1, 1]] }, 'O': { shape: [[1, 1], [1, 1]] },
            'T': { shape: [[0, 1, 0], [1, 1, 1]] }, 'L': { shape: [[0, 0, 1], [1, 1, 1]] },
            'J': { shape: [[1, 0, 0], [1, 1, 1]] }, 'S': { shape: [[0, 1, 1], [1, 1, 0]] },
            'Z': { shape: [[1, 1, 0], [0, 1, 1]] }
        };

        const linesElement = document.getElementById('lines');
        const gameOverModal = document.getElementById('game-over-modal');
        const restartButton = document.getElementById('restart-button');
        let floor;

        function createEmptyBoard() {
            return Array.from({ length: BOARD_HEIGHT }, () => Array(BOARD_WIDTH).fill(0));
        }

        // === SCENE INITIALIZATION ===
        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color();
            clock = new THREE.Clock();

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            document.body.appendChild(renderer.domElement);

            const aspect = window.innerWidth / window.innerHeight;
            const d = 15;
            camera = new THREE.OrthographicCamera(-d * aspect, d * aspect, d, -d, 1, 1000);
            camera.position.copy(cameraViews[currentCameraViewIndex].position);
            camera.lookAt(cameraViews[currentCameraViewIndex].lookAt);
            originalCameraPos = camera.position.clone();

            const flashGeometry = new THREE.PlaneGeometry(2, 2);
            const flashMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0 });
            cameraFlashMesh = new THREE.Mesh(flashGeometry, flashMaterial);
            cameraFlashMesh.position.z = -1;
            camera.add(cameraFlashMesh);

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
            scene.add(ambientLight);

            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
            directionalLight.position.set(-20, 30, 20);
            directionalLight.castShadow = true;
            directionalLight.shadow.mapSize.width = 2048; directionalLight.shadow.mapSize.height = 2048;
            directionalLight.shadow.camera.left = -20; directionalLight.shadow.camera.right = 20;
            directionalLight.shadow.camera.top = 20; directionalLight.shadow.camera.bottom = -20;
            scene.add(directionalLight);
            
            const wallMaterial = new THREE.MeshStandardMaterial({ roughness: 0.8 });
            floor = new THREE.Mesh(new THREE.PlaneGeometry(BOARD_WIDTH * 2.5, BOARD_WIDTH * 2.5), wallMaterial.clone());
            floor.rotation.x = -Math.PI / 2;
            floor.position.y = -CUBE_SIZE;
            floor.receiveShadow = true;
            scene.add(floor);

            composer = new THREE.EffectComposer(renderer);
            composer.addPass(new THREE.RenderPass(scene, camera));
            const saoPass = new THREE.SAOPass(scene, camera, false, true);
            saoPass.params.saoBias = 0.5; saoPass.params.saoIntensity = 0.0015;
            saoPass.params.saoScale = 200; saoPass.params.saoKernelRadius = 30;
            composer.addPass(saoPass);
            const ExposureShader = {
                uniforms: { "tDiffuse": { value: null }, "exposure": { value: 0.3 } },
                vertexShader: `varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 ); }`,
                fragmentShader: `uniform float exposure; uniform sampler2D tDiffuse; varying vec2 vUv; void main() { vec4 color = texture2D( tDiffuse, vUv ); gl_FragColor = vec4( color.rgb * pow( 2.0, exposure ), color.a ); }`
            };
            composer.addPass(new THREE.ShaderPass(ExposureShader));

            setupEventListeners();
            loadFontAndCreateScore(); // Load font and then start the game
            
            ThemeManager.setTheme('synthwave');
            startGame();
            animate();
        }

        function setupEventListeners() {
            window.addEventListener('resize', onWindowResize);
            document.addEventListener('keydown', handleKeyDown);
            document.addEventListener('keyup', handleKeyUp);
            document.getElementById('theme-synthwave').addEventListener('click', () => ThemeManager.setTheme('synthwave'));
            document.getElementById('theme-classic').addEventListener('click', () => ThemeManager.setTheme('classic'));
            document.getElementById('theme-mono').addEventListener('click', () => ThemeManager.setTheme('mono'));
            restartButton.addEventListener('click', startGame);
            document.getElementById('left-btn').addEventListener('click', () => movePiece(-1));
            document.getElementById('right-btn').addEventListener('click', () => movePiece(1));
            document.getElementById('rotate-btn').addEventListener('click', () => rotatePiece());
            document.getElementById('drop-btn').addEventListener('click', () => hardDrop());
            const downBtn = document.getElementById('down-btn');
            downBtn.addEventListener('mousedown', () => { if(gameState === 'PLAYING') fallSpeedMultiplier = 8.0; });
            downBtn.addEventListener('mouseup', () => fallSpeedMultiplier = 1.0);
            downBtn.addEventListener('mouseleave', () => fallSpeedMultiplier = 1.0);
            downBtn.addEventListener('touchstart', (e) => { e.preventDefault(); if(gameState === 'PLAYING') fallSpeedMultiplier = 8.0; });
            downBtn.addEventListener('touchend', () => fallSpeedMultiplier = 1.0);
        }

        function loadFontAndCreateScore() {
            fontLoader.load('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/fonts/gentilis_bold.typeface.json', function (font) {
                scoreFont = font;
                updateScoreDisplay(); // Create initial score
            });
        }
        
        function onWindowResize() {
            const aspect = window.innerWidth / window.innerHeight;
            const d = 15;
            camera.left = -d * aspect;
            camera.right = d * aspect;
            camera.top = d;
            camera.bottom = -d;
            camera.updateProjectionMatrix();

            renderer.setSize(window.innerWidth, window.innerHeight);
            composer.setSize(window.innerWidth, window.innerHeight);
        }

        function applyCurrentTheme() {
            if (!scene || !floor) return;
            scene.background.set(ThemeManager.get('background'));
            floor.material.color.set(ThemeManager.get('floor'));
            BOMB_POWERUP.createTexture();
            if (activePiece && activePieceMesh && activePieceMesh.material && !activePiece.isPowerUp) {
                activePieceMesh.material.color.set(ThemeManager.getPieceColor(activePiece.pieceType));
            }
            updateLandedVisuals();
        }

        // === GAME LOGIC ===
        function startGame() {
            gameState = 'PLAYING';
            score = 0;
            linesCleared = 0;
            lastScore = -1; // Force score update
            fallSpeed = 1.2;
            gameBoard = createEmptyBoard();
            
            if (landedCubesMesh) {
                scene.remove(landedCubesMesh);
                landedCubesMesh.traverse(child => {
                    if (child.isMesh) {
                        child.geometry.dispose();
                        child.material.dispose();
                    }
                });
                landedCubesMesh = null;
            }
            if (activePieceMesh) {
                scene.remove(activePieceMesh);
                activePieceMesh.geometry.dispose();
                activePieceMesh.material.dispose();
                activePieceMesh = null;
            }
            if (ghostPieceMesh) {
                scene.remove(ghostPieceMesh);
                ghostPieceMesh.geometry.dispose();
                ghostPieceMesh.material.dispose();
                ghostPieceMesh = null;
            }
            
            updateUI();
            gameOverModal.style.display = 'none';
            if (scene) spawnNewPiece();
        }

        function applyGravity() {
            for (let c = 0; c < BOARD_WIDTH; c++) {
                let emptyRow = -1;
                for (let r = 0; r < BOARD_HEIGHT; r++) { if (gameBoard[r][c] === 0) { emptyRow = r; break; } }
                if (emptyRow !== -1) {
                    for (let r = emptyRow + 1; r < BOARD_HEIGHT; r++) {
                        if (gameBoard[r][c] !== 0) { gameBoard[emptyRow][c] = gameBoard[r][c]; gameBoard[r][c] = 0; emptyRow++; }
                    }
                }
            }
        }
        
        function spawnNewPiece() {
            let pieceType; let shape; let powerUpType = null;
            if (Math.random() < 0.15) { // 15% chance for a bomb
                pieceType = 'BOMB'; shape = [[1]]; powerUpType = 'BOMB';
            } else {
                const pieceNames = Object.keys(TETROMINOES);
                pieceType = pieceNames[Math.floor(Math.random() * pieceNames.length)];
                shape = TETROMINOES[pieceType].shape;
            }
            const xPos = Math.floor(BOARD_WIDTH / 2) - Math.ceil(shape[0].length / 2);
            activePiece = { shape, pieceType, x: xPos, y: BOARD_HEIGHT -1, visualX: xPos, visualY: BOARD_HEIGHT -1, powerUpType, isPowerUp: !!powerUpType };
            
            updatePieceMesh(shape, ThemeManager.getPieceColor(pieceType), powerUpType);
            
            if (activePieceMesh) activePieceMesh.scale.setScalar(0.1);
            gameState = 'SPAWNING'; animationTimer = 0;
            if (!isValidMove(activePiece, activePiece.x, activePiece.y)) {
                endGame();
                return;
            }
            updateGhostPieceVisuals();
        }
        
        function isValidMove(piece, newX, floatY) {
            for (let r = 0; r < piece.shape.length; r++) {
                for (let c = 0; c < piece.shape[r].length; c++) {
                    if (piece.shape[r][c]) {
                        const boardX = newX + c;
                        const cubeY = floatY - r;
                        if (boardX < 0 || boardX >= BOARD_WIDTH || cubeY < 0) return false;
                        const boardY = Math.floor(cubeY);
                        if (boardY < BOARD_HEIGHT && gameBoard[boardY][boardX]) return false;
                    }
                }
            }
            return true;
        }
        
        function movePiece(dx) {
            if (gameState !== 'PLAYING' || !activePiece || isCameraAnimating) return;
            const newX = activePiece.x + dx;
            if (isValidMove(activePiece, newX, activePiece.y)) { 
                activePiece.x = newX; 
                updateGhostPieceVisuals(); 
            }
        }
        
        function rotatePiece() {
            if (gameState !== 'PLAYING' || !activePiece || activePiece.isPowerUp || isCameraAnimating) return;
            const originalShape = activePiece.shape;
            activePiece.shape = originalShape[0].map((_, colIndex) => originalShape.map(row => row[colIndex]).reverse());
            
            let kickOffset = 0;
            if (!isValidMove(activePiece, activePiece.x, activePiece.y)) {
                kickOffset = 1;
                if (!isValidMove(activePiece, activePiece.x + kickOffset, activePiece.y)) {
                    kickOffset = -1;
                    if (!isValidMove(activePiece, activePiece.x + kickOffset, activePiece.y)) {
                        kickOffset = 0; 
                        activePiece.shape = originalShape;
                    }
                }
            }

            if (kickOffset !== 0) {
                 activePiece.x += kickOffset;
            }

            updatePieceMesh(activePiece.shape, ThemeManager.getPieceColor(activePiece.pieceType), null);
            updateGhostPieceVisuals();
        }

        function hardDrop() {
            if (gameState !== 'PLAYING' || !activePiece || isCameraAnimating) return;
            let ghostY = activePiece.y;
            while(isValidMove(activePiece, activePiece.x, ghostY - 1)) {
                ghostY--;
            }
            activePiece.y = ghostY;
            lockPiece();
        }
        
        function lockPiece() {
            if (!activePiece) return;
            fallSpeedMultiplier = 1.0;
            activePiece.y = Math.floor(activePiece.y); activePiece.visualY = activePiece.y;
            activePiece.shape.forEach((row, r) => {
                row.forEach((value, c) => {
                    if (value) {
                        const boardX = activePiece.x + c; const boardY = activePiece.y - r;
                        if (boardY >= 0 && boardY < BOARD_HEIGHT) {
                            gameBoard[boardY][boardX] = { pieceType: activePiece.pieceType, powerUpType: activePiece.powerUpType };
                        } else {
                            endGame();
                        }
                    }
                });
            });

            if (gameState === 'GAME_OVER') return;

            scene.remove(activePieceMesh); activePieceMesh.geometry.dispose(); activePieceMesh.material.dispose(); activePieceMesh = null;
            scene.remove(ghostPieceMesh); ghostPieceMesh.geometry.dispose(); ghostPieceMesh.material.dispose(); ghostPieceMesh = null;
            activePiece = null;
            
            updateLandedVisuals();

            if (!clearLines()) {
                 spawnNewPiece();
            }
        }

        function clearLines() {
            let linesToClear = [], powerUpsToActivate = [];
            for (let r = 0; r < BOARD_HEIGHT; r++) {
                if (gameBoard[r].every(cell => cell !== 0)) {
                    linesToClear.push(r);
                    for (let c = 0; c < BOARD_WIDTH; c++) {
                        const cell = gameBoard[r][c];
                        if (cell && cell.powerUpType) {
                            powerUpsToActivate.push({x: c, y: r, type: cell.powerUpType});
                        }
                    }
                }
            }
            if (linesToClear.length > 0) {
                gameState = 'LINE_CLEAR';
                PowerUpManager.activeAnimations.push({
                    timer: 0, duration: LINE_CLEAR_ANIMATION_DURATION,
                    update: (p, cam, orig, flash) => { flash.material.opacity = Math.sin(p * Math.PI) * 0.5; },
                    onComplete: () => {
                        cameraFlashMesh.material.opacity = 0;
                        handlePostLineClear(linesToClear, powerUpsToActivate);
                    }
                });
                return true;
            }
            return false;
        }

        function handlePostLineClear(linesToClear, powerUps) {
            linesCleared += linesToClear.length;
            score += [0, 100, 300, 500, 800][linesToClear.length];
            linesToClear.reverse().forEach(rowIndex => {
                gameBoard.splice(rowIndex, 1);
                gameBoard.push(Array(BOARD_WIDTH).fill(0));
            });
            updateLandedVisuals();
            fallSpeed += 0.05 * linesToClear.length;
            updateUI();

            const nextAction = () => {
                if (powerUps.length > 0) {
                    gameState = 'POWERUP_ANIM';
                    const gameContext = { scene, gameBoard, updateLandedVisuals, spawnNewPiece, camera, originalCameraPos, cameraFlashMesh, applyGravity };
                    powerUps.forEach(p => PowerUpManager.activate(p.type, p.x, p.y, gameContext));
                } else {
                    spawnNewPiece();
                }
            };

            startLineClearVisuals(nextAction);
        }

        function startLineClearVisuals(onCompleteCallback) {
            const squaresGroup = new THREE.Group();
            const squareMaterial = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true });
            squaresGroup.position.y = -CUBE_SIZE + 0.01;
            
            for(let i=1; i < 9; i++) {
                const size = BOARD_WIDTH * 0.4 * i;
                const squareGeom = new THREE.BufferGeometry().setFromPoints([
                    new THREE.Vector3(-size, 0, -size), new THREE.Vector3(size, 0, -size),
                    new THREE.Vector3(size, 0, size), new THREE.Vector3(-size, 0, size),
                    new THREE.Vector3(-size, 0, -size)
                ]);
                const square = new THREE.LineLoop(squareGeom, squareMaterial.clone());
                squaresGroup.add(square);
            }
            scene.add(squaresGroup);

            PowerUpManager.activeAnimations.push({
                timer: 0, duration: 1.5,
                update: (p) => {
                    squaresGroup.children.forEach((square, index) => {
                        const delay = index * 0.04;
                        if (p > delay) {
                            const localP = (p - delay) / (1 - delay);
                            square.scale.setScalar(1 + localP * 3);
                            square.material.opacity = 1.0 - localP;
                        }
                    });
                },
                onComplete: () => {
                    scene.remove(squaresGroup);
                    squaresGroup.traverse(child => {
                        if(child.isLine) { child.geometry.dispose(); child.material.dispose(); }
                    });
                }
            });

            isCameraAnimating = true;
            currentCameraViewIndex = (currentCameraViewIndex + 1) % cameraViews.length;
            const startPos = camera.position.clone();
            const endPos = cameraViews[currentCameraViewIndex].position;
            const endLookAt = cameraViews[currentCameraViewIndex].lookAt;

            PowerUpManager.activeAnimations.push({
                timer: 0, duration: 1.2,
                update: (p) => {
                    const t = p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
                    camera.position.lerpVectors(startPos, endPos, t);
                    originalCameraPos.copy(camera.position); // Update original pos for shake
                    camera.lookAt(endLookAt);
                },
                onComplete: () => {
                    isCameraAnimating = false;
                    camera.position.copy(endPos);
                    originalCameraPos.copy(endPos);
                    camera.lookAt(endLookAt);
                    if (onCompleteCallback) { onCompleteCallback(); }
                }
            });
        }
        
        function endGame() { 
            gameState = 'GAME_OVER'; 
            gameOverModal.style.display = 'block'; 
        }
        
        function handleKeyDown(event) {
            if (gameState !== 'PLAYING' || isCameraAnimating) return;
            switch(event.key) {
                case 'ArrowLeft': case 'a': case 'A': movePiece(-1); break;
                case 'ArrowRight': case 'd': case 'D': movePiece(1); break;
                case 'ArrowDown': case 's': case 'S': fallSpeedMultiplier = 8.0; break;
                case 'ArrowUp': case 'w': case 'W': rotatePiece(); break;
                case ' ': hardDrop(); break;
            }
        }
        function handleKeyUp(event) { 
            if (event.key === 'ArrowDown' || event.key === 's' || event.key === 'S') fallSpeedMultiplier = 1.0;
        }
        
        // === VISUALIZATION LOGIC ===
        function getCubePosition(c, r) { return { x: (c - BOARD_WIDTH / 2 + 0.5) * CUBE_SIZE, y: r * CUBE_SIZE, z: 0 }; }
        
        function createMergedGeometry(shape) {
            const geometries = [];
            shape.forEach((row, r) => {
                row.forEach((value, c) => {
                    if (value) { 
                        const g = new THREE.BoxGeometry(CUBE_SIZE, CUBE_SIZE, CUBE_SIZE); 
                        g.translate(c * CUBE_SIZE, -r * CUBE_SIZE, 0); 
                        geometries.push(g); 
                    }
                });
            });
            return geometries.length > 0 ? THREE.BufferGeometryUtils.mergeBufferGeometries(geometries) : null;
        }

        function updatePieceMesh(shape, color, powerUpType) {
            const mergedGeometry = createMergedGeometry(shape); if (!mergedGeometry) return;
            const material = powerUpType ? new THREE.MeshStandardMaterial({ map: BOMB_POWERUP.texture }) : new THREE.MeshStandardMaterial({ color, metalness: 0.2, roughness: 0.5 });
            
            if (activePieceMesh) { scene.remove(activePieceMesh); activePieceMesh.geometry.dispose(); activePieceMesh.material.dispose(); }
            activePieceMesh = new THREE.Mesh(mergedGeometry, material);
            activePieceMesh.castShadow = true;
            scene.add(activePieceMesh);
            
            if (ghostPieceMesh) { 
                scene.remove(ghostPieceMesh);
                ghostPieceMesh.geometry.dispose(); 
            }
            ghostPieceMesh = new THREE.Mesh(mergedGeometry.clone(), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.25, wireframe: true }));
            scene.add(ghostPieceMesh);
            
            ghostPieceMesh.visible = activePieceMesh.visible = true;
        }

        function updateGhostPieceVisuals() {
            if (!activePiece || gameState === 'LINE_CLEAR' || !ghostPieceMesh) return;
            let ghostY = activePiece.y;
            while(isValidMove(activePiece, activePiece.x, ghostY - 1)) ghostY--;
            ghostPieceMesh.position.copy(getCubePosition(activePiece.x, Math.floor(ghostY)));
            ghostPieceMesh.visible = true;
        }
        
        function updateLandedVisuals() {
            if (landedCubesMesh) {
                scene.remove(landedCubesMesh);
                landedCubesMesh.traverse(child => {
                    if (child.isMesh) {
                        child.geometry.dispose();
                        child.material.dispose();
                    }
                });
            }
            
            const geometriesByColor = {};

            for (let r = 0; r < BOARD_HEIGHT; r++) {
                for (let c = 0; c < BOARD_WIDTH; c++) {
                    const cell = gameBoard[r][c];
                    if (cell) {
                        const colorHex = ThemeManager.getPieceColor(cell.pieceType);
                        if (!geometriesByColor[colorHex]) {
                            geometriesByColor[colorHex] = [];
                        }
                        const pos = getCubePosition(c, r);
                        const geometry = new THREE.BoxGeometry(CUBE_SIZE, CUBE_SIZE, CUBE_SIZE);
                        geometry.translate(pos.x, pos.y, pos.z);
                        geometriesByColor[colorHex].push(geometry);
                    }
                }
            }

            const finalMeshGroup = new THREE.Group();
            for (const colorHex in geometriesByColor) {
                if (geometriesByColor[colorHex].length > 0) {
                    const mergedGeom = THREE.BufferGeometryUtils.mergeBufferGeometries(geometriesByColor[colorHex]);
                    const material = new THREE.MeshStandardMaterial({ color: parseInt(colorHex), metalness: 0.2, roughness: 0.5 });
                    const mesh = new THREE.Mesh(mergedGeom, material);
                    mesh.castShadow = true;
                    mesh.receiveShadow = true;
                    finalMeshGroup.add(mesh);
                }
            }
            landedCubesMesh = finalMeshGroup;
            scene.add(landedCubesMesh);
        }
        
        function updateActivePieceVisuals() {
            if (!activePieceMesh) return;
            activePiece.visualX += (activePiece.x - activePiece.visualX) * LERP_FACTOR;
            activePiece.visualY += (activePiece.y - activePiece.visualY) * LERP_FACTOR;
            activePieceMesh.position.copy(getCubePosition(activePiece.visualX, activePiece.visualY));
        }

        function updateScoreDisplay() {
            if (!scoreFont || score === lastScore) return;

            if (scoreTextMesh) {
                scene.remove(scoreTextMesh);
                scoreTextMesh.geometry.dispose();
                scoreTextMesh.material.dispose();
            }

            const geometry = new THREE.TextGeometry(score.toString(), {
                font: scoreFont,
                size: 2,
                height: 0.2,
            });
            geometry.center();

            scoreTextMesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({ color: 0xffffff }));
            scoreTextMesh.position.set(0, -CUBE_SIZE + 0.1, BOARD_WIDTH / 2 + 3);
            scoreTextMesh.rotation.x = -Math.PI / 2;
            scene.add(scoreTextMesh);

            if (lastScore !== -1) { // Don't blink on first render
                triggerScoreBlink();
            }
            lastScore = score;
        }
        
        function triggerScoreBlink() {
            if (!scoreTextMesh) return;
            PowerUpManager.activeAnimations.push({
                timer: 0, duration: 0.6,
                update: (p) => {
                    const color = (Math.floor(p * 10) % 2 === 0) ? 0xff0000 : 0xffffff;
                    scoreTextMesh.material.color.setHex(color);
                },
                onComplete: () => {
                    scoreTextMesh.material.color.setHex(0xffffff);
                }
            });
        }
        
        function updateUI() { 
            linesElement.textContent = linesCleared;
            updateScoreDisplay();
        }

        // === ANIMATION LOOP ===
        function animate() {
            requestAnimationFrame(animate); 

            const deltaTime = clock.getDelta();

            if (gameState === 'GAME_OVER') {
                 composer.render();
                 return;
            }

            const gameContext = { scene, camera, originalCameraPos, cameraFlashMesh, gameBoard, applyGravity, updateLandedVisuals, spawnNewPiece };
            PowerUpManager.updateAnimations(deltaTime, gameContext);
            
            switch(gameState) {
                case 'SPAWNING':
                    animationTimer += deltaTime;
                    const progress = Math.min(1, animationTimer / SPAWN_ANIMATION_DURATION);
                    const c1 = 1.70158;
                    const c3 = c1 + 1;
                    const scale = 1 + c3 * Math.pow(progress - 1, 3) + c1 * Math.pow(progress - 1, 2);
                    if (activePieceMesh) activePieceMesh.scale.setScalar(Math.max(0, scale));
                    if (progress >= 1) { 
                        gameState = 'PLAYING'; 
                        if (activePieceMesh) activePieceMesh.scale.setScalar(1.0); 
                    }
                    if(activePiece) updateActivePieceVisuals();
                    break;
                case 'PLAYING':
                    if (activePiece) {
                        const fallDistance = fallSpeed * fallSpeedMultiplier * deltaTime;
                        if (isValidMove(activePiece, activePiece.x, activePiece.y - fallDistance)) {
                            activePiece.y -= fallDistance;
                        } else { 
                            lockPiece(); 
                        }
                        updateActivePieceVisuals();
                    }
                    break;
            }
            composer.render();
        }

        init();
}
