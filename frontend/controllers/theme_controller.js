import { Controller } from "@hotwired/stimulus";

const STORAGE_KEY = "theme";

/**
 * Alterna entre os temas claro e escuro (classe `.dark` na raiz do documento) e
 * lembra a escolha em `localStorage`. O estado inicial é decidido por um script
 * inline em `templates/layouts/base.html`, antes deste controller carregar, para
 * não haver flash do tema errado.
 *
 *   <button data-controller="theme" data-action="theme#toggle">alternar tema</button>
 */
export default class extends Controller {
  toggle() {
    const isDark = document.documentElement.classList.toggle("dark");

    localStorage.setItem(STORAGE_KEY, isDark ? "dark" : "light");
  }
}
