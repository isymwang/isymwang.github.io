(function () {
  'use strict';
  function setLanguage(language, save) {
    language = language === 'zh' ? 'zh' : 'en';
    document.documentElement.dataset.language = language;
    document.documentElement.lang = language === 'zh' ? 'zh-CN' : 'en';
    document.querySelectorAll('[data-set-language]').forEach(function (button) {
      button.setAttribute('aria-pressed', String(button.dataset.setLanguage === language));
    });
    document.querySelectorAll('[data-en-label]').forEach(function (element) {
      element.setAttribute('aria-label', element.getAttribute('data-' + language + '-label'));
    });
    if (save) {
      try { localStorage.setItem('homepage-language', language); } catch (error) {}
      try {
        var url = new URL(location.href);
        url.searchParams.set('lang', language);
        history.replaceState(null, '', url.href);
      } catch (error) {}
    }
    document.dispatchEvent(new CustomEvent('languagechange', { detail: { language: language } }));
  }
  document.querySelectorAll('[data-set-language]').forEach(function (button) {
    button.addEventListener('click', function () { setLanguage(button.dataset.setLanguage, true); });
  });
  setLanguage(document.documentElement.dataset.language, false);
  document.querySelectorAll('a[href]').forEach(function (link) {
    if (/^https?:/.test(link.href) && new URL(link.href).origin !== location.origin) {
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
    }
  });
})();
