# 0016. Portas do compose internas por padrão

- **Status**: Aceito
- **Data**: 2026-09-01
- **Relacionados**: [`docs/standards/infra.md`](../standards/infra.md)

## Contexto

O `docker-compose.yml` publicava cinco portas fixas no host: `app` 8000, `frontend`
8001, `database` 5432, `kv-database` 6379 e `prometheus` 9090. Com mais de uma stack
Docker na mesma máquina — outro projeto, um segundo clone deste — as portas colidem e
`docker compose up` falha com `port is already allocated`. `5432` e `6379` são as que
mais colidem, porque quase todo projeto sobe um Postgres e um Redis/Valkey na porta
padrão.

Dentro da rede do compose os serviços já se encontram pelo nome (`database:5432`,
`kv-database:6379`) — o bloco `x-app` sobrescreve as URLs para isso. A porta publicada
no host só serve para o browser (`app`, `frontend`), para o Prometheus e para o caminho
de desenvolvimento em que a aplicação roda na máquina e precisa alcançar o banco e o
cache em `127.0.0.1`.

## Decisão

`database` e `kv-database` não publicam porta no `docker-compose.yml`. O acesso a partir
do host é por `docker compose exec`. `app`, `frontend` e `prometheus` publicam presos a
`127.0.0.1` e com a porta vinda do ambiente — `APP_PORT`, `VITE_PORT`, `PROMETHEUS_PORT`,
com o valor atual como default (`"127.0.0.1:${APP_PORT:-8000}:8000"`).

O caminho "só banco e cache em containers, app na máquina" ganha um segundo arquivo de
compose versionado, `docker-compose.local-db.yml`, que reexpõe `5432`/`6379` no host
(também parametrizados, por `POSTGRES_PORT`/`VALKEY_PORT`). Ele **não** é carregado pelo
`docker compose up` da stack inteira — só quando passado com `-f`, o que `make services`
faz. Assim a stack em container nunca reexpõe o banco no host.

Todas as portas ficam listadas em `.env.example`. `COMPOSE_PROJECT_NAME` também, para o
prefixo de container/rede/volume não colidir entre clones.

## Consequências

- **Positivas**: duas stacks Docker convivem sem conflito no caso comum (banco e cache
  não tocam o host). As portas que sobram são configuráveis por um número no `.env`.
  Publicar em `127.0.0.1` tira os serviços da rede local.
- **Negativas**: `psql`/`redis-cli` direto do host exigem `docker compose exec` (ou o
  `make services`, no caminho da app na máquina). Quem sobe o banco com `docker compose
  up -d database` cru não tem mais a porta — precisa de `make services` ou do `-f`.
- **Neutras**: mais um arquivo de compose e cinco variáveis novas no `.env.example`.
  Emenda o ADR [0009](0009-adotar-git-flow-para-branches-e-releases.md)? Não — os dois
  caminhos de desenvolvimento do `infra.md` seguem valendo, só muda como o banco é
  exposto.

## Alternativas consideradas

### Portas do host dinâmicas via script no `make setup`

Um script sondaria portas livres a partir do default e gravaria no `.env`, reescrevendo
também as URLs. Resolve os cinco casos, mas é código para manter, reescrever `.env` com
regex é frágil, e a maior parte do ganho vem só de não expor `database`/`kv-database` —
que não precisa de script nenhum.

### Portas efêmeras (`- "5432"`, Docker escolhe)

Conflito zero, mas obriga `docker compose port database 5432` para descobrir a porta e
quebra as URLs estáticas do `.env` no caminho da app na máquina.

### Rodar aplicação e testes dentro do container por padrão

Elimina a necessidade de expor o banco, mas move os quality gates (`make check`) para
`docker compose exec`, com impacto em CI, i18n e e2e (que não rodam no container de dev)
e no feedback local. Custo desproporcional para um problema de porta.
