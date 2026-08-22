# 0014. Remover o fallback de avatar para o Gravatar

- **Status**: Aceito
- **Data**: 2026-08-22
- **Relacionados**: [0008](0008-desativar-envio-de-pii-para-o-sentry.md),
  `docs/standards/privacy.md`

## Contexto

`AvatarMixin.avatar_url()` (`apps/accounts/models/mixins.py`), quando o perfil não tinha
imagem enviada, chamava `gravatar_url()` (`apps/accounts/services/gravatar.py`), que monta
`https://www.gravatar.com/avatar/{hash}` a partir do hash SHA-256 do e-mail do usuário. Sem
flag para desligar: todo `GET /profile/me` sem avatar próprio mandava esse hash para
`gravatar.com` — um serviço de terceiro fora do projeto — só para resolver uma imagem
padrão.

E-mail (e o hash dele) é dado pessoal tanto sob a LGPD quanto sob o GDPR (art. 4(1): um
identificador pseudonimizado ainda identifica a pessoa). Isso é o mesmo raciocínio que já
levou o projeto a desligar `send_default_pii` no Sentry (ADR 0008): dado pessoal não sai do
perímetro do projeto por padrão, sem alguém decidir explicitamente que aquele fluxo é
necessário e aceitável. O fallback do Gravatar nunca foi essa decisão explícita — era só o
jeito mais simples de sempre ter uma imagem para mostrar.

## Decisão

`AvatarMixin.avatar_url()` retorna a URL do avatar enviado ou string vazia — sem fallback
para nenhum serviço externo. `apps/accounts/services/gravatar.py` (e o pacote
`apps/accounts/services/`, que não tinha mais nada dentro) foi removido, junto com a
propriedade `email` que `AvatarMixin`/`Profile` mantinham só para alimentar essa chamada.

Resolver um avatar padrão quando o usuário não enviou um (iniciais, imagem estática local,
serviço de terceiro escolhido conscientemente) passa a ser decisão de cada projeto gerado a
partir do template, não algo que vem pronto.

## Consequências

- **Positivas**: nenhum dado do usuário sai para um terceiro por causa de avatar ausente;
  `GET /profile/me` para de ter um efeito colateral de rede (a chamada ao Gravatar já era
  só a URL montada, não uma requisição HTTP daqui, mas o navegador do cliente que carregasse
  `picture` fazia essa chamada em nome do usuário, sem ele saber).
- **Negativas**: perfil sem avatar agora devolve `picture` vazio em vez de sempre ter uma
  imagem — quem consome a API precisa de um fallback visual próprio (iniciais, placeholder
  local) em vez de contar com uma URL sempre válida.
- **Neutras**: `apps/accounts/services/` deixou de existir; volta a existir no dia em que
  algum efeito colateral de rede real precisar de um lugar para morar.

## Alternativas consideradas

### Manter o fallback, mas atrás de uma flag desligada por padrão

Preserva a opção para quem realmente quer avatar automático. Descartada pelo mesmo motivo
do ADR 0008: manter dado pessoal saindo do perímetro do projeto, ainda que opt-in, exige que
alguém lembre de manter a flag desligada em produção — reativação por engano ou por copiar
`.env` de outro ambiente é o tipo de erro silencioso que este projeto prefere não deixar
possível. Remover na origem não deixa esse caminho existir.

### Trocar o Gravatar por uma imagem padrão gerada localmente (iniciais, cor por hash do id)

Resolveria a UX sem enviar dado a terceiro, mas é decisão de apresentação de cada projeto
(que iniciais, que paleta), não algo que o template deveria impor. Fica registrado aqui como
o caminho natural para quem quiser um avatar padrão sem terceiro.
