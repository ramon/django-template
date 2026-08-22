import { Application } from "@hotwired/stimulus";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import PasswordVisibilityController from "./password_visibility_controller.js";

let application;

function mount(html) {
  document.body.innerHTML = html;

  application = Application.start();
  application.register("password-visibility", PasswordVisibilityController);

  // o Stimulus conecta os controllers num microtask
  return new Promise((resolve) => setTimeout(resolve, 0));
}

describe("password visibility controller", () => {
  beforeEach(async () => {
    await mount(`
      <div data-controller="password-visibility">
        <input type="password" data-password-visibility-target="input">
        <button data-action="password-visibility#toggle">
          <svg data-password-visibility-target="showIcon"></svg>
          <svg data-password-visibility-target="hideIcon" class="hidden"></svg>
        </button>
      </div>
    `);
  });

  afterEach(() => {
    application?.stop();
    document.body.innerHTML = "";
  });

  it("comeca com o campo oculto e o icone de mostrar visivel", () => {
    expect(document.querySelector("input").type).toBe("password");
    expect(
      document
        .querySelector("[data-password-visibility-target='showIcon']")
        .classList.contains("hidden"),
    ).toBe(false);
    expect(
      document
        .querySelector("[data-password-visibility-target='hideIcon']")
        .classList.contains("hidden"),
    ).toBe(true);
  });

  it("revela o campo e troca os icones ao acionar", () => {
    document.querySelector("button").click();

    expect(document.querySelector("input").type).toBe("text");
    expect(
      document
        .querySelector("[data-password-visibility-target='showIcon']")
        .classList.contains("hidden"),
    ).toBe(true);
    expect(
      document
        .querySelector("[data-password-visibility-target='hideIcon']")
        .classList.contains("hidden"),
    ).toBe(false);
  });

  it("oculta de novo no segundo acionamento", () => {
    document.querySelector("button").click();
    document.querySelector("button").click();

    expect(document.querySelector("input").type).toBe("password");
    expect(
      document
        .querySelector("[data-password-visibility-target='showIcon']")
        .classList.contains("hidden"),
    ).toBe(false);
    expect(
      document
        .querySelector("[data-password-visibility-target='hideIcon']")
        .classList.contains("hidden"),
    ).toBe(true);
  });
});
