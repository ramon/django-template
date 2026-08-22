import { Application } from "@hotwired/stimulus";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import ThemeController from "./theme_controller.js";

let application;

function mount(html) {
  document.body.innerHTML = html;

  application = Application.start();
  application.register("theme", ThemeController);

  // o Stimulus conecta os controllers num microtask
  return new Promise((resolve) => setTimeout(resolve, 0));
}

describe("theme controller", () => {
  beforeEach(async () => {
    document.documentElement.classList.remove("dark");
    localStorage.clear();

    await mount(`<button data-controller="theme" data-action="theme#toggle">alternar</button>`);
  });

  afterEach(() => {
    application?.stop();
    document.body.innerHTML = "";
    document.documentElement.classList.remove("dark");
    localStorage.clear();
  });

  it("liga o tema escuro e guarda a escolha", () => {
    document.querySelector("button").click();

    expect(document.documentElement.classList.contains("dark")).toBe(true);
    expect(localStorage.getItem("theme")).toBe("dark");
  });

  it("desliga o tema escuro e guarda a escolha", () => {
    document.documentElement.classList.add("dark");

    document.querySelector("button").click();

    expect(document.documentElement.classList.contains("dark")).toBe(false);
    expect(localStorage.getItem("theme")).toBe("light");
  });
});
