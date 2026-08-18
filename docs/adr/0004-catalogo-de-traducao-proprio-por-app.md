# 0004. Catálogo de tradução próprio por app

- **Status**: Aceito
- **Data**: 2026-08-18
- **Relacionados**: 0005, `docs/standards/i18n.md`

## Contexto

O caminho padrão em projetos Django é um único `locale/` na raiz, listado em
`LOCALE_PATHS`, com todas as strings de todos os apps. Num projeto organizado por domínio
isso desfaz a fronteira que o resto da estrutura mantém: mover ou remover um app deixa
suas traduções órfãs no catálogo global, e todo `.po` tem conflito de merge em qualquer
trabalho paralelo, porque todos escrevem no mesmo arquivo.

## Decisão

Cada app tem o seu catálogo em `apps/<app>/locale/`. O `locale/` da raiz — o único em
`LOCALE_PATHS` — guarda apenas o que não pertence a app nenhum: `templates/` e `config/`.

Não é preciso rodar um comando por app: o Django decide o destino durante a varredura —
ao encontrar um diretório `locale/`, passa a mandar para lá tudo que estiver abaixo do
diretório pai. Como cada app tem o seu, as strings do app ficam no app, e um
`python manage.py makemessages` na raiz cuida de todos.

A precedência é a do Django, verificada por teste neste projeto (`tests/test_i18n.py`):
`LOCALE_PATHS` ganha de tudo; entre apps, quem vem **antes** em `INSTALLED_APPS` ganha. Na
prática `django.contrib.auth` sobrepõe uma tradução de mesmo `msgid` em `apps/accounts` —
para cravar um texto, o lugar é o catálogo da raiz.

Os `.po` são versionados; os `.mo`, não. A compilação é passo de build: o `Dockerfile` a
executa no estágio `assets` e o job `test` do CI antes do pytest.

## Consequências

- **Positivas**: app é unidade completa, traduções incluídas; conflito de merge fica
  restrito ao app tocado; apagar um app apaga suas strings.
- **Negativas**: a mesma string traduzida em dois apps é traduzida duas vezes; e a regra
  de precedência passa a importar de verdade — uma tradução que "não pega" costuma ser um
  app anterior em `INSTALLED_APPS` sobrepondo o `msgid`, o que não é óbvio.
- **Neutras**: são mais arquivos `.po` — um por app e por idioma, em vez de um por
  idioma — com o mesmo total de strings.

## Alternativas consideradas

### `locale/` único na raiz

O padrão. Recusado pelos conflitos de merge e pela perda da fronteira de domínio.

### Um catálogo por app, com `LOCALE_PATHS` apontando para todos

Funciona, mas transforma `LOCALE_PATHS` numa lista que cresce a cada app e inverte a
precedência esperada (o global deixaria de ganhar). A descoberta automática por app
instalado é comportamento nativo do Django e não precisa de registro manual.
