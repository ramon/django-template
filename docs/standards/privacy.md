# Padrões: dados pessoais e LGPD

Este projeto guarda dado pessoal desde o dia zero: `User` (e-mail, nome, telefone) e
`Profile` (nacionalidade, documento, data de nascimento, gênero, avatar) —
[`apps/accounts/CONTEXT.md`](../../apps/accounts/CONTEXT.md). Isso coloca qualquer projeto
gerado daqui sob a Lei 13.709/2018 (LGPD) assim que tiver o primeiro usuário real. Este
documento registra o que o template já faz para minimizar e proteger esse dado, e separa
claramente o que **não** vem pronto — decisão que cada projeto tem que tomar e registrar
antes de ir a produção, no molde da MFA opcional em [`auth.md`](auth.md#mfa).

## Minimização

- **Dado derivado não é armazenado.** `Age` não é coluna nenhuma: é calculado a partir de
  `birth_date` a cada leitura, em `calculate_age` (`apps/accounts/domain/services.py`),
  exposto via `apps/accounts/presenters.py:26`. Atributo pessoal novo que pode ser derivado
  de um campo já existente segue o mesmo caminho — `property`/presenter — em vez de virar
  coluna nova no banco.
- **Documento não existe sem nacionalidade.** `Nationality` e `Document` são validados
  juntos em `Profile.clean()` ([ADR 0010](../adr/0010-documento-de-identidade-tipado-pela-nacionalidade.md)),
  e `full_clean()` roda automaticamente em todo `save()` de model com `BaseModel`
  ([ADR 0011](../adr/0011-full-clean-automatico-no-basemodel-save.md)) — não há caminho de
  escrita (view, admin, shell) que persista um documento sem o par nacionalidade/formato
  esperado.

## PII em log e observabilidade

Convenção já em vigor, coberta em detalhe em [`observability.md`](observability.md#sentry-erro-sem-pii)
e [`backend.md#logs`](backend.md#logs) — resumo aqui só para o cruzamento com LGPD:

- `send_default_pii=False` no Sentry ([ADR 0008](../adr/0008-desativar-envio-de-pii-para-o-sentry.md)):
  nenhum e-mail, IP ou cookie sai para o Sentry por padrão.
- `structlog` correlaciona por `correlation_id` (`django-guid`), não por dado pessoal —
  evento de log não carrega documento, data de nascimento ou e-mail como kwarg solto; se um
  caso precisa desse contexto, é `set_context`/`set_tag` explícito no ponto que já sabe que
  aquele dado é seguro de sair, nunca captura automática.

## Compartilhamento com terceiro já existente: Gravatar

`AvatarMixin` (`apps/accounts/models/mixins.py:32`) cai para `gravatar_url()`
(`apps/accounts/services/gravatar.py`) sempre que o usuário não tem avatar próprio — sem
flag para desligar. Isso envia o hash SHA-256 do e-mail do usuário para
`gravatar.com`, um serviço de terceiro fora do projeto, em toda resposta da API de perfil
que cai no fallback. É um fluxo de dado pessoal (ainda que hasheado, e-mail é dado pessoal
sob a LGPD) para fora do perímetro que **já está no template por padrão** — projeto que não
pode compartilhar nem um hash de e-mail com terceiro precisa remover ou condicionar esse
fallback antes de ir a produção.

## Segurança do dado armazenado

- Senha: `Argon2PasswordHasher`, único hasher habilitado — ver [`auth.md#senha`](auth.md#senha).
- `full_clean()` automático (ADR 0011) impede que dado inconsistente ou fora do formato
  esperado (documento, e-mail) chegue a ser persistido por um caminho que pulou validação.

## O que o template não decide — cada projeto registra em ADR antes de produção

Sem mecanismo pronto hoje, no molde de "MFA é opcional, decisão de cada projeto" em
[`auth.md`](auth.md#mfa):

- **Consentimento**: não há captura de consentimento (timestamp + versão de política)
  em lugar nenhum. Necessário assim que o projeto coletar dado para finalidade que exija
  consentimento explícito (art. 7º/8º) — marketing, cookie não essencial, compartilhamento
  com parceiro.
- **Direitos do titular** (acesso, correção, portabilidade, eliminação — arts. 9º e 18):
  não existe endpoint de exportação nem de exclusão/anonimização de conta. Ao construir um,
  decida e registre se é hard delete ou anonimização, e o que acontece com o que é
  encadeado ao `User` (`Profile`, avatar em storage, sessões do `allauth.usersessions`).
- **Retenção**: não há job de expurgo nem prazo definido. Definir e documentar antes do
  primeiro deploy com usuário real — prazo indefinido não é uma política, é ausência dela.
- **Transferência internacional** (art. 33): decidida junto da região de infraestrutura
  ([`infra.md`](infra.md)), não aqui. Provedor ou região fora do Brasil exige registrar a
  base legal da transferência (cláusula padrão, adequação) no ADR que decide a infra.
- **Controlador e encarregado (DPO)**: papel organizacional, não técnico — este documento
  não é o lugar de registrar quem é; mantenha essa informação onde o projeto já guarda
  documentação de compliance.

## Checklist

- [ ] campo de dado pessoal novo: computado a partir de um campo existente em vez de
      armazenado, quando possível (como `Age`); se precisar ser coluna, a finalidade está
      documentada no `CONTEXT.md` do app
- [ ] nenhum dado pessoal cru em `structlog` ou evento do Sentry — contexto explícito via
      `set_context`, nunca `send_default_pii`
- [ ] integração nova que envia dado pessoal a terceiro documenta o que sai e por quê,
      igual ao Gravatar aqui
- [ ] indo a produção com usuário real: consentimento (se aplicável), direitos do titular e
      retenção decididos e registrados em ADR — não fica para depois
