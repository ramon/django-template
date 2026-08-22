# Architecture Decision Records

Um ADR registra uma decisão arquitetural: o que foi decidido, em que contexto, e o que
foi descartado no caminho. O valor está na última parte — sem ela, a decisão parece
arbitrária e alguém a desfaz de boa-fé.

## Quando escrever

Escreva um ADR quando a decisão:

- é difícil de reverter depois (escolha de biblioteca, formato de dados, fronteira entre
  camadas);
- cria uma convenção que outros vão seguir;
- é deliberadamente contra-intuitiva, e vai parecer erro para quem chegar depois;
- foi discutida com alternativas reais na mesa.

Não escreva ADR para: escolha óbvia sem alternativa, detalhe de implementação local,
correção de bug, ou preferência de formatação (isso é `standards/`).

## Como escrever

1. Copie [`0000-template.md`](0000-template.md) para `NNNN-titulo-em-kebab-case.md`,
   com o próximo número livre.
2. O título é a decisão, não o assunto: `usar-vite-como-pipeline-de-assets`, não
   `sobre-assets`.
3. Preencha **Contexto** (as forças em jogo), **Decisão** (no presente: "usamos X"),
   **Consequências** (o bom e o ruim) e **Alternativas** (com o motivo da recusa).
4. Adicione a linha no índice abaixo.

## Ciclo de vida

`Proposto` → `Aceito` → `Substituído por NNNN` ou `Depreciado`.

Um ADR aceito não é editado para mudar a decisão — só para corrigir erro ou acrescentar
o link do substituto. Mudou a decisão? ADR novo, e o antigo passa a
`Substituído por NNNN`.

## ADRs herdados da base

Os ADRs 0001–0006 vêm do `django-template` e descrevem decisões que este projeto herdou
prontas. Valem como qualquer outro: **para contrariar um deles, escreva um ADR novo que o
substitua** — não edite o antigo, e não deixe o código divergir em silêncio. A numeração de
ADRs novos continua de onde a lista abaixo termina.

## Índice

| # | Decisão | Status | Data |
| --- | --- | --- | --- |
| [0001](0001-settings-do-framework-separados-da-configuracao-da-aplicacao.md) | Settings do framework separados da configuração da aplicação | Aceito | 2026-08-18 |
| [0002](0002-vite-como-pipeline-de-assets-em-backend-integration.md) | Vite como pipeline de assets, em modo backend integration | Aceito | 2026-08-18 |
| [0003](0003-htmx-stimulus-e-alpine-em-vez-de-uma-spa.md) | HTMX, Stimulus e Alpine em vez de uma SPA | Aceito | 2026-08-18 |
| [0004](0004-catalogo-de-traducao-proprio-por-app.md) | Catálogo de tradução próprio por app | Aceito | 2026-08-18 |
| [0005](0005-makemessages-idempotente-para-o-ci-verificar-catalogos.md) | `makemessages` idempotente para o CI verificar catálogos | Aceito | 2026-08-18 |
| [0006](0006-django-cotton-para-componentes-de-template.md) | django-cotton para componentes de template | Aceito | 2026-08-18 |
| [0007](0007-autenticacao-com-django-allauth-e-mfa.md) | Autenticação com django-allauth, MFA e CORS liberado para a API | Aceito | 2026-08-18 |
| [0008](0008-desativar-envio-de-pii-para-o-sentry.md) | Desativar o envio de PII para o Sentry | Aceito | 2026-08-18 |
| [0009](0009-adotar-git-flow-para-branches-e-releases.md) | Adotar git-flow para branches e releases | Aceito | 2026-08-18 |
| [0010](0010-documento-de-identidade-tipado-pela-nacionalidade.md) | Documento de identidade tipado pela nacionalidade, com suporte parcial a países | Aceito | 2026-08-22 |
| [0011](0011-full-clean-automatico-no-basemodel-save.md) | `full_clean()` automático em `BaseModel.save()` | Aceito | 2026-08-22 |
| [0012](0012-tema-com-tokens-no-molde-do-material-design-3.md) | Tema com tokens no molde do Material Design 3 | Aceito | 2026-08-22 |
| [0013](0013-customizacao-de-ui-do-allauth-via-elements-e-apps-ui.md) | Customização de UI do allauth via override de elements/layouts, delegando para `apps/ui` | Aceito | 2026-08-22 |
| [0014](0014-remover-fallback-de-avatar-para-o-gravatar.md) | Remover o fallback de avatar para o Gravatar | Aceito | 2026-08-22 |
