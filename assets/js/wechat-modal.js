(function () {
  "use strict";

  function initWeChatModal() {
    var modal = document.getElementById("wechat-modal");
    if (!modal) return;

    var dialog = modal.querySelector(".wechat-modal__dialog");
    var openers = document.querySelectorAll("[data-wechat-open]");
    var closers = modal.querySelectorAll("[data-wechat-close]");
    var lastFocused = null;

    function openModal(event) {
      if (event) event.preventDefault();
      lastFocused = document.activeElement;
      modal.hidden = false;
      document.body.classList.add("wechat-modal-open");
      dialog.focus();
    }

    function closeModal(event) {
      if (event) event.preventDefault();
      modal.hidden = true;
      document.body.classList.remove("wechat-modal-open");
      if (lastFocused && typeof lastFocused.focus === "function") {
        lastFocused.focus();
      }
    }

    Array.prototype.forEach.call(openers, function (opener) {
      opener.addEventListener("click", openModal);
    });

    Array.prototype.forEach.call(closers, function (closer) {
      closer.addEventListener("click", closeModal);
    });

    document.addEventListener("keydown", function (event) {
      if (!modal.hidden && event.key === "Escape") {
        closeModal(event);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initWeChatModal);
  } else {
    initWeChatModal();
  }
})();
