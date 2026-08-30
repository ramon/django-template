# 0015. Convenção de autoria de componentes Cotton

- **Status**: Aceito
- **Data**: 2026-08-30
- **Relacionados**: 0003, 0006, 0012, 0013, `docs/standards/components.md`

## Contexto

A [0006](0006-django-cotton-para-componentes-de-template.md) adotou `django-cotton`, mas
não disse *como* escrever um componente. Os componentes de `apps/ui/` cresceram sem
contrato comum: `class` do chamador não passa para lugar nenhum (nenhum declara `class`
no `<c-vars>`), a escolha de estilo por variante é `{% if %}` aninhado dentro do atributo
`class` (o `button.html` tinha três níveis), e nenhum tinha teste ou comentário de
cabeçalho. Cada componente novo reinventava a forma.

O [`django-cotton-ui`](https://github.com/wrabit/django-cotton-ui) — o kit oficial, com
~40 componentes — resolve os mesmos problemas com um conjunto de convenções estáveis:
mapa `variante → classes` no `<c-vars>`, `class` sempre declarada e aplicada por último,
`{{ attrs }}` no controle que submete o valor, split `index`/`impl` para componentes de
formulário, comentário de cabeçalho, teste que renderiza o template real. O kit em si não
serve ao projeto — é Tailwind v4 com uma paleta `ink-*` própria (conflita com os tokens
no molde do Material Design 3 da [0012](0012-tema-com-tokens-no-molde-do-material-design-3.md))
e traz um bundle Alpine com comportamento embutido (contra a
[0003](0003-htmx-stimulus-e-alpine-em-vez-de-uma-spa.md): comportamento é Stimulus). Mas
as convenções são independentes disso.

## Decisão

Componentes Cotton do projeto seguem uma convenção de autoria única, no molde do
`django-cotton-ui`, descrita em [`docs/standards/components.md`](../standards/components.md).
O kit **não** entra como dependência: só os padrões são emprestados.

O que a convenção fixa:

- toda prop com comportamento no `<c-vars>` com default; `class` sempre declarada e
  aplicada por último; o resto passa por `{{ attrs }}`;
- `{{ attrs }}` no elemento raiz semântico — e, em controle de formulário, no próprio
  `<input>`/`<select>`/`<textarea>`, para binding de HTMX/Alpine alcançar quem submete;
- variante → classes é um dict no `<c-vars>`, resolvido com `|get_item`, não `{% if %}`
  dentro do atributo `class`;
- token semântico do tema sempre; nunca classe Tailwind interpolada com variável;
- comportamento é Stimulus ou Alpine, nunca lógica no template;
- cada componente abre com um `{% comment %}` de uma a três linhas;
- todo componente tem teste de contrato em `apps/ui/tests/` que renderiza o template real
  e assere prop → markup e passthrough de `{{ attrs }}`.

Os componentes que já existiam foram migrados para a convenção no mesmo PR que a
introduziu. Layouts (`templates/components/layouts/`) são a exceção: são shells de
herança clássica, não componentes de marcação, e seguem a
[0006](0006-django-cotton-para-componentes-de-template.md).

## Consequências

- **Positivas**: componente novo tem forma pronta; `class` do chamador sempre funciona;
  a matriz de variantes fica legível; regressão de markup é pega por teste.
- **Negativas**: mais cerimônia por componente (dict de variantes, comentário, teste) do
  que um `<div class="…">` solto. A convenção precisa ser relida a cada componente novo
  até virar hábito.
- **Neutras**: seguir de perto o `django-cotton-ui` deixa a porta aberta para portar um
  componente de lá pontualmente, traduzindo as classes para os tokens do tema.

## Alternativas consideradas

### Adotar `django-cotton-ui` como dependência

~40 componentes prontos e acessíveis. Mas a paleta é `ink-*`/Tailwind v4, não os tokens
da [0012](0012-tema-com-tokens-no-molde-do-material-design-3.md), e o bundle Alpine embute
comportamento que a [0003](0003-htmx-stimulus-e-alpine-em-vez-de-uma-spa.md) põe no
Stimulus. Reestilizar ~40 componentes para os tokens do projeto é mais trabalho do que
escrever os poucos que o projeto usa.

### Manter sem convenção

Cada componente decide sua forma. Era o estado até aqui — e a razão de `button.html` ter
`{% if %}` triplo no atributo `class` e de nenhum componente aceitar `class` do chamador.

### django-components

Já descartado na [0006](0006-django-cotton-para-componentes-de-template.md): componente
com classe Python e CSS/JS por componente é peso que o projeto não quer — marcação é
Cotton, comportamento é Stimulus.
