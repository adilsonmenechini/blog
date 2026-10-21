# Adilson's Guide

**Adilson's Guide** — blog trilíngue (PT/EN/ES) feito com [Hugo](https://gohugo.io/) + tema [Mana](https://github.com/Livour/hugo-mana-theme), publicado em:

> **https://adilsonmenechini.github.io/blog/**

Idiomas: PT na raiz · EN em `/blog/en/` · ES em `/blog/es/`

## Desenvolvimento local

```bash
hugo server -D     # -D inclui rascunhos (draft: true)
```

Abra http://localhost:1313/blog/ — PT na raiz, EN em /blog/en/.

## Como publicar um artigo

1. Crie o artigo em Português:

   ```bash
   hugo new content pt/posts/meu-novo-post.md
   ```

2. Crie as versões com **o mesmo nome de arquivo** (é assim que o Hugo liga as
   traduções e o seletor de idioma funciona):

   ```bash
   hugo new content en/posts/meu-novo-post.md
   hugo new content es/posts/meu-novo-post.md
   ```

3. Edite os três arquivos em `content/{pt,en,es}/posts/`, troque
   `draft: true` por `draft: false` e faça `git push`.

O GitHub Actions (.github/workflows/hugo.yml) faz o build e o deploy
automaticamente para o GitHub Pages a cada push na branch `main`.

## Front matter de referência

```yaml
---
title: "Título do artigo"
date: 2026-10-20
draft: false
tags: ["SRE", "Kubernetes"]
summary: "Resumo curto que aparece na listagem."
---
```

## Atualizar o tema PaperMod

O tema está em `themes/PaperMod` (cópia local, sem git). Para atualizar:

```bash
rm -rf themes/PaperMod
git clone --depth 1 https://github.com/adityatelange/hugo-PaperMod themes/PaperMod
rm -rf themes/PaperMod/.git
```

## Estrutura

```
blog/
├── hugo.yml                 # produção (PaperMod, 3 idiomas)
├── hugo-mana.yml            # preview do tema Mana (não publica)
├── hugo-mikosch.yml         # preview do tema Mikosch (não publica)
├── content/
│   ├── pt/                  # artigos em Português (posts, about, search)
│   ├── en/                  # artigos em English
│   └── es/                  # artigos em Español
├── i18n/                    # strings PT/ES (tema e previews)
├── assets/images/           # avatar/monograma
├── layouts/partials/        # override do partial de imagem (tema Mana)
├── themes/                  # PaperMod (produção) + temas de preview locais
└── .github/workflows/hugo.yml
```
