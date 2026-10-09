# 0019. Separar suítes de teste no CI com banco por worker

- **Status**: Aceito
- **Data**: 2026-10-06
- **Relacionados**: `docs/standards/testing.md`, `docs/standards/quality-gates.md`

## Contexto

Testes sem banco, com banco e de browser têm custos e requisitos diferentes. A suíte
Python executava sequencialmente; testes transacionais limpam o banco com `flush`,
o que exige isolamento para executá-los em paralelo. A cobertura agregada deixaria
de representar a suíte completa se fosse aferida separadamente em cada job.

## Decisão

Executamos três jobs independentes. Os jobs sem banco e com banco usam dois workers do
pytest-xdist; o e2e roda num processo só. Com dois workers, o pytest do e2e caiu de 40 s
para 22 s, mas o job continuou em torno de 2m20, porque o tempo é dominado pelo setup
(Playwright, browsers e build do frontend). Selecionamos por necessidade de banco e pela
marca e2e, incluindo fixtures transitivas. O pytest-django cria um banco por worker no
PostgreSQL do job; artefatos de browser ficam separados por worker quando o e2e roda com
`-n`. O CI roda testes Python e JavaScript sem validação de cobertura. Mantemos os
comandos locais e os pisos de cobertura existentes.

## Consequências

- **Positivas**: suítes executam em paralelo; `flush` não interfere com outros workers;
  o job sem banco dispensa os serviços PostgreSQL e Valkey.
- **Negativas**: migrations são aplicadas por worker e os jobs repetem o setup; o CI
  não detecta queda de cobertura, que continua sendo verificada localmente.
- **Neutras**: testes que liberam banco manualmente precisam declarar a marca `database`.

## Alternativas consideradas

### Workers especializados numa única sessão

Exigiria um scheduler personalizado para reservar workers por categoria. Jobs separados
permitem configurar serviços e dependências conforme a suíte usando mecanismos padrão.

### Seleção apenas por diretório

Há testes em `unit/` que usam banco e testes transversais na raiz. Seleção pelas marcas e
fixtures acompanha esses requisitos sem manter listas de arquivos no workflow.

### Cobertura combinada no CI

Exigiria publicar e combinar artefatos dos jobs. Foi dispensada por decisão do usuário;
a validação local permanece disponível.
