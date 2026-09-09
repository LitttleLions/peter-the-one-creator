const CATALOG_URL = './data/catalog.json';

/**
 * @typedef {Object} CatalogBook
 * @property {string} id
 * @property {string} title
 * @property {string} [subtitle]
 * @property {string} author
 * @property {string} [summary]
 * @property {string} coverUrl
 * @property {string} [amazonUrl]
 * @property {number} [sortOrder]
 */

/**
 * @typedef {Object} Catalog
 * @property {CatalogBook[]} books
 * @property {string} [generatedAt]
 */

/**
 * @returns {Promise<{ status: 'ok' | 'empty' | 'missing', catalog: Catalog | null }>}
 */
export async function loadCatalog() {
  try {
    const response = await fetch(CATALOG_URL, { cache: 'no-cache' });
    if (!response.ok) {
      return { status: 'missing', catalog: null };
    }

    const data = await response.json();
    const books = Array.isArray(data?.books) ? data.books : [];

    if (books.length === 0) {
      return { status: 'empty', catalog: { ...data, books: [] } };
    }

    const sorted = [...books].sort((a, b) => {
      const orderA = typeof a.sortOrder === 'number' ? a.sortOrder : Number.MAX_SAFE_INTEGER;
      const orderB = typeof b.sortOrder === 'number' ? b.sortOrder : Number.MAX_SAFE_INTEGER;
      if (orderA !== orderB) return orderA - orderB;
      return (a.title || '').localeCompare(b.title || '', 'de');
    });

    return { status: 'ok', catalog: { ...data, books: sorted } };
  } catch {
    return { status: 'missing', catalog: null };
  }
}
