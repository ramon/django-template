# Accounts

Identidade do usuário: credenciais de autenticação e o perfil pessoal que as estende.

## Language

**User**:
A identidade autenticável do sistema — e-mail (username field), senha e status de
conta (active/staff). Exige nome completo e telefone já na criação.
_Avoid_: account, login, conta

**Profile**:
Dados pessoais complementares ao User — document, birth date, Gender, avatar. Relação
um-para-um com o User, criado automaticamente junto com ele.
_Avoid_: account details, dados da conta

**Document**:
Identificador de 11 caracteres, único por perfil. Não validado por dígito verificador
no código atual.
_Avoid_: CPF, ID

**Avatar**:
Imagem de perfil enviada pelo usuário. Quando ausente, cai para o Gravatar.
_Avoid_: foto, picture

**Gravatar**:
Serviço externo que gera uma imagem a partir do hash do e-mail do usuário; usado como
avatar padrão quando nenhuma imagem foi enviada.

**Age**:
Idade calculada a partir do birth_date do Profile no momento da leitura — nunca
armazenada.
_Avoid_: idade cadastrada
