import * as THREE from 'three';

// Spine (+Z) faces camera in the row. Featured book rotates to show cover (+X).
const BOOK_WIDTH = 0.16;
const BOOK_HEIGHT = 1.55;
const BOOK_DEPTH = 1.05;
const BOOK_GAP = 0.05;
const SHELF_DEPTH = 0.55;
const SHELF_HEIGHT = 0.12;
const SHELF_Y = -0.95;

const PAPER = 0xf4ede3;
const WALNUT = 0x5c4332;
const PAGE_COLOR = 0xf2e8d8;

const SPINE_FALLBACK = [
  0x7a5a48, 0x5f6b55, 0x6a5a78, 0x8a6340, 0x4f6270, 0x7a4f4f, 0x5a6a52, 0x6e5a40,
];

/**
 * @param {import('../catalog.js').CatalogBook} entry
 * @param {number} index
 */
function createBookMesh(entry, index) {
  const heightJitter = 1 + ((index % 5) - 2) * 0.02;
  const depthJitter = 1 + ((index % 3) - 1) * 0.03;
  const width = BOOK_WIDTH * (1 + ((index % 4) - 1.5) * 0.06);
  const height = BOOK_HEIGHT * heightJitter;
  const depth = BOOK_DEPTH * depthJitter;
  const fallback = SPINE_FALLBACK[index % SPINE_FALLBACK.length];

  const geometry = new THREE.BoxGeometry(width, height, depth);
  const materials = [
    new THREE.MeshStandardMaterial({ color: fallback, roughness: 0.7, metalness: 0.02 }), // +X cover
    new THREE.MeshStandardMaterial({ color: PAGE_COLOR, roughness: 0.96 }), // -X pages
    new THREE.MeshStandardMaterial({ color: PAGE_COLOR, roughness: 0.96 }),
    new THREE.MeshStandardMaterial({ color: PAGE_COLOR, roughness: 0.96 }),
    new THREE.MeshStandardMaterial({ color: fallback, roughness: 0.75, metalness: 0.02 }), // +Z spine
    new THREE.MeshStandardMaterial({ color: 0x4a372c, roughness: 0.9 }),
  ];

  const mesh = new THREE.Mesh(geometry, materials);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  mesh.userData = {
    entry,
    index,
    basePosition: new THREE.Vector3(),
    coverMaterial: materials[0],
    spineMaterial: materials[4],
  };
  return mesh;
}

/**
 * @param {THREE.MeshStandardMaterial} material
 * @param {string} url
 * @param {{ asSpine?: boolean }} [options]
 */
function applyCoverTexture(material, url, options = {}) {
  const loader = new THREE.TextureLoader();
  loader.load(
    url,
    (source) => {
      const texture = source.clone();
      texture.needsUpdate = true;
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.minFilter = THREE.LinearMipmapLinearFilter;
      texture.magFilter = THREE.LinearFilter;
      texture.wrapS = THREE.ClampToEdgeWrapping;
      texture.wrapT = THREE.ClampToEdgeWrapping;

      if (options.asSpine) {
        // Stretch the whole cover onto the spine (intentionally narrow/distorted).
        texture.repeat.set(1, 1);
        texture.offset.set(0, 0);
        texture.center.set(0.5, 0.5);
        texture.rotation = 0;
      }

      material.map = texture;
      material.color.set(0xffffff);
      material.needsUpdate = true;
    },
    undefined,
    () => {
      material.color.set(0x6b4f3a);
    },
  );
}

function createShelfSegment(length) {
  const group = new THREE.Group();
  const boardMat = new THREE.MeshStandardMaterial({
    color: WALNUT,
    roughness: 0.68,
    metalness: 0.04,
  });

  const board = new THREE.Mesh(
    new THREE.BoxGeometry(length, SHELF_HEIGHT, SHELF_DEPTH),
    boardMat,
  );
  board.position.y = SHELF_Y;
  board.receiveShadow = true;
  board.castShadow = true;
  group.add(board);

  const lip = new THREE.Mesh(
    new THREE.BoxGeometry(length, 0.05, 0.05),
    boardMat,
  );
  lip.position.set(0, SHELF_Y + SHELF_HEIGHT / 2 + 0.02, SHELF_DEPTH / 2 - 0.02);
  lip.castShadow = true;
  group.add(lip);

  return group;
}

export class ShelfScene {
  /**
   * @param {HTMLCanvasElement} canvas
   * @param {import('../catalog.js').CatalogBook[]} books
   * @param {{
   *   onFeatureChange: (book: import('../catalog.js').CatalogBook, index: number, total: number) => void,
   *   onInspect: (book: import('../catalog.js').CatalogBook | null) => void,
   * }} callbacks
   */
  constructor(canvas, books, callbacks) {
    this.canvas = canvas;
    this.books = books;
    this.callbacks = callbacks;

    this.mode = 'browse';
    this.featuredIndex = 0;
    this.scrollX = 0;
    this.targetScrollX = 0;
    this.isDragging = false;
    this.dragStartX = 0;
    this.dragStartY = 0;
    this.dragStartScroll = 0;
    this.pointerClient = { x: 0, y: 0 };
    this.raycaster = new THREE.Raycaster();
    this.pointer = new THREE.Vector2();
    this.bookMeshes = [];
    this.clock = new THREE.Clock();

    this._initScene();
    this._initBooks();
    this._initLights();
    this._bindEvents();
    this.setFeatured(0, { immediate: true });
    this._animate();
  }

