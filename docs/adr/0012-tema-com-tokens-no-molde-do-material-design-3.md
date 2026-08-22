# 0012. Tema com tokens no molde do Material Design 3

- **Status**: Aceito
- **Data**: 2026-08-22
- **Relacionados**: `docs/standards/frontend.md`

## Contexto

O template tinha Tailwind instalado (`@tailwindcss/vite`) mas `frontend/styles/app.css`
só continha `@import "tailwindcss";` — nenhum token, nenhuma estratégia de dark mode. A
página de exemplo (`templates/pages/home.html`) já usava a variant `dark:` do Tailwind,
mas com cor hardcoded em cada elemento (`slate-*`, `emerald-*`), sem nome semântico: para
recolorir o tema era preciso caçar cada classe, em cada template, e não havia forma de o
usuário escolher o tema manualmente — só `prefers-color-scheme`.

Um projeto gerado a partir deste template precisa de um ponto de partida para tema que
não seja "cor solta no HTML", e de um jeito de o visitante escolher claro/escuro sem
depender só do sistema operacional.

## Decisão

**Tokens semânticos, no molde do Material Design 3.** `frontend/styles/app.css` define,
dentro de `@theme`, 36 custom properties nomeadas por papel (`primary`/`on-primary`,
`*-container`/`on-*-container`, `background`/`surface`/`surface-variant`, os cinco níveis
de `surface-container-*`, `outline`/`outline-variant`, `inverse-*`, `shadow`/`scrim`) —
a estrutura de papéis do M3, não a paleta oficial dele. As cores concretas usam as
escalas nativas do Tailwind v4 (`slate` neutro, `indigo` primary, `teal` secondary,
`amber` tertiary, `red` error), com os tons ajustados para contraste WCAG AA
(4.5:1 texto normal, 3:1 componente de UI) nos 24 pares `role`/`on-role` que importam.
Um bloco `.dark { … }` redefine as mesmas 36 properties; nenhuma classe precisa do
prefixo `dark:` para cor — `bg-primary`, `text-on-surface` etc. já respondem sozinhas,
porque a variável muda de valor conforme o ancestral tem ou não a classe `.dark`.

**Dark mode manual, com persistência.** `@custom-variant dark (&:where(.dark, .dark
*));` troca a variant `dark:` do Tailwind, que por padrão segue só
`prefers-color-scheme`, para responder à classe `.dark` em algum ancestral. Um botão
com `data-controller="theme" data-action="theme#toggle"` aciona
`frontend/controllers/theme_controller.js`, que alterna a classe em
`document.documentElement` e grava a escolha em `localStorage["theme"]`. Um script
inline no `<head>` de `templates/layouts/base.html` — antes de qualquer CSS, antes do
primeiro paint — lê a mesma chave (ou `prefers-color-scheme` na ausência dela) e aplica
a classe de imediato, para não haver flash do tema errado.

**Ordenação de classe Tailwind fora do Biome.** O parser HTML do Biome 2.5 não entende
sintaxe de template Django (`{% %}`/`{# #}` — ele espera Svelte/JSX) e falha em qualquer
`.html` do projeto; a regra `nursery.useSortedClasses` do Biome, por isso, não alcança
`templates/`. Quem ordena classe Tailwind nos templates é o `rustywind` (`bun run
lint:classes` / `lint:classes:fix`), que trabalha por regex sobre o atributo `class`,
agnóstico à linguagem de template ao redor.

## Consequências

- **Positivas**: recolorir o tema é editar ~36 linhas em um arquivo, não caçar classe
  espalhada; qualquer template novo herda claro/escuro de graça, sem `dark:` por
  elemento; o toggle e a persistência já vêm prontos, sem cada projeto gerado resolver
  FOUC e `localStorage` do zero.
- **Negativas**: 36 tokens (72 com light+dark) é mais que o mínimo de um tema ad-hoc —
  quem só queria trocar duas cores encontra uma estrutura maior que o necessário; a
  nomenclatura de papel (`on-surface-variant`, `surface-container-high`) exige raciocinar
  em "papel semântico" em vez de "essa cinza aí", o que tem curva de aprendizado.
- **Neutras**: `rustywind` é uma dependência de build a mais (binário Rust via
  `postinstall`), sem relação com o Biome que já ordena import/formata `frontend/**`.

## Alternativas consideradas

### Paleta oficial do M3 (cor gerada por semente via HCT)

Cores fiéis ao Material exigiriam ou rodar o algoritmo HCT (fora do escopo de um `@theme`
CSS-first) ou copiar os hex publicados da paleta *baseline* do Google — que fixaria a
marca em "roxo Material" para todo projeto gerado. Preferimos manter só a *estrutura* de
papéis e escolher cor livre por projeto.

### `prefers-color-scheme` puro, sem toggle

Zero JavaScript, mas tira do usuário a opção de contrariar o SO — caso comum em produção.
O custo de resolver FOUC e persistência uma vez, no template, é menor que cada projeto
gerado resolver sozinho depois.

### `nursery.useSortedClasses` do Biome nos templates

Testado e descartado: o parser HTML do Biome 2.5 não reconhece tag de template Django e
falha o `check` inteiro. Ativar a regra só em `frontend/**/*.js` teria efeito nulo — não
há string de classe Tailwind em JS no projeto.

### `prettier-plugin-tailwindcss`

Exige Prettier como formatter; o projeto usa Biome, que não é compatível com plugin de
Prettier. Trocar de formatter para ganhar ordenação de classe seria desproporcional.
