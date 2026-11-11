document.addEventListener("DOMContentLoaded", () => {
  // Drawer (menu latéral)
  const btn = document.getElementById("menu-btn");
  const drawer = document.getElementById("drawer");
  const overlay = document.getElementById("overlay");

  const setOpen = (open) => {
    drawer.classList.toggle("open", open);
    overlay.classList.toggle("show", open);
    btn.setAttribute("aria-expanded", String(open));
    drawer.setAttribute("aria-hidden", String(!open));
  };

  btn.addEventListener("click", () => setOpen(!drawer.classList.contains("open")));
  overlay.addEventListener("click", () => setOpen(false));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") setOpen(false); });

  // Bandeau cookies (cookie technique, pas de localStorage)
  const banner = document.getElementById("cookie-banner");
  const ok = document.getElementById("cookie-ok");
  if (!document.cookie.includes("fase_cookies=1")) banner.hidden = false;
  ok.addEventListener("click", () => {
    document.cookie = "fase_cookies=1; path=/; max-age=31536000; SameSite=Lax";
    banner.hidden = true;
  });
});
