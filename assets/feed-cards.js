/**
 * Shared editorial feed utilities and article card renderer.
 */
(function (global) {
  function basePath() {
    const seg = window.location.pathname.split('/').filter(Boolean);
    if (seg.length && !seg[seg.length - 1].includes('.')) {
      return '/' + seg[0] + '/';
    }
    if (seg.length > 1) {
      return '/' + seg[0] + '/';
    }
    return './';
  }

  function normalizeUrl(url) {
    return String(url || '')
      .replace(/^https?:\/\/[^/]+/, '')
      .replace(/^\//, '')
      .replace(/^jists\//, '');
  }

  function formatDate(value) {
    if (!value) return '';
    const date = new Date(value + 'T00:00:00');
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  }

  function categorySlug(name) {
    return String(name || '')
      .toLowerCase()
      .replace(/ & /g, '-')
      .replace(/\s+/g, '-')
      .replace(/&/g, '')
      .replace(/\./g, '')
      .replace(/[^a-z0-9-]/g, '');
  }

  function categoriesPageUrl(category) {
    return basePath() + 'categories.html#' + categorySlug(category);
  }

  function createCategoryBadge(category) {
    const badge = document.createElement('a');
    badge.className = 'category-badge';
    badge.href = categoriesPageUrl(category);
    badge.textContent = category;
    return badge;
  }

  function createImage(item, options) {
    const images = global.EditorialImages;
    const loading = options.loading || 'lazy';
    const className = 'post-card-image' + (options.className ? ' ' + options.className : '');

    if (images) {
      return images.create({
        src: item.imageUrl,
        alt: item.imageAlt || item.title,
        fallbackAlt: item.imageAlt || item.title,
        loading: loading,
        className: className,
        fetchPriority: options.fetchPriority,
      });
    }

    const img = document.createElement('img');
    img.className = className + ' editorial-image';
    img.src = item.imageUrl;
    img.alt = item.imageAlt || item.title;
    img.loading = loading;
    img.decoding = 'async';
    return img;
  }

  function createCard(item, options) {
    options = options || {};
    const index = options.index || 0;
    const isFeatured = options.featured === true;
    const uniform = options.uniform === true;

    const li = document.createElement('li');
    if (uniform) {
      li.className = 'post-card--uniform';
    } else {
      li.className = isFeatured ? 'post-card--featured' : 'post-card--compact';
    }

    const a = document.createElement('a');
    a.href = basePath() + item.url;
    a.className = 'post-card fade-in';
    a.setAttribute('aria-label', item.title);

    if (item.category) {
      li.appendChild(createCategoryBadge(item.category));
    }

    const media = document.createElement('div');
    media.className = 'media-frame post-card-media';
    if (item.imageUrl) {
      media.appendChild(
        createImage(item, {
          loading: index < 3 ? 'eager' : 'lazy',
          fetchPriority: isFeatured ? 'high' : undefined,
        })
      );
    } else if (global.EditorialImages) {
      media.classList.add('media-frame--fallback');
      media.setAttribute('aria-label', item.title);
    }
    a.appendChild(media);

    const body = document.createElement('div');
    body.className = 'post-card-body';

    const title = document.createElement('h3');
    title.className = 'post-card-title';
    title.textContent = item.title;
    body.appendChild(title);

    if (item.excerpt) {
      const excerpt = document.createElement('p');
      excerpt.className = 'post-card-excerpt';
      excerpt.textContent = item.excerpt;
      body.appendChild(excerpt);
    }

    const meta = document.createElement('p');
    meta.className = 'post-card-meta';
    const parts = [formatDate(item.date)];
    if (item.readTime) parts.push(item.readTime);
    if (item.author) parts.push(item.author);
    meta.textContent = parts.filter(Boolean).join(' · ');
    body.appendChild(meta);

    a.appendChild(body);
    li.appendChild(a);
    return li;
  }

  function createSkeletonCard(options) {
    options = options || {};
    const li = document.createElement('li');
    li.className = options.uniform ? 'post-card--uniform' : options.featured ? 'post-card--featured' : 'post-card--compact';
    li.innerHTML =
      '<div class="skeleton-card">' +
      '<div class="skeleton-media"></div>' +
      '<div class="skeleton-line skeleton-line--short"></div>' +
      '<div class="skeleton-line skeleton-line--title"></div>' +
      '<div class="skeleton-line skeleton-line--excerpt"></div>' +
      '</div>';
    return li;
  }

  function fetchFeed() {
    return fetch(basePath() + 'feed.json').then(function (r) {
      return r.ok ? r.json() : Promise.reject(new Error('Feed unavailable'));
    });
  }

  function getRelatedArticles(items, currentUrl, currentCategory, limit) {
    limit = limit || 4;
    const current = normalizeUrl(currentUrl);
    const others = items.filter(function (item) {
      return normalizeUrl(item.url) !== current;
    });

    const sameCategory = currentCategory
      ? others.filter(function (item) {
          return item.category === currentCategory;
        })
      : [];

    const related = sameCategory.slice(0, limit);
    others.forEach(function (item) {
      if (related.length >= limit) return;
      if (related.some(function (r) { return r.url === item.url; })) return;
      related.push(item);
    });

    return related.slice(0, limit);
  }

  global.EditorialFeed = {
    basePath: basePath,
    normalizeUrl: normalizeUrl,
    formatDate: formatDate,
    categorySlug: categorySlug,
    categoriesPageUrl: categoriesPageUrl,
    createCategoryBadge: createCategoryBadge,
    createCard: createCard,
    createSkeletonCard: createSkeletonCard,
    fetchFeed: fetchFeed,
    getRelatedArticles: getRelatedArticles,
  };
})(window);
