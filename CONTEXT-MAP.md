# Context Map

## Contexts

- [Core](./apps/core/CONTEXT.md): shared kernel — primitivos de domínio e comportamento
  de modelo reaproveitados pelos outros contextos
- [Accounts](./apps/accounts/CONTEXT.md): identidade do usuário — autenticação e perfil
- [UI](./apps/ui/CONTEXT.md): componentes Cotton genéricos — vocabulário visual
  (variante, cor, severidade), sem lógica de domínio

## Relationships

- **Core → Accounts**: Accounts usa os value objects `PersonName` e `PhoneNumber` e o
  valueset `Gender` de Core para compor `User` e `Profile`; nenhuma dependência no
  sentido inverso.
- **UI**: não depende de Core nem Accounts, e nenhum dos dois depende de UI — os
  componentes só consomem os tokens de tema (ADR 0012); quem os usa é template, não
  código Python de outro app.
