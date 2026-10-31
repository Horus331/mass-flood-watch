/* Mass Flood Watch service worker: app-shell only. Every request goes to the network first, so data and pages are never stale;
   the cached shell (viewer, styles, icons) is only a fallback when the phone is offline. Model data (site/data/) is never cached. */
var SHELL = 'mfw-shell-v4';
var FILES = ['viewer.html', 'about.html', 'site/viewer.js', 'site/viewer.css', 'wpi-logo.svg', 'icon-192.png', 'icon-512.png', 'manifest.webmanifest'];
self.addEventListener('install', function (e) { e.waitUntil(caches.open(SHELL).then(function (c) { return c.addAll(FILES); }).then(function () { return self.skipWaiting(); })); });
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (ks) { return Promise.all(ks.filter(function (k) { return k !== SHELL; }).map(function (k) { return caches.delete(k); })); }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  var u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin || u.pathname.indexOf('/site/data/') >= 0) return;   // data: straight to the network
  // pages and code are revalidated with the server on every load (no 10-minute HTTP cache), so a new version shows on the next reload
  e.respondWith(fetch(e.request, { cache: 'no-cache' }).then(function (r) {
    if (r.ok && FILES.some(function (f) { return u.pathname.endsWith('/' + f); })) { var cp = r.clone(); caches.open(SHELL).then(function (c) { c.put(e.request, cp); }); }
    return r;
  }).catch(function () { return caches.match(e.request, { ignoreSearch: true }); }));
});
