import { describe, expect, it } from "vitest";

import { controllerIdentifier } from "./stimulus-identifier.js";

describe("controllerIdentifier", () => {
  it("deriva o identificador de um controller simples", () => {
    expect(controllerIdentifier("./hello_controller.js")).toBe("hello");
  });

  it("troca underscore por hifen em nomes compostos", () => {
    expect(controllerIdentifier("./date_picker_controller.js")).toBe("date-picker");
  });

  it("funciona sem o prefixo relativo", () => {
    expect(controllerIdentifier("hello_controller.js")).toBe("hello");
  });
});
