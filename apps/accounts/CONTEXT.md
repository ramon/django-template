# Accounts

Identidade do usuário: credenciais de autenticação e o perfil pessoal que as estende.

## Language

**User**:
A identidade autenticável do sistema — e-mail (username field), senha e status de
conta (active/staff). Exige nome completo e telefone já na criação.
_Avoid_: account, login, conta

**Profile**:
Dados pessoais complementares ao User — nationality, document, document type, birth
date, Gender, avatar. Relação um-para-um com o User, criado automaticamente junto
com ele.
_Avoid_: account details, dados da conta

**Nationality**:
País de cidadania da pessoa. Opcional -- mas uma vez preenchida, exige um Document
válido para aquele país. Não é o país de residência nem o país emissor de um
documento específico.
_Avoid_: country, país

**Document**:
Número do documento oficial de identidade da pessoa, único por perfil. O formato
exigido depende da Nationality: CPF para `BR`, SSN para `US`. Qualquer outra
nacionalidade cai em passaporte, aceito sem checagem de formato -- o projeto está
preparado para validar mais países, mas só tem os dois de cima implementados.
_Avoid_: CPF, ID, SSN (são Document Type, não sinônimo de Document)

**Document Type**:
O tipo de Document guardado (`CPF`, `SSN`, `PASSPORT`). Derivado da Nationality,
nunca escolhido diretamente por quem preenche o perfil.
_Avoid_: document kind

**Avatar**:
Imagem de perfil enviada pelo usuário. Quando ausente, a URL exposta fica vazia --
não há avatar padrão gerado a partir de dado do usuário.
_Avoid_: foto, picture

**Age**:
Idade calculada a partir do birth_date do Profile no momento da leitura — nunca
armazenada.
_Avoid_: idade cadastrada
