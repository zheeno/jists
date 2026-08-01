/**
 * Read Next related articles on article detail pages.
 */
(function () {
  const container = document.getElementById('read-next-posts');
  const feed = window.EditorialFeed;

  if (!container || !feed) return;

  const currentUrl = container.dataset.currentUrl || '';
  const currentCategory = container.dataset.currentCategory || '';
  const limit = Number(container.dataset.limit || 4);

  function showSkeletons() {
    container.innerHTML = '';
    container.setAttribute('aria-busy', 'true');
    for (let i = 0; i < limit; i++) {
      container.appendChild(feed.createSkeletonCard({ uniform: true }));
    }
  }

  function showMessage(message) {
    container.innerHTML = '';
    container.setAttribute('aria-busy', 'false');
    const li = document.createElement('li');
    li.className = 'read-next-empty';
    li.textContent = message;
    container.appendChild(li);
  }

  function renderRelated(items) {
    container.innerHTML = '';
    container.setAttribute('aria-busy', 'false');

    if (!items.length) {
      showMessage('No related articles right now.');
      return;
    }

    items.forEach(function (item, index) {
      container.appendChild(
        feed.createCard(item, {
          index: index,
          uniform: true,
        })
      );
    });

    if (window.EditorialImages) {
      window.EditorialImages.init(container);
    }
  }

  showSkeletons();

  feed
    .fetchFeed()
    .then(function (data) {
      const related = feed.getRelatedArticles(
        data.items || [],
        currentUrl,
        currentCategory,
        limit
      );
      renderRelated(related);
    })
    .catch(function () {
      showMessage('Could not load related articles.');
    });
})();