  _initScene() {
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: false,
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.12;
    this.renderer.setClearColor(PAPER);

    this.world = new THREE.Group();
    this.camera = new THREE.PerspectiveCamera(36, 1, 0.1, 100);
    this.camera.position.set(0, 0.15, 4.6);
    this.camera.lookAt(0, -0.15, 0);

    this.rootScene = new THREE.Scene();
    this.rootScene.background = new THREE.Color(PAPER);
    this.rootScene.add(this.world);

    this._resize();
  }

  _initBooks() {
    const count = this.books.length;
    const unit = BOOK_WIDTH + BOOK_GAP;
    const shelfLength = Math.max(count * unit + 4, 12);

    this.unit = unit;
    this.world.add(createShelfSegment(shelfLength));

    const startX = -((count - 1) * unit) / 2;
    this.books.forEach((entry, index) => {
      const mesh = createBookMesh(entry, index);
      const height = mesh.geometry.parameters.height || BOOK_HEIGHT;
      const x = startX + index * unit;
      mesh.position.set(x, SHELF_Y + SHELF_HEIGHT / 2 + height / 2 + 0.01, 0.08);
      mesh.userData.basePosition.copy(mesh.position);

      if (entry.coverUrl) {
        applyCoverTexture(mesh.userData.coverMaterial, entry.coverUrl);
        applyCoverTexture(mesh.userData.spineMaterial, entry.coverUrl, { asSpine: true });
      }

      this.world.add(mesh);
      this.bookMeshes.push(mesh);
    });

    this.scrollBounds = {
      min: -Math.max(0, (count * unit) / 2 - 0.8),
      max: Math.max(0, (count * unit) / 2 - 0.8),
    };
  }

  _initLights() {
    this.rootScene.add(new THREE.AmbientLight(0xfff8ef, 0.95));
    this.rootScene.add(new THREE.HemisphereLight(0xfff6ea, 0xd8cec0, 0.5));

    const key = new THREE.DirectionalLight(0xfff1e0, 0.9);
    key.position.set(2, 6, 5);
    key.castShadow = true;
    key.shadow.mapSize.set(1024, 1024);
    key.shadow.camera.left = -12;
    key.shadow.camera.right = 12;
    key.shadow.camera.top = 6;
    key.shadow.camera.bottom = -4;
    key.shadow.bias = -0.0002;
    this.rootScene.add(key);

    const fill = new THREE.DirectionalLight(0xe8dcc8, 0.4);
    fill.position.set(-4, 3, 3);
    this.rootScene.add(fill);
  }

  _bindEvents() {
    this._onResize = () => this._resize();
    this._onPointerDown = (e) => this._handlePointerDown(e);
    this._onPointerMove = (e) => this._handlePointerMove(e);
    this._onPointerUp = () => this._handlePointerUp();
    this._onWheel = (e) => this._handleWheel(e);
    this._onKeyDown = (e) => this._handleKeyDown(e);

    window.addEventListener('resize', this._onResize);
    this.canvas.addEventListener('pointerdown', this._onPointerDown);
    this.canvas.addEventListener('pointermove', this._onPointerMove);
    window.addEventListener('pointerup', this._onPointerUp);
    this.canvas.addEventListener('wheel', this._onWheel, { passive: false });
    window.addEventListener('keydown', this._onKeyDown);
  }

  _resize() {
    const rect = this.canvas.getBoundingClientRect();
    const width = Math.max(rect.width, 1);
    const height = Math.max(rect.height, 1);
    this.renderer.setSize(width, height, false);
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
  }

  /**
   * @param {number} index
   * @param {{ immediate?: boolean }} [options]
   */
  setFeatured(index, options = {}) {
    if (index < 0 || index >= this.bookMeshes.length) return;
    this.featuredIndex = index;
    const mesh = this.bookMeshes[index];
    const targetScroll = this._clampScroll(-mesh.userData.basePosition.x + 0.55);
    this.targetScrollX = targetScroll;
    if (options.immediate) this.scrollX = targetScroll;

    this.callbacks.onFeatureChange(this.books[index], index, this.books.length);
  }

  featureNext(delta) {
    const next = THREE.MathUtils.clamp(
      this.featuredIndex + delta,
      0,
      this.bookMeshes.length - 1,
    );
    this.setFeatured(next);
  }

