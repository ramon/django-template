# Core

Shared kernel: primitivos de domínio e comportamento de modelo reaproveitados por
todos os outros contextos. Não é, em si, uma capacidade de negócio.

## Language

**PersonName**:
Value object que separa o nome de uma pessoa em first/last e deriva variações — full,
familiar, abbreviated, sorted, initials, mentionable.
_Avoid_: nome completo (string crua), display name

**PhoneNumber**:
Value object em torno de um número de telefone validado, formatado em E.164
internamente e exposto em international/national/E164 e código do país.
_Avoid_: telefone (string crua)

**Gender**:
Valueset fixo (male/female/unknown) de gênero para fins legais/cadastrais. Nunca
obrigatório de início — assume unknown até ser informado.
_Avoid_: sexo

**Social name**:
Nome pelo qual a pessoa se apresenta no dia a dia, quando diferente do nome legal.
Texto livre, não derivado do `PersonName`.
_Avoid_: nome social preferido, display name

**Gender identity**:
Como a pessoa identifica seu próprio gênero, em texto livre — distinto do valueset
fixo `Gender`, porque identidade de gênero não é enumerável.
_Avoid_: gênero (quando autodeclarado)

**Pronouns**:
Os pronomes que a pessoa usa. Texto livre.
