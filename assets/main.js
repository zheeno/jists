/**
 * Homepage feed renderer.
 *
 * Expected feed item shape:
 * {
 *   title: string,
 *   url: string,
 *   date: string,
 *   source?: string,
 *   category?: string,
 *   author?: string,
 *   readTime?: string,
 *   excerpt?: string,
 *   imageUrl?: string,
 *   imageAlt?: string
 * }
 */
(function () {
  const ul = document.getElementById('posts');
  const countEl = document.getElementById('post-count');
  if (!ul) return;

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

  function showSkeletons() {
    ul.innerHTML = '';
    for (let i = 0; i < 4; i++) {
      const li = document.createElement('li');
      const featured = i === 0;
      li.className = featured ? 'post-card--featured' : 'post-card--compact';
      li.innerHTML =
        '<div class="skeleton-card">' +
        '<div class="skeleton-media"></div>' +
        '<div class="skeleton-line skeleton-line--short"></div>' +
        '<div class="skeleton-line skeleton-line--title"></div>' +
        '<div class="skeleton-line skeleton-line--title2"></div>' +
        '<div class="skeleton-line skeleton-line--excerpt"></div>' +
        '</div>';
      ul.appendChild(li);
    }
  }

  function createCard(item, index) {
    const li = document.createElement('li');
    const isFeatured = index === 0;
    li.className = isFeatured ? 'post-card--featured' : 'post-card--compact';

    const a = document.createElement('a');
    a.href = basePath() + item.url;
    a.className = 'post-card fade-in';
    a.setAttribute('aria-label', item.title);

    if (item.category) {
      const category = document.createElement('p');
      category.className = 'post-card-category';
      category.textContent = item.category;
      a.appendChild(category);
    }

    if (item.imageUrl) {
      const media = document.createElement('div');
      media.className = 'post-card-media';

      const img = document.createElement('img');
      img.className = 'post-card-image';
      img.src = item.imageUrl;
      img.alt = item.imageAlt || item.title;
      img.loading = index < 2 ? 'eager' : 'lazy';
      img.decoding = 'async';
      if (index === 0) img.fetchPriority = 'high';

      media.appendChild(img);
      a.appendChild(media);
    }

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

  showSkeletons();

  fetch(basePath() + 'feed.json')
    .then(function (r) {
      return r.ok ? r.json() : Promise.reject(r.status);
    })
    .then(function (data) {
      const items = data.items || [];
      ul.innerHTML = '';
      ul.setAttribute('aria-busy', 'false');

      if (countEl) {
        countEl.textContent = items.length ? items.length + ' posts' : '';
      }

      if (!items.length) {
        ul.innerHTML =
          '<li class="post-grid-empty">No posts yet.</li>';
        return;
      }

      items.forEach(function (item, i) {
        ul.appendChild(createCard(item, i));
      });
    })
    .catch(function () {
      ul.innerHTML =
        '<li class="post-grid-empty">Could not load posts. Check feed.json.</li>';
      ul.setAttribute('aria-busy', 'false');
    });
})();
