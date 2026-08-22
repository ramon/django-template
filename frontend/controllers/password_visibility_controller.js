import { Controller } from "@hotwired/stimulus";

/**
 * Alterna um campo de senha entre `type="password"` e `type="text"`, com um par
 * de ícones (mostrar/ocultar) que troca de visibilidade junto. Ligado por
 * `<c-ui.field type="password">` (`apps/ui/templates/components/ui/field.html`).
 *
 *   <div data-controller="password-visibility">
 *     <input type="password" data-password-visibility-target="input">
 *     <button data-action="password-visibility#toggle">
 *       <svg data-password-visibility-target="showIcon">...</svg>
 *       <svg data-password-visibility-target="hideIcon" class="hidden">...</svg>
 *     </button>
 *   </div>
 */
export default class extends Controller {
  static targets = ["input", "showIcon", "hideIcon"];

  toggle() {
    const isHidden = this.inputTarget.type === "password";

    this.inputTarget.type = isHidden ? "text" : "password";
    this.showIconTarget.classList.toggle("hidden", isHidden);
    this.hideIconTarget.classList.toggle("hidden", !isHidden);
  }
}
