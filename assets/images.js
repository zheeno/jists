/**
 * Shared editorial image utilities: fallback handling and lazy init.
 */
(function (global) {
  var FALLBACK_CLASS = 'media-frame--fallback';
  var IMAGE_CLASS = 'editorial-image';

  function placeholderUrl() {
    var base = document.querySelector('link[rel="icon"]');
    var root = '';
    if (base && base.href) {
      root = base.href.replace(/assets\/favicon\.svg.*$/, '');
    }
    return root + 'assets/image-placeholder.svg';
  }

  function getFrame(img) {
    return img.closest('.media-frame');
  }

  function applyFallback(img) {
    if (img.dataset.fallbackApplied === 'true') return;

    var frame = getFrame(img);
    img.dataset.fallbackApplied = 'true';
    img.classList.add(IMAGE_CLASS + '--failed');
    img.removeAttribute('srcset');
    img.src = placeholderUrl();
    img.alt = img.getAttribute('data-fallback-alt') || img.alt || 'Image unavailable';

    if (frame) {
      frame.classList.add(FALLBACK_CLASS);
      frame.setAttribute('aria-label', img.alt);
    }
  }

  function attach(img) {
    if (!img || img.dataset.editorialBound === 'true') return img;

    img.dataset.editorialBound = 'true';
    img.classList.add(IMAGE_CLASS);

    img.addEventListener(
      'error',
      function () {
        applyFallback(img);
      },
      { once: true }
    );

    if (img.complete && img.naturalWidth === 0 && img.src) {
      applyFallback(img);
    }

    return img;
  }

  function createImage(options) {
    var img = document.createElement('img');
    img.className = IMAGE_CLASS + (options.className ? ' ' + options.className : '');
    img.alt = options.alt || '';
    img.loading = options.loading || 'lazy';
    img.decoding = 'async';
    img.dataset.editorialImage = 'true';
    if (options.fallbackAlt) img.dataset.fallbackAlt = options.fallbackAlt;
    if (options.src) img.src = options.src;
    if (options.fetchPriority) img.fetchPriority = options.fetchPriority;
    return attach(img);
  }

  function init(root) {
    var scope = root || document;
    scope.querySelectorAll('[data-editorial-image], img.' + IMAGE_CLASS).forEach(attach);
    scope.querySelectorAll('.editorial-content img').forEach(attach);
  }

  global.EditorialImages = {
    attach: attach,
    create: createImage,
    init: init,
    applyFallback: applyFallback,
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      init(document);
    });
  } else {
    init(document);
  }
})(window);
