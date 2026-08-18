# 0002. Vite como pipeline de assets, em modo backend integration

- **Status**: Aceito
- **Data**: 2026-08-18
- **Relacionados**: 0003, `docs/standards/frontend.md`

## Contexto

O HTML é renderizado pelo Django (ver [0003](0003-htmx-stimulus-e-alpine-em-vez-de-uma-spa.md)),
mas o CSS e o JS precisam de uma toolchain moderna: Tailwind 4, ES modules, HMR em
desenvolvimento e hash no nome do arquivo em produção. Isso significa dois servidores em
desenvolvimento e um mapeamento estável entre o nome que o template pede e o arquivo que
o build gerou — o problema clássico de integrar bundler com backend server-rendered.

## Decisão

O Vite roda no modo *backend integration* documentado por ele mesmo: não serve a
aplicação, apenas os assets. Em desenvolvimento, o dev server sobe em `:8001`
(`strictPort`, CORS liberado para `http://localhost:8000`); em produção, `bun run build`
gera o bundle e o `manifest.json` em `static/dist/`.

`static/dist/` está dentro de `STATICFILES_DIRS`, então o `collectstatic` publica os
assets em `public/static/` e o `{% static %}` resolve as URLs com hash — o Vite não
precisa saber nada sobre a árvore de estáticos do Django.

As template tags ficam em `apps/core/templatetags/vite.py` e expõem `{% vite_css %}`,
`{% vite_js %}` e `{% vite_asset %}`. **O argumento é a chave do manifest**, que o Vite
gera a partir do caminho do input relativo à raiz do projeto:

```django
{% load vite %}
{% vite_css 'frontend/entries/app.js' %}
{% vite_js 'frontend/entries/app.js' %}
```

Entrypoint novo entra em `vite.config.mjs` (`build.rollupOptions.input`) e é referenciado
pelo caminho do arquivo no template.

## Consequências

- **Positivas**: uma string só identifica o asset em dev e em produção, sem tabela de
  tradução paralela; o Django continua dono das URLs de estático; trocar o bundler no
  futuro mexe em um templatetag, não nos templates.
- **Negativas**: desenvolvimento exige dois processos (`runserver` e `bun run dev`); fora
  de `DEBUG` os templates dependem do manifest existir, o que obrigou a suíte de testes a
  injetar um manifest stub (`conftest.py`) para não depender da toolchain de JS.
- **Neutras**: o Bun cuida de instalar e rodar o pipeline; o `package.json` não declara
  nada além disso.

## Alternativas consideradas

### `django-vite`

Faz exatamente isso e é mantido. Recusado por ser uma dependência a mais para ~80 linhas
de templatetag que o projeto entende inteiras — e porque a chave do manifest aqui é uma
convenção que queríamos explícita, não configurada.

### Nome do bundle como chave (`app` em vez de `frontend/entries/app.js`)

Mais curto no template, mas exige um mapeamento entre o nome lógico e o input do Vite —
que existe em dois lugares (dev server e manifest) e sai de sincronia.

### Sem bundler: `django-compressor` ou assets à mão

Perde HMR, Tailwind 4 (que é um plugin de bundler) e o cache-busting por hash. O ganho
de simplicidade não paga o custo diário.
