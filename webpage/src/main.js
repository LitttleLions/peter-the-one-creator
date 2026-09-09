import { loadCatalog } from './catalog.js';
import { ShelfScene } from './shelf/ShelfScene.js';

const loadingEl = document.getElementById('loading-state');
const emptyEl = document.getElementById('empty-state');
const canvas = document.getElementById('shelf-canvas');
const panel = document.getElementById('book-panel');
const panelBack = document.getElementById('panel-back');
const panelSubtitle = document.getElementById('panel-subtitle');
const panelTitle = document.getElementById('panel-title');
const panelAuthor = document.getElementById('panel-author');
const panelSummary = document.getElementById('panel-summary');
const panelAmazon = document.getElementById('panel-amazon');
const positionMarker = document.getElementById('position-marker');
const positionCurrent = document.getElementById('position-current');
const positionTotal = document.getElementById('position-total');
const volumeCount = document.getElementById('volume-count');
const featureCard = document.getElementById('feature-card');
const featureTitle = document.getElementById('feature-title');
const featureAuthor = document.getElementById('feature-author');
const featureDetails = document.getElementById('feature-details');
const navPrev = document.getElementById('nav-prev');
const navNext = document.getElementById('nav-next');

/** @type {ShelfScene | null} */
let shelf = null;

function showLoading() {
  loadingEl.hidden = false;
  emptyEl.hidden = true;
  canvas.hidden = true;
  positionMarker.hidden = true;
  featureCard.hidden = true;
}

function showEmpty() {
  loadingEl.hidden = true;
  emptyEl.hidden = false;
  canvas.hidden = true;
  positionMarker.hidden = true;
  featureCard.hidden = true;
}

function showShelf(total) {
  loadingEl.hidden = true;
  emptyEl.hidden = true;
  canvas.hidden = false;
  positionMarker.hidden = false;
  featureCard.hidden = false;
  positionTotal.textContent = String(total);
  positionCurrent.textContent = '1';
  volumeCount.textContent = String(total);
}

/**
 * @param {import('./catalog.js').CatalogBook} book
 * @param {number} index
 * @param {number} total
 */
function updateFeatureCard(book, index, total) {
  featureCard.hidden = false;
  featureTitle.textContent = book.title || 'Ohne Titel';
  featureAuthor.textContent = book.author || '';
  positionCurrent.textContent = String(index + 1);
  positionTotal.textContent = String(total);
}

/**
 * @param {import('./catalog.js').CatalogBook | null} book
 */
function updatePanel(book) {
  if (!book) {
    panel.classList.remove('is-open');
    panel.hidden = true;
    document.body.classList.remove('is-inspecting');
    requestAnimationFrame(() => shelf?._resize?.());
    return;
  }

  document.body.classList.add('is-inspecting');
  panel.hidden = false;
  panel.classList.add('is-open');

  panelSubtitle.textContent = book.subtitle || '';
  panelSubtitle.hidden = !book.subtitle;
  panelTitle.textContent = book.title || 'Ohne Titel';
  panelAuthor.textContent = book.author || '';
  panelSummary.textContent = book.summary || 'Keine Beschreibung vorhanden.';

  if (book.amazonUrl) {
    panelAmazon.href = book.amazonUrl;
    panelAmazon.hidden = false;
  } else {
    panelAmazon.hidden = true;
  }

  requestAnimationFrame(() => shelf?._resize?.());
}

panelBack.addEventListener('click', () => shelf?.exitInspect());
featureDetails.addEventListener('click', () => shelf?.openDetails());
navPrev.addEventListener('click', () => shelf?.featureNext(-1));
navNext.addEventListener('click', () => shelf?.featureNext(1));

async function init() {
  if (window.location.protocol === 'file:') {
    loadingEl.hidden = true;
    emptyEl.hidden = false;
    canvas.hidden = true;
    positionMarker.hidden = true;
    featureCard.hidden = true;
    emptyEl.querySelector('.state-title').textContent = 'Bitte lokalen Server nutzen';
    emptyEl.querySelector('.state-body').innerHTML =
      'Die Datei <code>index.html</code> darf nicht per <code>file://</code> geoeffnet werden — ' +
      'der Browser blockiert dann die 3D-Module.<br><br>' +
      'Im Repo-Root: <code>python tools/preview_webpage.py</code><br>' +
      'oder Doppelklick auf <code>Dev-Start-Webpage.cmd</code><br>' +
      'dann <a href="http://127.0.0.1:4173">http://127.0.0.1:4173</a> oeffnen.';
    return;
  }

  showLoading();
  const { status, catalog } = await loadCatalog();

  if (status === 'missing' || status === 'empty') {
    showEmpty();
    return;
  }

  const books = catalog?.books ?? [];
  showShelf(books.length);

  shelf = new ShelfScene(canvas, books, {
    onFeatureChange: updateFeatureCard,
    onInspect: updatePanel,
  });
}

init();
