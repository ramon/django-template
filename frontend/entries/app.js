import Alpine from "alpinejs";
import htmx from "htmx.org";

import "../styles/app.css";
import "../controllers";
import { registerCsrfHeader } from "../lib/csrf.js";

// --- HTMX -------------------------------------------------------------------
window.htmx = htmx;
registerCsrfHeader();

// --- Alpine -----------------------------------------------------------------
window.Alpine = Alpine;

// Fragmentos trocados pelo htmx precisam ser inicializados a mao; o Stimulus faz
// isso sozinho via MutationObserver, o Alpine nao.
htmx.onLoad((content) => Alpine.initTree(content));

Alpine.start();
