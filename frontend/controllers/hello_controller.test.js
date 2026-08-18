import { Application } from "@hotwired/stimulus";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import HelloController from "./hello_controller.js";

let application;

function mount(html) {
  document.body.innerHTML = html;

  application = Application.start();
  application.register("hello", HelloController);

  // o Stimulus conecta os controllers num microtask
  return new Promise((resolve) => setTimeout(resolve, 0));
}

describe("hello controller", () => {
  beforeEach(async () => {
    await mount(`
      <div data-controller="hello">
        <input data-hello-target="name" value="Ramon">
        <button data-action="hello#greet">Cumprimentar</button>
        <span data-hello-target="output"></span>
      </div>
    `);
  });

  afterEach(() => {
    application?.stop();
    document.body.innerHTML = "";
  });

  it("escreve a saudacao ao acionar", () => {
    document.querySelector("button").click();

    expect(document.querySelector("[data-hello-target='output']").textContent).toBe("Ola, Ramon!");
  });

  it("reflete o valor atual do input", () => {
    document.querySelector("input").value = "Maria";
    document.querySelector("button").click();

    expect(document.querySelector("[data-hello-target='output']").textContent).toBe("Ola, Maria!");
  });

  it("nao escreve nada antes do acionamento", () => {
    expect(document.querySelector("[data-hello-target='output']").textContent).toBe("");
  });
});
