# Blog — Adilson Menechini

Blog bilíngue (PT/EN) feito com [Hugo](https://gohugo.io/) + tema [PaperMod](https://github.com/adityatelange/hugo-PaperMod), publicado em:

> **https://adilsonmenechini.github.io/blog/**

## Desenvolvimento local

```bash
hugo server -D     # -D inclui rascunhos (draft: true)
```

Abra http://localhost:1313/blog/ — PT na raiz, EN em /blog/en/.

## Como publicar um artigo

1. Crie o artigo em Português:

   ```bash
   hugo new content posts/meu-novo-post.md
   ```

2. Crie a versão em Inglês com **o mesmo nome de arquivo** (é assim que o Hugo
   liga as duas traduções e o botão PT/EN funciona):

   ```bash
   hugo new content en/posts/meu-novo-post.md
   ```

3. Edite os dois arquivos em `content/posts/` e `content/en/posts/`, troque
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
├── hugo.yml                 # configuração (bilíngue, menus PT/EN)
├── content/
│   ├── posts/               # artigos em Português
│   ├── en/posts/            # artigos em English
│   ├── search/              # página de busca (PT)
│   └── en/search/           # página de busca (EN)
├── themes/PaperMod/         # tema (local)
└── .github/workflows/hugo.yml
```
