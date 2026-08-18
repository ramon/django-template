// @vitest-environment node
import { fileURLToPath } from "node:url";

import stylelint from "stylelint";
import { describe, expect, it } from "vitest";

// Aponta para a config real do projeto: o teste protege a convenca~o de verdade,
// nao uma copia das regras.
const configFile = fileURLToPath(new URL("../../.stylelintrc.json", import.meta.url));

async function classesRejeitadas(code) {
  const { results } = await stylelint.lint({ code, configFile, codeFilename: "teste.css" });

  return results[0].warnings.map((warning) => warning.rule);
}

describe("convencao BEM no CSS", () => {
  it.each([
    [".card", "bloco"],
    [".user-profile", "bloco em kebab-case"],
    [".card__title", "elemento"],
    [".user-profile__avatar-image", "elemento em kebab-case"],
    [".card--featured", "modificador"],
    [".card__title--muted", "elemento com modificador"],
  ])("aceita %s (%s)", async (selector) => {
    expect(await classesRejeitadas(`${selector} { color: red; }`)).toEqual([]);
  });

  it.each([
    [".Card", "PascalCase"],
    [".cardTitle", "camelCase"],
    [".card_title", "underscore simples em vez de duplo"],
    [".card__title__deep", "elemento aninhado"],
    [".card--featured--extra", "modificador duplicado"],
    [".CARD", "maiusculas"],
  ])("rejeita %s (%s)", async (selector) => {
    expect(await classesRejeitadas(`${selector} { color: red; }`)).toEqual([
      "selector-class-pattern",
    ]);
  });

  it("aceita o @import do tailwind sem reclamar", async () => {
    expect(await classesRejeitadas('@import "tailwindcss";')).toEqual([]);
  });

  it("valida classes dentro de seletores aninhados", async () => {
    const code = ".card { &__title { color: red; } }";

    expect(await classesRejeitadas(code)).toEqual([]);
  });

  it("exige kebab-case tambem em keyframes", async () => {
    const code = "@keyframes fadeIn { from { opacity: 0; } }";

    expect(await classesRejeitadas(code)).toEqual(["keyframes-name-pattern"]);
  });
});
