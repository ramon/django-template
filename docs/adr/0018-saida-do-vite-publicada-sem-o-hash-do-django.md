# 0018. Saída do Vite publicada sem o hash do Django

- **Status**: Aceito
- **Data**: 2026-09-16
- **Relacionados**: [0002](0002-vite-como-pipeline-de-assets-em-backend-integration.md), [`docs/standards/frontend.md`](../standards/frontend.md)

## Contexto

O [0002](0002-vite-como-pipeline-de-assets-em-backend-integration.md) põe `static/dist/`
dentro de `STATICFILES_DIRS` e deixa o `collectstatic` publicar o build com o
`CompressedManifestStaticFilesStorage` do ServeStatic, "com hash". Só que o Vite já
versiona o que gera pelo conteúdo (`dist/assets/shared-Ab12Cd34.js`), e os chunks se
importam por esse nome (`import "./shared-Ab12Cd34.js"`). O storage acrescentava o hash do
Django (`shared-Ab12Cd34.3f9c1e2d4b5a.js`), e o `{% static %}` devolvia esse outro nome.

Para o navegador são duas URLs e, portanto, dois módulos. O `modulepreload` que a tag
emite baixava uma cópia que ninguém executava, e o `import` baixava a outra: cada chunk
importado ia duas vezes pela rede. O defeito ficou latente enquanto havia um entry só e
nenhum chunk importado. Num projeto derivado com quatro entries, o chunk comum de 1,3 MB
era baixado duas vezes. A cópia pedida pelo nome do Vite ainda voltava com `max-age=60`,
porque o ServeStatic só reconhece como imutável o hash de 12 caracteres do Django.

Fora de `dist/` o manifest do Django continua necessário: os estáticos do admin, do
allauth (`account/`, `mfa/`) e das bandeiras são referenciados por `{% static %}` em
templates de terceiros e só têm versão pelo hash que o Django acrescenta.

## Decisão

Usamos `apps.core.storage.ViteManifestStaticFilesStorage` como storage de estáticos. É o
`CompressedManifestStaticFilesStorage` com uma exceção: o que está sob `dist/` fica com o
nome e o conteúdo que o Vite gerou. O `url()` dos CSS de `dist/` não é reescrito, porque o
nome já traz o hash daquele conteúdo. Todo o resto continua com o hash do Django, e a
compressão vale para tudo.

Os arquivos versionados pelo Vite (`dist/assets/<nome>-<hash>.<ext>`) saem com
`Cache-Control: max-age=315360000, public, immutable` por
`SERVESTATIC_ADD_HEADERS_FUNCTION` (`add_vite_cache_headers`, em
`config/settings/parts/storage.py`). O `SERVESTATIC_IMMUTABLE_FILE_TEST` não serve para
isso: o `ServeStaticMiddleware` sobrescreve `immutable_file_test` e ignora a configuração.

## Consequências

- **Positivas**: cada chunk é baixado uma vez e fica em cache como imutável; o
  `{% static %}` devolve o nome que os `import` pedem em todo lugar, inclusive com
  `STATIC_URL` num CDN; o `collectstatic` para de gerar cópias de `dist/` que ninguém pede.
- **Negativas**: um storage próprio sobre API interna do `HashedFilesMixin`
  (`hashed_name`, `url_converter`), que precisa ser conferido ao atualizar o Django ou o
  ServeStatic; a imutabilidade de `dist/` depende do padrão de nome do Vite
  (`[name]-[hash]`), e mudar `build.rollupOptions.output` exige rever a regex.
- **Neutras**: o `url()` de um CSS de `dist/` que aponte para fora de `dist/` não recebe mais
  o hash do Django; o Vite não gera esse caso sozinho.

## Alternativas consideradas

### Tag que monta a URL sem o storage

`STATIC_URL` + `dist/` + nome do manifest do Vite nas tags. Corrige o download duplicado sem
mexer no storage, mas deixa o `{% static 'dist/...' %}` devolvendo o nome errado em
qualquer outro lugar e mantém o `collectstatic` gerando cópias inúteis. Corrige o sintoma
na tag, não a origem.

### `CompressedStaticFilesStorage`, sem manifest nenhum

A saída do Vite dispensa o hash do Django, mas o admin, o allauth e as bandeiras do django-countries não: sem o
manifest, os ~780 arquivos deles voltariam a ter URL fixa e `max-age=60`, sem cache-busting
a cada deploy. Também se perde o erro que o manifest estrito dá para um `{% static %}` que
aponta para arquivo inexistente.

### `SERVESTATIC_IMMUTABLE_FILE_TEST`

É o nome óbvio para a parte do cache, mas o middleware ignora a configuração (ver
Decisão).
