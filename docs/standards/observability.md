# Padrões: observabilidade

Como este projeto enxerga o que está acontecendo em produção: logs, erros e métricas. As
sondas de saúde (`/health/`, `/health/workers/`) têm padrão próprio em
[`infra.md`](infra.md#sondas-de-saúde); os logs estruturados, em
[`backend.md#logs`](backend.md#logs). Este documento cobre o que fica entre os dois: erro
capturado (Sentry) e métrica exportada (Prometheus).

## Sentry: erro, sem PII

Ativado fora de `DEBUG` quando `INTEGRATION_SENTRY_DSN` está definido
(`config/settings/parts/sentry.py`), com integração ao Django e ao Celery.

**`send_default_pii=False`, de propósito** — ver
[ADR 0008](../adr/0008-desativar-envio-de-pii-para-o-sentry.md). O SDK, com essa opção
desligada, não anexa e-mail, IP nem cookie de sessão ao evento. O que chega ao Sentry é
stack trace, request path, método HTTP e o `correlation_id` do `django-guid`. Para saber
*qual usuário* bateu num erro, o caminho é cruzar esse `correlation_id` — o mesmo que sai no
header `X-Correlation-Id` — com o log estruturado da requisição, não abrir o evento
esperando ver o e-mail direto.

Não reative `send_default_pii` como atalho de depuração: se um caso específico precisa de
mais contexto, anexe explicitamente via `sentry_sdk.set_context(...)` no ponto do código que
já sabe que aquele dado é seguro de sair, em vez de ligar a captura automática para todo
evento. Ver [`privacy.md`](privacy.md) para o resto das regras de dado pessoal e LGPD.

`traces_sample_rate` e `profile_session_sample_rate` estão em `0.1` (10% das transações) —
mudar a amostragem é decisão de custo/observabilidade de cada projeto, não algo a inferir
daqui.

## Prometheus

Opcional, atrás de `ENABLE_PROMETHEUS` (`.env`). Ligado, expõe métricas em
`/monitoring/metrics` e instala os middlewares `PrometheusBefore`/`PrometheusAfter` — é por
isso que o part `observability` entra **por último** em `config/settings/base.py`: os dois
precisam envolver toda a stack de middleware.

```bash
docker compose --profile observability up   # sobe o app com ENABLE_PROMETHEUS e o Prometheus em :9090
```

A configuração de scrape já pronta fica em `tools/prometheus.yml`.

## Logs

Ver [`backend.md#logs`](backend.md#logs) para a convenção de `structlog` (logger nomeado,
evento como primeiro argumento, contexto como kwargs) — não duplicado aqui.

## Checklist

- [ ] contexto extra num evento do Sentry é explícito (`set_context`/`set_tag`), nunca
      via `send_default_pii`
- [ ] investigação de erro em produção cruza `correlation_id` entre Sentry e log, não
      assume e-mail/IP no evento
- [ ] métrica nova: `ENABLE_PROMETHEUS=True` local antes de assumir que ela aparece em
      `/monitoring/metrics`
