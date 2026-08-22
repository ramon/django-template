# Context Map

## Contexts

- [Core](./apps/core/CONTEXT.md): shared kernel — primitivos de domínio e comportamento
  de modelo reaproveitados pelos outros contextos
- [Accounts](./apps/accounts/CONTEXT.md): identidade do usuário — autenticação e perfil

## Relationships

- **Core → Accounts**: Accounts usa os value objects `PersonName` e `PhoneNumber` e o
  valueset `Gender` de Core para compor `User` e `Profile`; nenhuma dependência no
  sentido inverso.
