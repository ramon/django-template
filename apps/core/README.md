# Core

Base compartilhada do projeto: mixins de model, value objects, validadores,
apresentação de dados e as páginas/sondas que provam que a stack subiu.

Não é um domínio de negócio — é a fundação que os outros apps constroem em cima. Para
o vocabulário e as decisões de nomenclatura, veja [`CONTEXT.md`](CONTEXT.md).

## O que tem aqui

- **Mixins de model**: chave primária UUID v7, timestamps, soft delete, ordenação,
  nome de pessoa e telefone — prontos para qualquer model do projeto herdar em vez de
  reimplementar.
- **Value objects**: `PersonName` e `PhoneNumber`, que validam e formatam nome e
  telefone fora do banco (Pydantic), usados pelos mixins de model equivalentes.
- **Sondas de saúde**: `/health/` e `/health/workers/`, usadas por orquestrador e
  load balancer para saber se o processo está pronto para receber tráfego.
- **Página e task de exemplo**: `HomeView`/`ping` e a task `echo` do Celery existem
  para provar que a stack (Django, HTMX, Vite, fila) funciona de ponta a ponta. São
  scaffolding — veja "Começando um projeto a partir desta base" no
  [`AGENTS.md`](../../AGENTS.md) da raiz para saber o que apagar na primeira feature
  real.
- **Comandos `makemessages`/`compilemessages` customizados**: aplicam os idiomas do
  projeto sem precisar de flags na linha de comando.

## Para quem for mexer aqui

Referência da interface pública (o que importar, com que assinatura) fica em
[`AGENTS.md`](AGENTS.md). Convenções de código — camadas, testes, tipagem — ficam em
[`docs/standards/backend.md`](../../docs/standards/backend.md).
