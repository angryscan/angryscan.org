/* Detect browser language, redirect to preferred locale, and remember user choice. */
(function () {
  var storageKey = "angryscan.docs.preferredLanguage";
  var supported = ["en", "ru"];
  var defaultLanguage = "en";

  var path = window.location.pathname;
  if (path.endsWith("index.html")) {
    path = path.slice(0, -10);
  }
  if (path.length > 1 && path.endsWith("/")) {
    path = path.slice(0, -1);
  }

  var segments = path.split("/").filter(function (segment) {
    return segment.length > 0;
  });
  var languageIndex = -1;

  for (var i = 0; i < segments.length; i += 1) {
    if (supported.indexOf(segments[i]) !== -1) {
      languageIndex = i;
      break;
    }
  }

  var prefixSegments = languageIndex >= 0 ? segments.slice(0, languageIndex) : segments;
  var currentLanguage =
    languageIndex >= 0 ? segments[languageIndex] : document.documentElement.lang || defaultLanguage;

  var basePath = "/";
  if (prefixSegments.length > 0) {
    basePath += prefixSegments.join("/") + "/";
  }

  function persistLanguage(lang) {
    try {
      window.localStorage.setItem(storageKey, lang);
    } catch (error) {
      /* localStorage might be unavailable (e.g., private mode). Ignore failures. */
    }
  }

  function readStoredLanguage() {
    try {
      var stored = window.localStorage.getItem(storageKey);
      if (stored && supported.indexOf(stored) !== -1) {
        return stored;
      }
    } catch (error) {
      return null;
    }
    return null;
  }

  function resolveNavigatorLanguage() {
    var navigatorLanguages = [];
    if (Array.isArray(navigator.languages)) {
      navigatorLanguages = navigator.languages.slice();
    } else if (navigator.language) {
      navigatorLanguages = [navigator.language];
    } else if (navigator.userLanguage) {
      navigatorLanguages = [navigator.userLanguage];
    }

    for (var i = 0; i < navigatorLanguages.length; i += 1) {
      var language = navigatorLanguages[i];
      if (!language) {
        continue;
      }
      var normalized = language.toLowerCase().split("-")[0];
      if (supported.indexOf(normalized) !== -1) {
        return normalized;
      }
    }
    return defaultLanguage;
  }

  function buildLocalizedPath(lang) {
    return basePath + lang + "/";
  }

  if (languageIndex >= 0) {
    persistLanguage(currentLanguage);
    return;
  }

  var preferredLanguage = readStoredLanguage() || resolveNavigatorLanguage();
  if (supported.indexOf(preferredLanguage) === -1) {
    preferredLanguage = defaultLanguage;
  }
  if (preferredLanguage === currentLanguage) {
    return;
  }

  persistLanguage(preferredLanguage);
  var target = buildLocalizedPath(preferredLanguage) + window.location.search + window.location.hash;
  if (target !== window.location.pathname + window.location.search + window.location.hash) {
    window.location.replace(target);
  }
})();
