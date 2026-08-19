# 0009. Adotar git-flow para branches e releases

- **Status**: Aceito
- **Data**: 2026-08-18
- **Relacionados**: [`docs/standards/git.md`](../standards/git.md)

## Contexto

Até aqui o projeto era trunk-based: `master` era o tronco, todo trabalho entrava por
branch curta e PR direto contra `master`, e o CI rodava só em push para `master` e em PR.
Isso funcionou enquanto o projeto tinha um único fluxo de entrega (merge = pronto para
produção) e nenhuma noção de release.

Duas coisas passam a exigir mais estrutura: o versionamento semântico do projeto (ver
[`git.md`](../standards/git.md#changelog-e-versionamento)) precisa de um ponto no tempo
em que uma versão é "fechada" — com `CHANGELOG.md` e bump de versão revisados antes de ir
para produção — e não só a cada merge individual; e um fluxo de hotfix precisa poder
corrigir produção sem carregar trabalho já integrado mas ainda não liberado. Trunk-based
resolve o primeiro caso (deploy contínuo) mas não separa "integrado" de "liberado".

## Decisão

Adotamos o modelo git-flow (Vincent Driessen). Duas branches permanentes:

- **`master`**: reflete exatamente o que está em produção. Só recebe merge de
  `release/*` ou `hotfix/*`. Todo merge em `master` é uma versão: leva tag `vX.Y.Z`
  (ver [`git.md`](../standards/git.md#changelog-e-versionamento)).
- **`develop`**: branch de integração. É contra ela que todo PR de trabalho em andamento
  é aberto e é dela que toda `feature/*` nasce.

Branches de vida curta:

- **`feature/<escopo>-<descricao>`**: a partir de `develop`, volta para `develop` via PR.
  É o equivalente da branch curta que já se usava, só que a base muda de `master` para
  `develop`.
- **`release/X.Y.Z`**: a partir de `develop`, quando o escopo do próximo release fecha.
  Só recebe fix e o trabalho de release (bump de versão, mover `Unreleased` do
  `CHANGELOG.md` para a seção da versão). Ao terminar: merge em `master` (com tag) e
  merge de volta em `develop`.
- **`hotfix/X.Y.Z`**: a partir de `master`, para corrigir produção sem esperar o próximo
  release. Merge em `master` (com tag) e merge de volta em `develop`.

O CI passa a rodar em push para `master` **e** `develop`, além de todo PR — ver
`.github/workflows/ci.yml`.

## Consequências

- **Positivas**: `master` vira um histórico limpo de releases, cada uma taggeada e
  correspondente a uma entrada do `CHANGELOG.md`. Hotfix não precisa esperar `develop`
  estabilizar. O fluxo dá um lugar natural para o trabalho de release (bump de versão,
  changelog) sem misturar com feature.
- **Negativas**: mais uma branch permanente para manter sincronizada — merge de
  `release/*`/`hotfix/*` sempre vai para os dois lados (`master` e `develop`), e esquecer
  o segundo lado é uma forma comum de regressão (fix aplicado em produção "some" da
  próxima release). PR passa a mirar `develop` por padrão, não `master` — muda o hábito de
  quem já tinha o trunk-based internalizado.
- **Neutras**: o padrão de commit (Conventional Commits) não muda; só a base da branch e o
  destino do merge mudam.

## Alternativas consideradas

### Manter trunk-based e versionar a cada merge em `master`

Mais simples, mas não separa "integrado" de "liberado": um merge que quebra em produção
não tem como ser isolado de trabalho já integrado mas ainda não testado em conjunto para
release. Também não dá um lugar natural para o trabalho de fechar uma versão (bump,
changelog) sem misturar commit de feature com commit de release.

### GitHub flow com branches de release adicionadas ad-hoc

Fica no meio do caminho: ganha a separação de release sem o `develop` permanente, mas
perde o lugar único de integração — cada release branch nasceria de um ponto arbitrário
de `master`, e não haveria onde acumular trabalho integrado à espera do próximo release.
Preferiu-se o modelo completo, já testado e documentado, a inventar uma variação.
