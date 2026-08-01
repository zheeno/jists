/**
 * Homepage feed with load-more pagination.
 */
(function () {
  const ul = document.getElementById('posts');
  const countEl = document.getElementById('post-count');
  const loadMoreBtn = document.getElementById('load-more');
  const feed = window.EditorialFeed;

  if (!ul || !feed) return;

  const INITIAL_COUNT = 6;
  const BATCH_SIZE = 6;
  const LOAD_DELAY_MS = 280;

  let allItems = [];
  let visibleCount = 0;

  function showSkeletons() {
    ul.innerHTML = '';
    for (let i = 0; i < INITIAL_COUNT; i++) {
      ul.appendChild(feed.createSkeletonCard({ featured: i === 0 }));
    }
  }

  function showError(message, retry) {
    ul.innerHTML = '';
    ul.setAttribute('aria-busy', 'false');
    if (loadMoreBtn) loadMoreBtn.hidden = true;

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

  function renderItems(from, to) {
    for (let i = from; i < to && i < allItems.length; i++) {
      ul.appendChild(
        feed.createCard(allItems[i], {
          index: i,
          featured: i === 0,
        })
      );
    }

    if (window.EditorialImages) {
      window.EditorialImages.init(ul);
    }
  }

  function updateCountLabel() {
    if (!countEl) return;
    if (!allItems.length) {
      countEl.textContent = '';
      return;
    }
    countEl.textContent = 'Showing ' + visibleCount + ' of ' + allItems.length;
  }

  function updateLoadMoreButton() {
    if (!loadMoreBtn) return;

    if (visibleCount >= allItems.length) {
      loadMoreBtn.hidden = true;
      loadMoreBtn.disabled = true;
      return;
    }

    loadMoreBtn.hidden = false;
    loadMoreBtn.disabled = false;
    loadMoreBtn.classList.remove('is-loading');
    loadMoreBtn.textContent = 'Load more';
    loadMoreBtn.setAttribute('aria-label', 'Load more articles');
  }

  function loadMore() {
    if (!loadMoreBtn || visibleCount >= allItems.length) return;

    loadMoreBtn.disabled = true;
    loadMoreBtn.classList.add('is-loading');
    loadMoreBtn.textContent = 'Loading…';

    window.setTimeout(function () {
      const from = visibleCount;
      visibleCount = Math.min(visibleCount + BATCH_SIZE, allItems.length);
      renderItems(from, visibleCount);
      updateCountLabel();
      updateLoadMoreButton();
    }, LOAD_DELAY_MS);
  }

  function initFeed() {
    showSkeletons();
    ul.setAttribute('aria-busy', 'true');

    feed
      .fetchFeed()
      .then(function (data) {
        allItems = data.items || [];
        ul.innerHTML = '';
        ul.setAttribute('aria-busy', 'false');

        if (!allItems.length) {
          showError('No posts yet.');
          return;
        }

        visibleCount = Math.min(INITIAL_COUNT, allItems.length);
        renderItems(0, visibleCount);
        updateCountLabel();
        updateLoadMoreButton();
      })
      .catch(function () {
        showError('Could not load the latest issues.', initFeed);
      });
  }

  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', loadMore);
  }

  initFeed();
})();
