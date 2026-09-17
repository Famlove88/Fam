/* قوائم الناخبين – بر الياس – service worker
   cache prefix "famvote-" : on activate we delete ONLY our own old caches,
   never sibling apps' caches on the same GitHub Pages origin. */
var VERSION = 'famvote-v2';
var PRECACHE = ['./', './index.html', './data.js', './manifest.json', './icon-192.png', './icon-512.png'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(VERSION).then(function (c) { return c.addAll(PRECACHE); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k.indexOf('famvote-') === 0 && k !== VERSION; })
                          .map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  var isFont = url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com';
  if (url.origin !== self.location.origin && !isFont) return;

  var isApp = url.origin === self.location.origin && /(\/|index\.html|data\.js|manifest\.json)$/.test(url.pathname);
  if (isApp) {
    // index.html / data.js: network first so a regenerated list shows right away; cache is the offline fallback
    e.respondWith(fetch(req).then(function (res) {
      if (res && res.ok) { var copy = res.clone(); caches.open(VERSION).then(function (c) { c.put(req, copy); }); }
      return res;
    }).catch(function () { return caches.match(req, { ignoreSearch: true }); }));
    return;
  }
  // icons and fonts: cache first
  e.respondWith(caches.match(req, { ignoreSearch: true }).then(function (cached) {
    return cached || fetch(req).then(function (res) {
      // opaque responses (no-cors fonts) have res.ok === false but are still cacheable
      if (res && (res.ok || res.type === 'opaque')) { var copy = res.clone(); caches.open(VERSION).then(function (c) { c.put(req, copy); }); }
      return res;
    });
  }));
});
