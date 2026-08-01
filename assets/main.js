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

  function showSkeletons() {
    ul.innerHTML = '';
    for (let i = 0; i < 4; i++) {
      const li = document.createElement('li');
      li.className = 'skeleton-card' + (i === 0 ? ' md:col-span-7' : ' md:col-span-5');
      li.innerHTML =
        '<div class="skeleton-line skeleton-line--short"></div>' +
        '<div class="skeleton-line skeleton-line--title"></div>' +
        '<div class="skeleton-line skeleton-line--title2"></div>';
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

    const meta = document.createElement('p');
    meta.className = 'post-card-meta';
    meta.textContent = item.date + ' · ' + (item.source || 'newsletter');

    const title = document.createElement('h3');
    title.className = 'post-card-title';
    title.textContent = item.title;

    a.appendChild(meta);
    a.appendChild(title);

    if (isFeatured && item.excerpt) {
      const excerpt = document.createElement('p');
      excerpt.className = 'post-card-excerpt';
      excerpt.textContent = item.excerpt;
      a.appendChild(excerpt);
    }

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
        ul.innerHTML = '<li class="col-span-full" style="color: var(--color-ink-muted); font-size: 0.875rem;">No posts yet.</li>';
        return;
      }

      items.forEach(function (item, i) {
        ul.appendChild(createCard(item, i));
      });
    })
    .catch(function () {
      ul.innerHTML = '<li style="color: var(--color-ink-muted); font-size: 0.875rem;">Could not load posts. Check feed.json.</li>';
      ul.setAttribute('aria-busy', 'false');
    });
})();
