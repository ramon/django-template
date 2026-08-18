import "../styles/app.css";

import Alpine from "alpinejs";
import htmx from "htmx.org";

import "../controllers";

// --- HTMX -------------------------------------------------------------------
window.htmx = htmx;

// Django rejeita requests unsafe sem o token; o base.html expoe o valor em
// <meta name="csrf-token">.
document.addEventListener("htmx:configRequest", (event) => {
  const token = document.querySelector('meta[name="csrf-token"]')?.content;

  if (token) {
    event.detail.headers["X-CSRFToken"] = token;
  }
});

// --- Alpine -----------------------------------------------------------------
window.Alpine = Alpine;

// Fragmentos trocados pelo htmx precisam ser inicializados a mao; o Stimulus faz
// isso sozinho via MutationObserver, o Alpine nao.
htmx.onLoad((content) => Alpine.initTree(content));

Alpine.start();
