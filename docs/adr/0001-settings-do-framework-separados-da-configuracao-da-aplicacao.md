# 0001. Settings do framework separados da configuração da aplicação

- **Status**: Aceito
- **Data**: 2026-08-18
- **Relacionados**: `docs/standards/backend.md`

## Contexto

Um `settings.py` de projeto Django acumula dois tipos de configuração que não têm nada em
comum além do arquivo: o que o framework exige para bootar (`DEBUG`, `SECRET_KEY`,
`DATABASES`, `MIDDLEWARE`) e o que a aplicação decide sobre si mesma (região padrão de
telefone, DSN do Sentry, flags de feature). Misturados, os dois herdam os defeitos um do
outro: a configuração de aplicação vira `getattr(settings, "X", default)` espalhado pelo
código, sem tipo nem validação, e o arquivo do framework cresce até ninguém achar nada.

O projeto também precisa de mais de um ambiente (desenvolvimento, teste, produção) sem
duplicar a base inteira em cada um.

## Decisão

São dois lugares, com ferramentas diferentes.

**`config/settings/`** — settings do framework, lidos com `django-environ`. A base é
partida em `parts/`, um módulo por assunto (`django`, `security`, `cache`, `logging`,
`celery`, `sentry`, `observability`, …), cada um exportando `__all__`.
`config/settings/base.py` importa todos com `import *`, e **a ordem desses imports é
semântica**: os parts mutam `INSTALLED_APPS` e `MIDDLEWARE` em sequência — por isso o
arquivo carrega `# ruff: noqa: I001` e o `observability` fica por último, já que os
middlewares do Prometheus precisam envolver toda a stack. Sobre a base ficam
`development.py`, `test.py` e `production.py`.

**`config/app_settings/`** — configuração de aplicação e de integrações, com
`pydantic-settings`, em três recortes por prefixo de ambiente: `AppSettings` (`APP_`),
`FeatureSettings` (`FEATURE_`) e `IntegrationSettings` (`INTEGRATION_`). Cada um é lido
por um acessor com `lru_cache`, e o código consome direto, sem passar por
`django.conf.settings`:

```python
from config.app_settings import get_app_settings

region = get_app_settings().phone_number_region  # APP_PHONE_NUMBER_REGION
```

Configuração nova de aplicação entra como campo tipado em um dos três modelos. Variável
solta em `config/settings/` é reservada para o que o Django ou uma app de terceiros lê
por nome.

## Consequências

- **Positivas**: configuração de aplicação passa a ser validada no boot e tipada para o
  MyPy; achar onde um assunto é configurado é achar o arquivo com esse nome; ambientes
  diferem por poucas linhas.
- **Negativas**: há dois lugares para procurar, e quem chega precisa aprender o critério
  de divisão. A ordem dos imports em `base.py` é uma armadilha silenciosa — reordenar
  "para organizar" muda o resultado, o que exigiu o `noqa` e este ADR.
- **Neutras**: o `.env` serve aos dois; a distinção aparece no prefixo do nome.

## Alternativas consideradas

### Um `settings.py` único com `os.environ`

O padrão do `startproject`. Recusado pelo motivo de sempre: cresce sem estrutura, e a
configuração de aplicação fica sem validação nem tipo.

### `django-configurations` (settings como classes)

Resolve a herança entre ambientes, mas mantém tudo no mesmo espaço de nomes do framework
e não dá validação de tipo para a configuração de aplicação — que era o problema maior.

### `pydantic-settings` para tudo, inclusive o framework

Tentador pela uniformidade, mas o Django lê settings por nome de módulo e espera
constantes em nível de módulo; embrulhar `INSTALLED_APPS` e `MIDDLEWARE` em um modelo
Pydantic acrescenta uma camada de tradução sem ganho, já que ninguém valida uma lista de
strings de app.
