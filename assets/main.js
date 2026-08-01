/**
 * Homepage feed renderer.
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

  function createImage(item, index) {
    const images = window.EditorialImages;
    const img = images
      ? images.create({
          src: item.imageUrl,
          alt: item.imageAlt || item.title,
          fallbackAlt: item.imageAlt || item.title,
          loading: index < 3 ? 'eager' : 'lazy',
          className: 'post-card-image',
          fetchPriority: index === 0 ? 'high' : undefined,
        })
      : Object.assign(document.createElement('img'), {
          className: 'post-card-image editorial-image',
          src: item.imageUrl,
          alt: item.imageAlt || item.title,
          loading: index < 3 ? 'eager' : 'lazy',
          decoding: 'async',
        });

    return img;
  }

  function showSkeletons() {
    ul.innerHTML = '';
    for (let i = 0; i < 6; i++) {
      const li = document.createElement('li');
      const featured = i === 0;
      li.className = featured ? 'post-card--featured' : 'post-card--compact';
      li.innerHTML =
        '<div class="skeleton-card">' +
        '<div class="skeleton-media"></div>' +
        '<div class="skeleton-line skeleton-line--short"></div>' +
        '<div class="skeleton-line skeleton-line--title"></div>' +
        '<div class="skeleton-line skeleton-line--excerpt"></div>' +
        '</div>';
      ul.appendChild(li);
    }
  }

  function showError(message, retry) {
    ul.innerHTML = '';
    ul.setAttribute('aria-busy', 'false');

    const li = document.createElement('li');
    li.className = 'post-grid-error';

    const text = document.createElement('p');
    text.textContent = message;
    li.appendChild(text);

    if (retry) {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'post-grid-retry';
      button.textContent = 'Try again';
      button.addEventListener('click', retry);
      li.appendChild(button);
    }

    ul.appendChild(li);
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

    const media = document.createElement('div');
    media.className = 'media-frame post-card-media';
    if (item.imageUrl) {
      media.appendChild(createImage(item, index));
    } else if (window.EditorialImages) {
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

  function loadFeed() {
    showSkeletons();
    ul.setAttribute('aria-busy', 'true');

    return fetch(basePath() + 'feed.json')
      .then(function (r) {
        return r.ok ? r.json() : Promise.reject(new Error('Feed unavailable'));
      })
      .then(function (data) {
        const items = data.items || [];
        ul.innerHTML = '';
        ul.setAttribute('aria-busy', 'false');

        if (countEl) {
          countEl.textContent = items.length ? items.length + ' issues' : '';
        }

        if (!items.length) {
          showError('No posts yet.');
          return;
        }

        items.forEach(function (item, i) {
          ul.appendChild(createCard(item, i));
        });

        if (window.EditorialImages) {
          window.EditorialImages.init(ul);
        }
      })
      .catch(function () {
        showError('Could not load the latest issues.', loadFeed);
      });
  }

  loadFeed();
})();
