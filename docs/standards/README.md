# Padrões

Convenções de código deste projeto, por área. Regras estáveis, escritas no presente: se um
documento aqui discorda do código, um dos dois está errado e a divergência precisa ser
resolvida — não ignorada.

| Documento | Cobre |
| --- | --- |
| [`backend.md`](backend.md) | anatomia de um app, camadas, models, API, configuração, tasks, tipagem |
| [`frontend.md`](frontend.md) | Vite e manifest, HTMX/Stimulus/Alpine, templates e Cotton, BEM |
| [`testing.md`](testing.md) | layout da suíte, fixtures, factories, e2e, o que testar |
| [`i18n.md`](i18n.md) | catálogo por app, `makemessages`, precedência |
| [`infra.md`](infra.md) | compose e os dois caminhos de dev, imagens, `Procfile`, variáveis, sondas |
| [`auth.md`](auth.md) | allauth, MFA, sessões, contas sociais, CORS da API |
| [`observability.md`](observability.md) | Sentry (sem PII), Prometheus |
| [`privacy.md`](privacy.md) | dado pessoal, LGPD e GDPR: minimização, PII em log, terceiro, decisões que cada projeto registra em ADR |
| [`git.md`](git.md) | commits, branches (git-flow), changelog e versionamento, PR, pre-commit, o que o CI verifica |
| [`quality-gates.md`](quality-gates.md) | qual gate se aplica a qual mudança, ordem de execução, por que cada um existe |

Setup, comandos e stack ficam no [`README.md`](../../README.md) da raiz; daqui a gente
linka em vez de repetir.

## Padrões herdados

Estes documentos vieram do `django-template` junto com o código que descrevem, e continuam
válidos enquanto o projeto não decidir diferente. Quando decidir: atualize o padrão **no
mesmo commit** que muda o código, e abra um ADR se a mudança for estrutural. Padrão que
descreve um código que não existe mais é a pior documentação possível — agentes o seguem.

## Escrevendo um padrão novo

Um padrão descreve o que já é verdade no código — não uma intenção. Se a regra ainda não
está aplicada, ela é um plano (`docs/plans/`) ou uma decisão a tomar (`docs/adr/`).

Prefira: a regra em uma frase, um exemplo curto do código real (por caminho, não colado), e
a armadilha que a regra evita. O *por quê* longo mora no ADR; aqui fica o link.
