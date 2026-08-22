# Padrões: dados pessoais, LGPD e GDPR

Este projeto guarda dado pessoal desde o dia zero: `User` (e-mail, nome, telefone) e
`Profile` (nacionalidade, documento, data de nascimento, gênero, avatar) —
[`apps/accounts/CONTEXT.md`](../../apps/accounts/CONTEXT.md). Isso coloca qualquer projeto
gerado daqui sob a Lei 13.709/2018 (LGPD) assim que tiver o primeiro usuário real. As duas
leis convergem nos princípios que este documento cobre (minimização, base legal, segurança,
direitos do titular), então as seções abaixo tratam as duas juntas e só separam onde elas
divergem de fato. Este documento registra o que o template já faz para minimizar e proteger
esse dado, e separa claramente o que **não** vem pronto — decisão que cada projeto tem que
tomar e registrar antes de ir a produção, no molde da MFA opcional em
[`auth.md`](auth.md#mfa).

O GDPR (Regulation (EU) 2016/679) se aplica além de projeto sediado ou hospedado na União
Europeia: o art. 3º tem alcance extraterritorial e pega qualquer controlador, onde quer que
esteja, que processa dado de titular que está na UE — inclusive oferecendo produto/serviço a
essas pessoas ou monitorando o comportamento delas. Não decida se o GDPR se aplica pela
localização da infraestrutura; decida por quem é o usuário. Projeto sem usuário na UE hoje
mas com esse plano deve tratar o GDPR como aplicável desde já, não como algo a resolver
quando o primeiro usuário europeu aparecer.

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
e [`backend.md#logs`](backend.md#logs) — resumo aqui só para o cruzamento com LGPD e GDPR:

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
tanto sob a LGPD quanto sob o GDPR, cujo art. 4(1) trata identificador pseudonimizado como
dado pessoal) para fora do perímetro que **já está no template por padrão** — projeto que
não pode compartilhar nem um hash de e-mail com terceiro precisa remover ou condicionar
esse fallback antes de ir a produção. Se o terceiro (Automattic/Gravatar) processa esse
dado fora do Brasil ou da UE, isso também é a transferência internacional descrita mais
abaixo — não um caso à parte.

## Segurança do dado armazenado

- Senha: `Argon2PasswordHasher`, único hasher habilitado — ver [`auth.md#senha`](auth.md#senha).
- `full_clean()` automático (ADR 0011) impede que dado inconsistente ou fora do formato
  esperado (documento, e-mail) chegue a ser persistido por um caminho que pulou validação.

## O que o template não decide — cada projeto registra em ADR antes de produção

Sem mecanismo pronto hoje, no molde de "MFA é opcional, decisão de cada projeto" em
[`auth.md`](auth.md#mfa). Onde LGPD e GDPR pedem a mesma coisa, é uma entrada só; onde
divergem, a diferença está explícita.

- **Consentimento**: não há captura de consentimento (timestamp + versão de política) em
  lugar nenhum. Necessário assim que o projeto coletar dado para finalidade que exija
  consentimento explícito — LGPD art. 7º/8º, GDPR art. 6(1)(a)/7. O GDPR também exige que
  retirar o consentimento seja tão fácil quanto dá-lo (art. 7(3)) — não construa um fluxo de
  opt-in sem o de opt-out correspondente.
- **Direitos do titular**: não existe endpoint de exportação nem de exclusão/anonimização
  de conta. LGPD arts. 9º/18 e GDPR arts. 15–20 (acesso, retificação, apagamento/"right to
  be forgotten", portabilidade) pedem essencialmente o mesmo conjunto de operações. Ao
  construir, decida e registre se é hard delete ou anonimização, e o que acontece com o que
  é encadeado ao `User` (`Profile`, avatar em storage, sessões do `allauth.usersessions`).
- **Retenção**: não há job de expurgo nem prazo definido. Definir e documentar antes do
  primeiro deploy com usuário real — prazo indefinido não é uma política, é ausência dela.
- **Notificação de incidente**: não há processo de resposta a vazamento. O GDPR fixa prazo:
  72 horas para notificar a autoridade supervisora após tomar conhecimento (art. 33); a
  LGPD pede "prazo razoável" à ANPD (art. 48), sem número fixo. Projeto sujeito ao GDPR
  precisa de um runbook que cumpra as 72h, não só "razoável".
- **Transferência internacional**: decidida junto da região de infraestrutura
  ([`infra.md`](infra.md)), não aqui. LGPD art. 33: provedor ou região fora do Brasil exige
  base legal da transferência. GDPR arts. 44–50: dado saindo do Espaço Econômico Europeu
  exige decisão de adequação da UE para o destino ou cláusulas contratuais padrão (SCC) —
  registre qual das duas no ADR que decide a infra.
- **Registro das operações de tratamento**: o GDPR art. 30 exige um registro formal (o quê,
  por quê, quem acessa, por quanto tempo) para a maioria dos controladores — não é opcional
  como a documentação de finalidade por campo já é sob a LGPD. Projeto sujeito ao GDPR
  mantém esse registro em compliance, alimentado pelo que este documento e o `CONTEXT.md`
  de cada app já descrevem por campo.
- **Encarregado/DPO**: papel organizacional, não técnico — este documento não é o lugar de
  registrar quem é. LGPD sempre exige um encarregado (art. 41); GDPR só exige um DPO formal
  para certos controladores (autoridade pública, monitoramento em larga escala, dado
  sensível em larga escala — art. 37) — avalie o enquadramento em vez de assumir que se
  aplica. Mantenha essa informação onde o projeto já guarda documentação de compliance.
- **Idade de consentimento de menor**: GDPR art. 8 fixa 16 anos como padrão (Estado-membro
  pode baixar até 13); LGPD trata como "melhor interesse da criança" via ECA, sem número
  fixo equivalente. Fluxo de cadastro que pode receber menor de idade sob GDPR precisa de
  verificação de idade e consentimento parental — não existe no template hoje.

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
- [ ] projeto com usuário na UE (ou que oferece serviço/monitora comportamento de gente na
      UE): GDPR tratado como aplicável desde já — runbook de notificação de 72h, avaliação
      da exigência de DPO (art. 37) e registro de tratamento (art. 30) resolvidos antes de
      produção, não só a via LGPD
