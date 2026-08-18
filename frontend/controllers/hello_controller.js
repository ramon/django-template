import { Controller } from "@hotwired/stimulus";

/**
 * Controller de exemplo, para validar que o Stimulus esta ativo.
 *
 *   <div data-controller="hello">
 *     <input data-hello-target="name" type="text">
 *     <button data-action="hello#greet">Cumprimentar</button>
 *     <span data-hello-target="output"></span>
 *   </div>
 */
export default class extends Controller {
  static targets = ["name", "output"];

  greet() {
    this.outputTarget.textContent = `Ola, ${this.nameTarget.value}!`;
  }
}
