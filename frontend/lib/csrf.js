/**
 * Integracao de CSRF entre o HTMX e o Django.
 *
 * O Django rejeita toda request unsafe sem o token; o base.html expoe o valor
 * em <meta name="csrf-token">.
 */

const META_SELECTOR = 'meta[name="csrf-token"]';

export const CSRF_HEADER = "X-CSRFToken";

/** Le o token do <meta>, ou null quando a pagina nao o expoe. */
export function readCsrfToken(doc = document) {
  return doc.querySelector(META_SELECTOR)?.content || null;
}

/** Escreve o header no objeto de headers, se houver token. Devolve o mesmo objeto. */
export function withCsrfHeader(headers, doc = document) {
  const token = readCsrfToken(doc);

  if (token) {
    headers[CSRF_HEADER] = token;
  }

  return headers;
}

/** Liga o handler ao evento que o HTMX dispara antes de cada request. */
export function registerCsrfHeader(target = document, doc = document) {
  const handler = (event) => withCsrfHeader(event.detail.headers, doc);

  target.addEventListener("htmx:configRequest", handler);

  return handler;
}
