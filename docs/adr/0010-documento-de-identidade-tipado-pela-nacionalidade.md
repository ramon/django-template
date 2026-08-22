# 0010. Documento de identidade tipado pela nacionalidade, com suporte parcial a países

- **Status**: Aceito
- **Data**: 2026-08-22
- **Relacionados**: `apps/accounts/domain/value_objects/document.py`,
  `apps/accounts/models/mixins.py` (`DocumentMixin`)

## Contexto

`Profile.document` era um `CharField(max_length=11)` sem validação de dígito
verificador, pensado só para CPF (o comentário do `CONTEXT.md` dizia isso
explicitamente). O pedido era generalizar para "qualquer documento oficial de
qualquer país", mas sem prometer suporte a 100% dos países — só Brasil e EUA
ficam com validação de formato de verdade na primeira leva; os demais só
precisam ser aceitos, prontos para ganhar um validador próprio depois.

O projeto não tinha, até aqui, nenhum campo de país/nacionalidade em `Profile`,
nem lib de validação de documento.

## Decisão

`Profile` (via `DocumentMixin`, `apps/accounts/models/mixins.py`) ganha três
campos: `nationality` (`django_countries.fields.CountryField`, ISO 3166-1
completo), `document_type` (`apps.accounts.models.choices.DocumentType`, hoje
`CPF`/`SSN`/`PASSPORT`) e `document` (o número, normalizado sem pontuação).

`document_type` é **derivado de `nationality`**, nunca escolhido livremente:
`BR` força CPF, `US` força SSN, qualquer outra nacionalidade cai em passaporte.
`nationality` é opcional, mas uma vez preenchida, `document` passa a ser
obrigatório e validado de acordo — é a regra "brasileiro tem que informar um
CPF válido".

A validação e a normalização moram em `apps.accounts.domain.value_objects.Document`
(um `pydantic.BaseModel`, seguindo o padrão de `PhoneNumber`/`PersonName` em
`apps.core.domain`), usando [`python-stdnum`](https://pypi.org/project/python-stdnum/)
(`stdnum.br.cpf`, `stdnum.us.ssn`) para CPF e SSN. Passaporte, por não ter
validador plugado ainda, só exige presença de ao menos um caractere
alfanumérico — sem checar formato.

## Consequências

- **Positivas**: extensão futura para outro país é registrar mais uma entrada
  no mapa nacionalidade→tipo do `Document` e (se o país tiver) plugar o módulo
  correspondente do `stdnum` — não é preciso desenhar arquitetura nova.
  `django-countries` cobre a lista de países sem manutenção própria.
- **Negativas**: duas dependências novas (`python-stdnum`, `django-countries`).
  `python-stdnum` valida CPF só pelo dígito verificador — não rejeita
  sequências repetidas (`111.111.111-11` passa no checksum), uma lacuna
  conhecida da lib, não deste projeto.
- **Neutras**: `document` continua único globalmente (não por país) — CPF (11
  dígitos) e SSN (9 dígitos) não colidem por tamanho, e a chance de colisão de
  string bruta entre um CPF/SSN e um passaporte de outro país é desprezível.

## Alternativas consideradas

### Documentos múltiplos por perfil (model `IdentityDocument` com FK)

Permitiria uma pessoa ter CPF *e* passaporte ao mesmo tempo. Não foi pedido —
o pedido era adaptar `Profile.document`, não introduzir relação 1:N. Fica como
extensão natural se a necessidade aparecer.

### `country` como "país emissor do documento", separado de nacionalidade

Mais preciso tecnicamente (documento e nacionalidade podem divergir, ex.:
residente estrangeiro), mas foi descartado a pedido explícito: o campo deve
representar a nacionalidade da pessoa, e a nacionalidade brasileira **exige**
CPF, não é so' uma sugestão de formato.

### Validadores próprios em vez de `python-stdnum`

Reimplementar o dígito verificador do CPF e o formato do SSN é código a mais
para manter e testar, com o mesmo risco de bugs que uma lib madura já cobre.
`python-stdnum` já cobre dezenas de países, o que casa com "preparado para
qualquer país, habilitado para alguns".

### `country`/nacionalidade como `TextChoices` manual (`BR`, `US`, `OTHER`)

Mais simples de implementar, mas um valor `OTHER` genérico não sabe *qual*
outro país é — não cumpre "funcionar para qualquer país", só finge que cumpre.
