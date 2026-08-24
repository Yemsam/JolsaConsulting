const loadPartial = async (selector, url) => {
  const targets = document.querySelectorAll(selector);

  if (!targets.length) {
    return;
  }

  try {
    const response = await fetch(url, { cache: "no-cache" });

    if (!response.ok) {
      throw new Error(`Unable to load ${url}`);
    }

    const html = await response.text();
    targets.forEach((target) => {
      target.outerHTML = html;
    });
  } catch (error) {
    console.error(error);
  }
};

const initNavigation = () => {
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".nav-links");

  if (!toggle || !nav) {
    return;
  }

  const closeMenu = () => {
    nav.classList.remove("open");
    document.body.classList.remove("menu-open");
    toggle.setAttribute("aria-expanded", "false");
  };

  toggle.addEventListener("click", () => {
    const isOpen = nav.classList.toggle("open");
    document.body.classList.toggle("menu-open", isOpen);
    toggle.setAttribute("aria-expanded", String(isOpen));
  });

  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeMenu();
    }
  });
};

const setCurrentYear = () => {
  document.querySelectorAll("[data-current-year]").forEach((target) => {
    target.textContent = new Date().getFullYear();
  });
};

document.addEventListener("DOMContentLoaded", async () => {
  await Promise.all([
    loadPartial("[data-site-header]", "header.html"),
    loadPartial("[data-site-footer]", "footer.html"),
    loadPartial("[data-testimonials]", "testimonials.html"),
  ]);

  initNavigation();
  setCurrentYear();
});

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  });
}
