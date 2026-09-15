// @vitest-environment node
import { spawnSync } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { afterAll, describe, expect, it } from "vitest";

// Roda o Biome de verdade, com o biome.json e o plugin do projeto: o teste protege a
// convencao real, nao uma copia das regras.
const root = fileURLToPath(new URL("../..", import.meta.url));
const biome = path.join(root, "node_modules", ".bin", "biome");

// dentro de frontend/ porque o Biome ignora arquivo fora de files.includes
const workdir = mkdtempSync(path.join(root, "frontend", ".bem-test-"));
afterAll(() => rmSync(workdir, { recursive: true, force: true }));

let counter = 0;

function diagnosticos(code) {
  counter += 1;
  const file = path.join(workdir, `teste-${counter}.css`);
  writeFileSync(file, code);

  const { stdout } = spawnSync(biome, ["lint", "--reporter=github", file], {
    cwd: root,
    encoding: "utf8",
  });

  // uma linha por diagnostico: ::error title=<regra>,file=...::<mensagem>
  return stdout
    .split("\n")
    .filter((line) => line.startsWith("::"))
    .map((line) => {
      const [, rule, message] = line.match(/title=([^,]+),.*?::(.*)$/);
      return rule === "plugin" ? `plugin: ${message.split(":")[0]}` : rule;
    });
}

const BEM = "plugin: Classe fora do padrao BEM";

describe("convencao BEM no CSS", () => {
  it.each([
    [".card", "bloco"],
    [".user-profile", "bloco em kebab-case"],
    [".card__title", "elemento"],
    [".user-profile__avatar-image", "elemento em kebab-case"],
    [".card--featured", "modificador"],
    [".card__title--muted", "elemento com modificador"],
  ])("aceita %s (%s)", (selector) => {
    expect(diagnosticos(`${selector} { color: red; }`)).toEqual([]);
  });

  it.each([
    [".Card", "PascalCase"],
    [".cardTitle", "camelCase"],
    [".card_title", "underscore simples em vez de duplo"],
    [".card__title__deep", "elemento aninhado"],
    [".card--featured--extra", "modificador duplicado"],
    [".CARD", "maiusculas"],
  ])("rejeita %s (%s)", (selector) => {
    expect(diagnosticos(`${selector} { color: red; }`)).toEqual([BEM]);
  });

  it("aceita o @import do tailwind sem reclamar", () => {
    expect(diagnosticos('@import "tailwindcss";')).toEqual([]);
  });

  it("valida classes dentro de seletores aninhados", () => {
    expect(diagnosticos(".card { & .card__Title { color: red; } }")).toEqual([BEM]);
  });

  it("rejeita o sufixo com & do Sass, que o CSS nativo compila para outro seletor", () => {
    // `.card { &__title {} }` vira `__title.card` no Lightning CSS, nao `.card__title`
    expect(diagnosticos(".card { &__title { color: red; } }")).toEqual([
      "lint/correctness/noUnknownTypeSelector",
    ]);
  });

  it("exige kebab-case tambem em keyframes", () => {
    expect(diagnosticos("@keyframes fadeIn { from { opacity: 0; } }")).toEqual([
      "plugin: Nome de keyframes deve ser kebab-case",
    ]);
  });
});
