# 0003. HTMX, Stimulus e Alpine em vez de uma SPA

- **Status**: Aceito
- **Data**: 2026-08-18
- **Relacionados**: 0002, 0006, `docs/standards/frontend.md`

## Contexto

A maior parte das aplicações deste porte não precisa de estado no cliente: precisa de
formulários, listas, filtros e atualização parcial de tela. Uma SPA resolve isso ao preço
de duplicar modelo de dados, roteamento, validação e autenticação no frontend, e de
exigir uma API para tudo — inclusive para telas que o servidor já sabe renderizar.

Ao mesmo tempo, "só Django templates" leva a jQuery informal: comportamento de cliente
espalhado em `<script>` inline, sem lugar definido nem teste.

## Decisão

O servidor renderiza o HTML; o cliente é enriquecido progressivamente por três
bibliotecas com papéis que não se sobrepõem:

| Biblioteca | Quando usar |
| --- | --- |
| HTMX | buscar ou trocar fragmentos HTML renderizados pelo servidor |
| Stimulus | comportamento estruturado e reutilizável, ligado a um pedaço de DOM |
| Alpine.js | microestado local — um dropdown, um toggle — sem criar um controller |

Tudo é inicializado em `frontend/entries/app.js`, que só orquestra: lógica com regra vira
módulo em `frontend/lib/`, testável em isolamento.

Três detalhes fazem os três conviverem:

- **Stimulus se auto-registra**: `frontend/controllers/index.js` varre
  `./*_controller.js` com `import.meta.glob` e deriva o identificador do nome do arquivo
  (`hello_controller.js` → `data-controller="hello"`).
- **HTMX manda o CSRF sozinho**: um listener de `htmx:configRequest` copia
  `<meta name="csrf-token">` para o header `X-CSRFToken` (`frontend/lib/csrf.js`), sem o
  que o Django rejeitaria todo POST.
- **Alpine é reinicializado nos fragmentos**: `htmx.onLoad(content =>
  Alpine.initTree(content))`, senão HTML injetado pelo HTMX chega com os `x-data`
  inertes. O Stimulus não precisa — observa o DOM por conta própria.

`window.htmx` e `window.Alpine` ficam expostos para uso em atributos inline nos
templates.

## Consequências

- **Positivas**: uma fonte de verdade (o servidor); nenhuma duplicação de validação ou
  roteamento; a API existe para clientes de verdade, não para alimentar a própria tela;
  cada pedaço de comportamento tem um lugar óbvio.
- **Negativas**: três bibliotecas para aprender em vez de uma, e a fronteira entre
  Stimulus e Alpine é de julgamento — sem a tabela acima, o time escolhe por gosto. A
  reinicialização do Alpine é acoplamento explícito entre duas bibliotecas.
- **Neutras**: interações muito ricas (editor, canvas, tempo real) continuam possíveis,
  mas serão ilhas dentro da página, não a arquitetura.

## Alternativas consideradas

### SPA (React/Vue) consumindo a API

Recusada pelo custo estrutural descrito no contexto, para um ganho que só aparece em
aplicações com estado de cliente pesado.

### Só HTMX

Cobre a troca de fragmentos, mas deixa sem casa o comportamento puramente local — um
menu que abre não deveria dar ida ao servidor.

### Só Alpine, sem Stimulus

Alpine em pedaços grandes de comportamento vira lógica dentro de atributos HTML, que não
é testável nem reutilizável. O Stimulus existe justamente para o que passa desse ponto.