  openDetails() {
    const book = this.books[this.featuredIndex];
    this.mode = 'inspect';
    this.callbacks.onInspect(book);
    this.canvas.classList.add('is-inspecting');
  }

  exitInspect() {
    this.mode = 'browse';
    this.callbacks.onInspect(null);
    this.canvas.classList.remove('is-inspecting');
  }

  _handlePointerDown(event) {
    if (this.mode === 'inspect') return;
    this.isDragging = true;
    this.dragStartX = event.clientX;
    this.dragStartY = event.clientY;
    this.pointerClient.x = event.clientX;
    this.pointerClient.y = event.clientY;
    this.dragStartScroll = this.targetScrollX;
    this.canvas.setPointerCapture(event.pointerId);
    this.canvas.classList.add('is-dragging');
  }

  _handlePointerMove(event) {
    this.pointerClient.x = event.clientX;
    this.pointerClient.y = event.clientY;
    if (this.mode === 'inspect' || !this.isDragging) return;
    const delta = (event.clientX - this.dragStartX) * 0.0045;
    this.targetScrollX = this._clampScroll(this.dragStartScroll - delta);
  }

  _handlePointerUp() {
    if (!this.isDragging) return;
    const moved =
      Math.abs(this.pointerClient.x - this.dragStartX) > 5 ||
      Math.abs(this.pointerClient.y - this.dragStartY) > 5;
    this.isDragging = false;
    this.canvas.classList.remove('is-dragging');

    if (this.mode === 'browse' && !moved) {
      this._tryPickBook(this.pointerClient.x, this.pointerClient.y);
    } else if (this.mode === 'browse' && moved) {
      this._snapFeaturedFromScroll();
    }
  }

  _handleWheel(event) {
    event.preventDefault();
    if (this.mode !== 'browse') return;
    this.targetScrollX = this._clampScroll(this.targetScrollX + event.deltaY * 0.0035);
    clearTimeout(this._wheelSnapTimer);
    this._wheelSnapTimer = setTimeout(() => this._snapFeaturedFromScroll(), 140);
  }

  _handleKeyDown(event) {
    if (event.key === 'Escape' && this.mode === 'inspect') {
      this.exitInspect();
      return;
    }
    if (this.mode !== 'browse') return;
    if (event.key === 'ArrowLeft') this.featureNext(-1);
    if (event.key === 'ArrowRight') this.featureNext(1);
    if (event.key === 'Enter') this.openDetails();
  }

  _clampScroll(value) {
    return THREE.MathUtils.clamp(value, this.scrollBounds.min, this.scrollBounds.max);
  }

  _snapFeaturedFromScroll() {
    let best = 0;
    let bestDist = Infinity;
    this.bookMeshes.forEach((mesh, index) => {
      const worldX = mesh.userData.basePosition.x + this.targetScrollX;
      const dist = Math.abs(worldX - 0.55);
      if (dist < bestDist) {
        bestDist = dist;
        best = index;
      }
    });
    this.setFeatured(best);
  }

  _tryPickBook(clientX, clientY) {
    const rect = this.canvas.getBoundingClientRect();
    this.pointer.x = ((clientX - rect.left) / rect.width) * 2 - 1;
    this.pointer.y = -((clientY - rect.top) / rect.height) * 2 + 1;
    this.raycaster.setFromCamera(this.pointer, this.camera);
    const hits = this.raycaster.intersectObjects(this.bookMeshes, false);
    if (!hits.length) return;
    const index = hits[0].object.userData.index;
    if (index === this.featuredIndex) {
      this.openDetails();
    } else {
      this.setFeatured(index);
    }
  }

  _animate = () => {
    requestAnimationFrame(this._animate);
    const dt = this.clock.getDelta();

    this.scrollX = THREE.MathUtils.damp(this.scrollX, this.targetScrollX, 7, dt);
    this.world.position.x = this.scrollX;

    this.bookMeshes.forEach((mesh, i) => {
      const base = mesh.userData.basePosition;
      const featured = i === this.featuredIndex;
      const targetPos = base.clone();
      let targetRotY = 0;

      if (featured) {
        targetPos.z = base.z + 0.95;
        targetPos.y = base.y + 0.08;
        targetRotY = -Math.PI / 2;
      }

      mesh.position.lerp(targetPos, 1 - Math.exp(-8 * dt));
      mesh.rotation.y = THREE.MathUtils.damp(mesh.rotation.y, targetRotY, 7, dt);
    });

    this.renderer.render(this.rootScene, this.camera);
  };

  dispose() {
    window.removeEventListener('resize', this._onResize);
    this.canvas.removeEventListener('pointerdown', this._onPointerDown);
    this.canvas.removeEventListener('pointermove', this._onPointerMove);
    window.removeEventListener('pointerup', this._onPointerUp);
    this.canvas.removeEventListener('wheel', this._onWheel);
    window.removeEventListener('keydown', this._onKeyDown);
    this.renderer.dispose();
  }
}
