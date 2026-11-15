/* FASE · UPC — interactions : thème, menu mobile, révélation, cookies */
(function () {
  "use strict";

  var root = document.documentElement;

  /* ---------- Thème clair / sombre ---------- */
  var themeBtn = document.getElementById("themeToggle");
  function setTheme(theme) {
    root.setAttribute("data-theme", theme);
    if (themeBtn) {
      themeBtn.setAttribute("aria-label", theme === "dark" ? "Passer au thème clair" : "Passer au thème sombre");
    }
    try { localStorage.setItem("fase-theme", theme); } catch (e) {}
  }
  if (themeBtn) {
    setTheme(root.getAttribute("data-theme") || "light");
    themeBtn.addEventListener("click", function () {
      setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });
  }

  /* ---------- Menu mobile ---------- */
  var nav = document.getElementById("mainNav");
  var menuBtn = document.getElementById("menuToggle");
  var scrim = document.getElementById("scrim");

  function setMenu(open) {
    if (!nav || !menuBtn) return;
    nav.classList.toggle("open", open);
    if (scrim) scrim.classList.toggle("show", open);
    menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.setAttribute("aria-label", open ? "Fermer le menu" : "Ouvrir le menu");
  }
  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      setMenu(!nav.classList.contains("open"));
    });
  }
  if (scrim) scrim.addEventListener("click", function () { setMenu(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
  window.addEventListener("resize", function () {
    if (window.innerWidth > 920) setMenu(false);
  });

  /* ---------- Révélation au défilement ---------- */
  var items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------- Bandeau cookies (cookie technique) ---------- */
  var banner = document.getElementById("cookie-banner");
  var okBtn = document.getElementById("cookie-ok");
  if (banner && document.cookie.indexOf("fase_cookies=1") === -1) {
    banner.hidden = false;
  }
  if (okBtn) {
    okBtn.addEventListener("click", function () {
      document.cookie = "fase_cookies=1; path=/; max-age=31536000; SameSite=Lax";
      if (banner) banner.hidden = true;
    });
  }
})();
