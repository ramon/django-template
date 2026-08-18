import { beforeEach, describe, expect, it } from "vitest";

import { CSRF_HEADER, readCsrfToken, registerCsrfHeader, withCsrfHeader } from "./csrf.js";

const TOKEN = "token-de-teste-123";

function setMeta(value) {
  document.head.innerHTML = value === null ? "" : `<meta name="csrf-token" content="${value}">`;
}

describe("readCsrfToken", () => {
  beforeEach(() => setMeta(TOKEN));

  it("le o token do meta", () => {
    expect(readCsrfToken(document)).toBe(TOKEN);
  });

  it("devolve null quando a pagina nao expoe o meta", () => {
    setMeta(null);

    expect(readCsrfToken(document)).toBeNull();
  });

  it("devolve null quando o meta esta vazio", () => {
    setMeta("");

    expect(readCsrfToken(document)).toBeNull();
  });
});

describe("withCsrfHeader", () => {
  beforeEach(() => setMeta(TOKEN));

  it("acrescenta o header sem descartar os existentes", () => {
    const headers = { "Content-Type": "application/json" };

    expect(withCsrfHeader(headers, document)).toEqual({
      "Content-Type": "application/json",
      [CSRF_HEADER]: TOKEN,
    });
  });

  it("nao inventa header quando nao ha token", () => {
    setMeta(null);

    expect(withCsrfHeader({}, document)).toEqual({});
  });
});

describe("registerCsrfHeader", () => {
  beforeEach(() => setMeta(TOKEN));

  it("preenche os headers no evento que o htmx dispara", () => {
    const target = new EventTarget();
    registerCsrfHeader(target, document);

    const detail = { headers: {} };
    target.dispatchEvent(new CustomEvent("htmx:configRequest", { detail }));

    expect(detail.headers[CSRF_HEADER]).toBe(TOKEN);
  });

  it("ignora outros eventos", () => {
    const target = new EventTarget();
    registerCsrfHeader(target, document);

    const detail = { headers: {} };
    target.dispatchEvent(new CustomEvent("htmx:afterSwap", { detail }));

    expect(detail.headers).toEqual({});
  });
});
