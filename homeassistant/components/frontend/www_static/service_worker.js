"use strict";function setOfCachedUrls(e){return e.keys().then(function(e){return e.map(function(e){return e.url})}).then(function(e){return new Set(e)})}function notificationEventCallback(e,t){firePushCallback({action:t.action,data:t.notification.data,tag:t.notification.tag,type:e},t.notification.data.jwt)}function firePushCallback(e,t){delete e.data.jwt,0===Object.keys(e.data).length&&e.data.constructor===Object&&delete e.data,fetch("/api/notify.html5/callback",{method:"POST",headers:new Headers({"Content-Type":"application/json",Authorization:"Bearer "+t}),body:JSON.stringify(e)})}var precacheConfig=[["/","086804a336aa449a8d369b38edd8e1e4"],["/frontend/panels/dev-event-5c82300b3cf543a92cf4297506e450e7.html","1bb68c3df5c14307a2550a0cca39b435"],["/frontend/panels/dev-info-1e305a9af8fd6e7be77f3ddf215c336f.html","c030fa0f7ea7b36610efde8c01091286"],["/frontend/panels/dev-service-9f749635e518a4ca7991975bdefdb10a.html","1bc71eb7620c7b7198fd4b7976d6bc13"],["/frontend/panels/dev-state-7d069ba8fd5379fa8f59858b8c0a7473.html","18694d76e03e1194c734e9819923b70b"],["/frontend/panels/dev-template-2b618508510afa5281c9ecae0c3a3dbd.html","554e7f893ab24c8548813382142207d4"],["/frontend/panels/map-9c8c7924ba8f731560c9f4093835cc26.html","8ae4874622d23d995ddf2a8b0ffa8d80"],["/static/core-adfeb513cf650acf763e284d76a48d6b.js","f5fdf5f1f754e801f9f54ad31a3cc922"],["/static/frontend-55ad0c8eb7ae154187303cc371f61136.html","c767cf69cc737ca63344530b2ef2620a"],["/static/mdi-c1dde43ccf5667f687c418fc8daf9668.html","6a3c9317736ca26e3390316335be9ba5"],["static/fonts/roboto/Roboto-Bold.ttf","d329cc8b34667f114a95422aaad1b063"],["static/fonts/roboto/Roboto-Light.ttf","7b5fb88f12bec8143f00e21bc3222124"],["static/fonts/roboto/Roboto-Medium.ttf","fe13e4170719c2fc586501e777bde143"],["static/fonts/roboto/Roboto-Regular.ttf","ac3f799d5bbaf5196fab15ab8de8431c"],["static/icons/favicon-192x192.png","419903b8422586a7e28021bbe9011175"],["static/icons/favicon.ico","04235bda7843ec2fceb1cbe2bc696cf4"],["static/images/card_media_player_bg.png","a34281d1c1835d338a642e90930e61aa"],["static/webcomponents-lite.min.js","32b5a9b7ada86304bec6b43d3f2194f0"]],cacheName="sw-precache-v2--"+(self.registration?self.registration.scope:""),ignoreUrlParametersMatching=[/^utm_/],addDirectoryIndex=function(e,t){var a=new URL(e);return"/"===a.pathname.slice(-1)&&(a.pathname+=t),a.toString()},createCacheKey=function(e,t,a,n){var c=new URL(e);return n&&c.toString().match(n)||(c.search+=(c.search?"&":"")+encodeURIComponent(t)+"="+encodeURIComponent(a)),c.toString()},isPathWhitelisted=function(e,t){if(0===e.length)return!0;var a=new URL(t).pathname;return e.some(function(e){return a.match(e)})},stripIgnoredUrlParameters=function(e,t){var a=new URL(e);return a.search=a.search.slice(1).split("&").map(function(e){return e.split("=")}).filter(function(e){return t.every(function(t){return!t.test(e[0])})}).map(function(e){return e.join("=")}).join("&"),a.toString()},hashParamName="_sw-precache",urlsToCacheKeys=new Map(precacheConfig.map(function(e){var t=e[0],a=e[1],n=new URL(t,self.location),c=createCacheKey(n,hashParamName,a,!1);return[n.toString(),c]}));self.addEventListener("install",function(e){e.waitUntil(caches.open(cacheName).then(function(e){return setOfCachedUrls(e).then(function(t){return Promise.all(Array.from(urlsToCacheKeys.values()).map(function(a){if(!t.has(a))return e.add(new Request(a,{credentials:"same-origin",redirect:"follow"}))}))})}).then(function(){return self.skipWaiting()}))}),self.addEventListener("activate",function(e){var t=new Set(urlsToCacheKeys.values());e.waitUntil(caches.open(cacheName).then(function(e){return e.keys().then(function(a){return Promise.all(a.map(function(a){if(!t.has(a.url))return e.delete(a)}))})}).then(function(){return self.clients.claim()}))}),self.addEventListener("fetch",function(e){if("GET"===e.request.method){var t,a=stripIgnoredUrlParameters(e.request.url,ignoreUrlParametersMatching);t=urlsToCacheKeys.has(a);var n="index.html";!t&&n&&(a=addDirectoryIndex(a,n),t=urlsToCacheKeys.has(a));var c="/";!t&&c&&"navigate"===e.request.mode&&isPathWhitelisted(["^((?!(static|api|local|service_worker.js|manifest.json)).)*$"],e.request.url)&&(a=new URL(c,self.location).toString(),t=urlsToCacheKeys.has(a)),t&&e.respondWith(caches.open(cacheName).then(function(e){return e.match(urlsToCacheKeys.get(a)).then(function(e){if(e)return e;throw Error("The cached response that was expected is missing.")})}).catch(function(t){return console.warn('Couldn\'t serve response for "%s" from cache: %O',e.request.url,t),fetch(e.request)}))}}),self.addEventListener("push",function(e){var t;e.data&&(t=e.data.json(),e.waitUntil(self.registration.showNotification(t.title,t).then(function(e){firePushCallback({type:"received",tag:t.tag,data:t.data},t.data.jwt)})))}),self.addEventListener("notificationclick",function(e){var t;notificationEventCallback("clicked",e),e.notification.close(),e.notification.data&&e.notification.data.url&&(t=e.notification.data.url,t&&e.waitUntil(clients.matchAll({type:"window"}).then(function(e){var a,n;for(a=0;a<e.length;a++)if(n=e[a],n.url===t&&"focus"in n)return n.focus();if(clients.openWindow)return clients.openWindow(t)})))}),self.addEventListener("notificationclose",function(e){notificationEventCallback("closed",e)});