# 0005. `makemessages` idempotente para o CI verificar catálogos

- **Status**: Aceito
- **Data**: 2026-08-18
- **Relacionados**: 0004, `docs/standards/i18n.md`

## Contexto

O `makemessages` padrão do Django não é idempotente: cada execução reescreve
`POT-Creation-Date` no header de todo `.po` e atualiza os comentários `#: arquivo:linha`
de cada mensagem. Duas consequências práticas:

1. **Diff sem conteúdo.** Renomear um arquivo ou mover uma função altera dezenas de
   linhas de referência em cada catálogo, sem que uma única tradução mude. Com catálogo
   por app ([0004](0004-catalogo-de-traducao-proprio-por-app.md)), é um arquivo sujo por
   app e por idioma em cada refatoração.
2. **Impossível verificar no CI.** A verificação natural — rodar `makemessages` e falhar
   se houver diff — acusaria diff sempre, porque a data muda a cada execução. Sem ela,
   nada impede alguém de adicionar uma string traduzível e esquecer o catálogo, e a string
   aparece sem tradução em produção.

Também havia um risco específico da suíte: um teste que afirma algo sobre uma string
traduzida injetaria essa string no catálogo, poluindo-o com texto de teste.

## Decisão

`apps/core/management/commands/makemessages.py` sobrescreve o comando do Django e muda
quatro padrões:

- **`--no-location`**: sem o par `arquivo:linha`. Para investigar uma string,
  `--add-location=file` volta atrás pontualmente.
- **`--no-obsolete`**: mensagens que saíram do código desaparecem, em vez de acumularem
  comentadas com `#~` até ninguém saber o que ainda está vivo.
- **`POT-Creation-Date` removida** dos catálogos do projeto depois da geração. O recorte é
  por `apps/`, não por `BASE_DIR`: `get_app_configs()` devolve também apps de terceiros e
  o `.venv` fica dentro do `BASE_DIR` — filtrar por ele reescreveria ~700 catálogos em
  `site-packages`.
- **Sem `-l/-x/-a`, os idiomas vêm de `settings.LANGUAGES`**, e `node_modules`,
  `static/dist` e `tests` ficam fora da varredura.

Os quatro juntos tornam o comando idempotente, e é isso que permite ao job `test` do CI
rodar `makemessages` e falhar em qualquer diff de `.po` com a mensagem de rodar o comando
e comitar.

## Consequências

- **Positivas**: `makemessages` duas vezes seguidas produz zero diff; o CI garante que
  catálogo desatualizado não passa; o histórico dos `.po` contém tradução, não referência
  de linha.
- **Negativas**: um comando customizado a mais para manter — se o Django mudar o
  `makemessages`, o override pode precisar de ajuste; e quem procura de onde vem uma
  string perde o `arquivo:linha` até rodar com `--add-location=file`.
- **Neutras**: as strings de `tests/` nunca entram no catálogo, o que é o desejado, mas
  significa que texto traduzível usado apenas em teste não é traduzido.

## Alternativas consideradas

### `makemessages` padrão, sem verificação no CI

Barato, mas deixa passar exatamente o erro que mais acontece: string nova sem catálogo
atualizado.

### Manter as locations e verificar no CI só o header

Reduz o falso positivo, mas não resolve o diff de refatoração — que é o ruído maior — e
exige comparação parcial de arquivo, mais frágil que `git diff --exit-code`.

### Um script de pós-processamento fora do comando

Funciona, mas passa a existir um jeito certo e um jeito errado de rodar `makemessages`.
Colocar o comportamento no próprio comando remove a escolha.
