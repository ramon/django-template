# 0011. `full_clean()` automático em `BaseModel.save()`

- **Status**: Aceito
- **Data**: 2026-08-22
- **Relacionados**: `apps/core/models/base.py`, [0010](0010-documento-de-identidade-tipado-pela-nacionalidade.md)

## Contexto

O `ADR 0010` criou uma regra de negócio real ("nacionalidade brasileira exige
CPF válido") implementada em `Profile.clean()`. Django, por padrão, **não**
chama `clean()`/`full_clean()` no `.save()` — só `ModelForm.full_clean()` o
faz. Um `Profile.objects.create(...)` ou `profile.save()` direto (de dentro de
um signal, script, ou teste) ignoraria a regra silenciosamente, porque nada
força a validação a rodar.

Uma regra "tem que" que só vale quando alguém lembra de chamar `full_clean()`
não é uma garantia — é sorte. O projeto não usa `bulk_create`/`bulk_update` em
lugar nenhum hoje (`grep` confirmado no repositório inteiro), então não há
caminho de escrita existente que dependa de pular a validação por performance.

## Decisão

`BaseModel.save()` (`apps/core/models/base.py`) chama `self.full_clean()`
antes de `super().save()`. Vale para todo model que herda de `BaseModel` —
hoje `User` e `Profile` — não só para quem tem uma regra de `clean()` custom.

Consequência direta: `bulk_create`/`bulk_update` **não devem ser usados** em
models que herdam `BaseModel`. Essas duas operações do Django escrevem direto
no banco via SQL em lote, sem instanciar `.save()` por linha — nenhum override
de `save()` alcança elas, então não há como "fazer elas chamarem
`full_clean()`" sem reimplementá-las como um loop de `.save()`, o que anula o
ganho de performance que elas existem para dar. Se um caso de uso realmente
precisar de escrita em lote num model com `BaseModel`, a validação vira
responsabilidade explícita de quem escreve o código naquele ponto.

## Consequências

- **Positivas**: regra de `clean()` (a de `DocumentMixin` e qualquer futura)
  vale em qualquer caminho de escrita — ORM direto, admin, management command,
  signal — não só em fluxo que passa por `ModelForm`.
- **Negativas**: todo `.save()` ganha o custo de `full_clean()` (validação de
  campo, `clean()`, `validate_unique()` — uma query a mais por constraint
  única). Para os volumes deste projeto (sem `bulk_create` nem hot path de
  escrita em massa) é aceitável; se um dia surgir um, o alerta é justamente
  "isso quer `bulk_create`, que não pode viver num model com `BaseModel`" e
  não "desliga a validação".
- **Neutras**: model com campo obrigatório (`blank=False`) que hoje é populado
  fora do Python (default do banco, por exemplo) passaria a falhar no
  `.save()` se a instância não tiver o valor em memória. Nenhum model atual
  depende disso — `User`/`Profile` só têm default em nível de Python/Django.

## Alternativas consideradas

### Sobrescrever `save()` só em `Profile`

Resolveria o caso concreto do CPF/SSN, mas deixaria a mesma lacuna aberta para
o próximo model com uma regra de `clean()` — cada um teria que lembrar de
repetir o override. Colocar em `BaseModel` torna a garantia o padrão, não uma
escolha por model.

### Confiar em `ModelForm`/`full_clean()` manual (não mudar nada)

É o comportamento padrão do Django. Descartado porque não sustenta um "TEM
QUE" de negócio: qualquer `.save()` direto — inclusive um teste ou um script
de manutenção — passaria por cima da regra sem erro nenhum.
