/* قوائم الناخبين – service worker
   cache prefix "famvote-" : on activate we delete ONLY our own old caches,
   never sibling apps' caches on the same GitHub Pages origin.
   v4: encrypted data (.enc) + Firebase SDK caching. The data files are encrypted, so caching them is safe;
       the key only ever lives in Firestore and is read after signing in. */
var VERSION = 'famvote-v4';
var PRECACHE = ['./', './index.html', './admin.html', './manifest.json', './icon-192.png', './icon-512.png'];
// البيانات المشفّرة: منخزّنها عند التثبيت إذا موجودة (best effort) حتى يفتح البرنامج من دون نت من بعد أول زيارة
var OPTIONAL = ['./towns.enc', './data.enc'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(VERSION).then(function (c) {
    return c.addAll(PRECACHE).then(function () {
      return Promise.all(OPTIONAL.map(function (u) { return c.add(new Request(u, { cache: 'no-cache' })).catch(function () {}); }));
    });
  }).then(function () { return self.skipWaiting(); }));
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
  var same = url.origin === self.location.origin;
  var isFont = url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com';
  var isSdk = url.hostname === 'www.gstatic.com' && url.pathname.indexOf('/firebasejs/') === 0;
  // Firebase Auth/Firestore API calls (googleapis.com) and anything else cross-origin: never intercepted
  if (!same && !isFont && !isSdk) return;

  // الصفحات وملفات البيانات المشفّرة (data.enc, towns.enc, towns/*.enc): من النت أولاً حتى تظهر القوائم الجديدة فوراً،
  // والنسخة المخزّنة هي الاحتياط لما ما في إنترنت
  var isApp = same && (/(\/|\.html|\.enc|manifest\.json)$/.test(url.pathname) || url.pathname.indexOf('/towns/') >= 0);
  if (isApp) {
    // cache:'no-cache' = يسأل السيرفر إذا في نسخة أجدد بدل ما يرضى بنسخة المتصفح القديمة
    e.respondWith(fetch(req, { cache: 'no-cache' }).then(function (res) {
      if (res && res.ok) { var copy = res.clone(); caches.open(VERSION).then(function (c) { c.put(req, copy); }); }
      return res;
    }).catch(function () {
      return caches.match(req, { ignoreSearch: true }).then(function (cached) {
        return cached || new Response('', { status: 503, statusText: 'offline' });
      });
    }));
    return;
  }
  // icons, fonts and the Firebase SDK (versioned URLs): cache first
  e.respondWith(caches.match(req, { ignoreSearch: true }).then(function (cached) {
    return cached || fetch(req).then(function (res) {
      // opaque responses (no-cors fonts) have res.ok === false but are still cacheable
      if (res && (res.ok || res.type === 'opaque')) { var copy = res.clone(); caches.open(VERSION).then(function (c) { c.put(req, copy); }); }
      return res;
    });
  }));
});
