# Padrões: componentes Cotton

Como se escreve um componente `django-cotton` neste projeto. O *porquê* e as alternativas
descartadas estão na [ADR 0015](../adr/0015-convencao-de-autoria-de-componentes-cotton.md);
a decisão de usar Cotton em si, na [0006](../adr/0006-django-cotton-para-componentes-de-template.md).
A convenção segue de perto o [`django-cotton-ui`](https://github.com/wrabit/django-cotton-ui),
sem trazer o kit como dependência.

Visão geral de front-end e a escolha entre HTMX/Stimulus/Alpine ficam em
[`frontend.md`](frontend.md); os tokens do tema, na
[0012](../adr/0012-tema-com-tokens-no-molde-do-material-design-3.md).

## Quando algo merece ser um componente

Um componente se paga quando tem **prop, variante, ou composição de slot** (`button`,
`field`, `alert`, `panel`, `form`, `table`) — ou **reuso real** em mais de um call site.

Uma tag com uma classe fixa e um único chamador **não** vira componente: a indireção do
`<c-vars>` + parser do Cotton não compra nada. Foi o caso de `<c-ui.h1>`/`h2`/`p`/`hr` e
dos subelementos de tabela (`thead`/`tr`/`td`…) — só o override de element do allauth os
usava, então o estilo voltou para a própria tag (em `templates/allauth/elements/*.html`
ou, no caso da tabela, num seletor de descendente do `<c-ui.table>`). O próprio
`django-cotton-ui` não tem primitivo tipográfico nem `<c-*.tr>`.

## Onde moram e como se chamam

```text
apps/ui/templates/components/ui/         # biblioteca genérica → <c-ui.*>
templates/components/                     # componentes do shell do projeto (layouts)
```

- Nome de arquivo em `snake_case` (`button_group.html`), porque
  `COTTON_SNAKE_CASED_NAMES = True`. O uso é `<c-ui.button_group>`.
- Um componente = um arquivo. Componente **composto** (que só faz sentido com suas
  partes) = uma pasta: `nome/index.html` é a raiz, `nome/item.html` / `nome/group.html` /
  `nome/trigger.html` são as partes. Uso: `<c-ui.accordion>` e `<c-ui.accordion.item>`.
- Referência de props de cada componente: [`apps/ui/AGENTS.md`](../../apps/ui/AGENTS.md),
  atualizada no mesmo commit que muda uma prop.

## Anatomia

```django
{% comment %}Alerta de página. `severity` decide cor e ícone.{% endcomment %}
<c-vars severity="info" class="" :styles="{ ... }" />

<div role="alert" {{ attrs }} class="… {{ styles|get_item:severity }} {{ class }}">
    {{ slot }}
</div>
```

1. **Comentário de cabeçalho**: um `{% comment %}` de uma a três linhas dizendo o que o
   componente renderiza e quando usá-lo. Notas de composição (ex.: "use `padding='none'`
   para conteúdo full-width") entram aqui.
2. **`<c-vars>`**: toda prop com comportamento próprio, com o default.
   - string: `variant="prominent"`; booleano/tipado: `:disabled="False"`, `:open="True"`;
   - opcional sem default útil: `label` (fica vazio).
   - `{% translate %}` funciona dentro do `<c-vars>` (django-cotton ≥ 2.7).
3. **Markup**: um elemento raiz semântico. Sem lógica — ver *Comportamento*.

Prop que é só um atributo HTML nativo (`id`, `name`, `type` de input, `hx-*`, `data-*`,
`aria-*`, `disabled`) **não** vai no `<c-vars>`: passa sozinha por `{{ attrs }}`.

## `class` e `{{ attrs }}`

- **`class` sempre no `<c-vars>`** (`class=""`), e aplicada **por último** na lista:
  `class="base… {{ class }}"`. Sem isso, classe do chamador não chega ao componente.
- **`{{ attrs }}` no elemento raiz semântico.** Um `{{ attrs }}` ao lado de um
  `class="…"` hardcoded já cobre o caso: como `class` está no `<c-vars>`, ela sai de
  `attrs` e não duplica o atributo.
- **Controle de formulário**: `{{ attrs }}` vai no próprio `<input>`/`<select>`/
  `<textarea>`, nunca num wrapper — é o que faz `x-model`, `hx-*` e afins alcançarem o
  elemento que submete o valor. Ver `apps/ui/templates/components/ui/field.html`.
- **Raiz visível envolvendo controle escondido** (checkbox/switch custom): `class` fica na
  raiz visível, `{{ attrs }}` vai no controle escondido.
- Alternativa para merge num só ponto:
  `{{ attrs.dict|merge:'class:classes base aqui' }}` (o filtro `merge` é builtin).

## Variantes: mapa no `<c-vars>`, não `{% if %}` no `class`

Escolha de classes por variante é um dict no `<c-vars>`, resolvido com `|get_item`:

```django
<c-vars color="neutral" class="" :colors="{'neutral': 'bg-surface-container-high text-on-surface-variant', 'primary': 'bg-primary-container text-on-primary-container', 'danger': 'bg-error-container text-on-error-container'}" />

<span {{ attrs }} class="… {{ colors|get_item:color }} {{ class }}">{{ slot }}</span>
```

O dict fica **numa linha só**: o parser do `<c-vars>` (django-cotton 2.7) quebra a tag
inteira se um atributo tem quebra de linha. Linha longa em `.html` não é lintada.

Duas variantes ortogonais (ex.: `variant` × `color`): uma chave composta e um
`{% with key=variant|add:"-"|add:color %}` antes do lookup — ver
`apps/ui/templates/components/ui/button.html`. Para uma escolha binária simples
(`align="right"`), um `{% if %}` inline no `class` ainda vale.

Escala de tamanho, quando existir, é sempre `xs sm md lg xl 2xl`.

## Slot ou prop

Conteúdo curto de texto (`label`, `title`, `header`, `actions`) aceita **prop** (string)
ou **`<c-slot name="…">`** de mesmo nome; o slot vence quando presente. Slot nomeado para
região com marcação; prop para string simples. O default `{{ slot }}` é o corpo.

## `href` troca o elemento

Componente clicável com `href=""` no `<c-vars>`: presente ⇒ renderiza `<a>`; ausente ⇒
`<button>`/`<span>`. Evita `<button>` dentro de `<a>`. Ver `button.html`, `badge.html`.

## Acessibilidade

- `role` e `aria-*` no que não é semântico por natureza; foco visível (`focus:ring-*`)
  em tudo que é interativo.
- SVG decorativo: `aria-hidden="true"`. Botão só com ícone: `<span class="sr-only">` com
  o rótulo, ou `aria-label`.
- Rótulo oculto visualmente continua no DOM (`sr-only`) — nunca removido. Ver o
  `hide_label` de `field.html`.

## CSS

Token semântico do tema sempre (`bg-primary`, `text-on-surface`, `surface-container-*`),
nunca a escala Tailwind crua nem cor hardcoded — ver
[`frontend.md`](frontend.md#tema-tokens-semânticos-e-dark-mode).

**Nunca uma classe Tailwind interpolada com variável**: `max-w-[{{ x }}]` não chega no
compilador. Use classe fixa, uma CSS var (`max-w-[var(--x)]`) ou `style` inline.

A ordem das classes é validada por `rustywind` (`bun run lint:classes`); rode
`bun run lint:classes:fix` antes de fechar.

## Comportamento

Template de componente não carrega lógica. Microestado local (toggle, dropdown, acordeão)
é Alpine inline; comportamento que dá vontade de testar é um controller Stimulus em
`frontend/controllers/<nome>_controller.js` — ver
[`frontend.md`](frontend.md#qual-biblioteca-usar) e o `password_visibility_controller.js`
ligado a `field.html`.

Dado do servidor para dentro de `x-data`: passe por `json_script` ou um filtro de
serialização — nunca interpole valor cru numa expressão Alpine.

## Armadilhas do parser do Cotton

- **Sem block tag no atributo de um componente.** `<c-x {% if %}…{% endif %}>` quebra o
  parser (`Invalid block tag … expected 'endcotton'`) — vale para `{% if %}`, `{% for %}`
  e `{% with %}`. Resolva fora, com `{% with %}`, e passe pronto: `:attr="variavel"`.
- **`:attr="x|filtro"` não aceita filtro.** Falha em silêncio: o atributo não é setado.
  Pré-compute com `{% with x=x|filtro %}` e passe a variável.
- **`{# … #}` só numa linha.** Comentário de mais de uma linha vaza pro HTML — use
  `{% comment %}…{% endcomment %}`.
- **`<c-vars>` numa linha só.** Quebra de linha dentro da tag (num dict `:map`, p. ex.)
  quebra a tag inteira em silêncio — o componente perde todas as props.

## Teste

Todo componente tem teste de contrato em `apps/ui/tests/integration/test_components.py`.
O helper `render()` (em `apps/ui/tests/integration/cotton.py`) compila e renderiza o
componente contra os templates reais, no molde do próprio `django-cotton-ui`:

```python
def test_button_renders_anchor_when_href_is_set():
    html = render('<c-ui.button href="/x">Ir</c-ui.button>')
    assert opening_tag(html, r"<a\b[^>]*>")


def test_button_forwards_native_attrs():
    html = render('<c-ui.button data-role="cta" hx-get="/x">Ir</c-ui.button>')
    tag = opening_tag(html, r"<button\b[^>]*>")
    assert 'data-role="cta"' in tag and 'hx-get="/x"' in tag
```

Asserir: cada valor de variante muda o markup esperado; `{{ attrs }}` chega ao elemento
certo; `class` do chamador aparece e não duplica. Não asserir sobre texto traduzido
(ver [`testing.md`](testing.md#o-que-vale-a-pena-testar)).

## Checklist de componente novo

- [ ] `{% comment %}` de cabeçalho
- [ ] toda prop de comportamento no `<c-vars>` com default; `class=""` incluída
- [ ] variantes como dict + `|get_item`; `class` por último no atributo
- [ ] `{{ attrs }}` no elemento certo (o controle, em formulário)
- [ ] tokens do tema; nenhuma classe interpolada; `lint:classes:fix` rodado
- [ ] comportamento em Stimulus/Alpine, não no template
- [ ] teste de contrato em `apps/ui/tests/integration/test_components.py`
- [ ] entrada em [`apps/ui/AGENTS.md`](../../apps/ui/AGENTS.md)
