# 🔒 Política de Segurança — Aethoria RPG Portfolio

## Versões Suportadas

| Versão | Suporte |
|--------|---------|
| 3.x    | ✅ Ativa |
| 2.x    | ⚠️ Apenas patches críticos |
| 1.x    | ❌ Encerrada |

## Reportando Vulnerabilidades

Este repositório é um portfólio pessoal com um jogo RPG. Não há dados sensíveis de usuários armazenados além de informações públicas do GitHub.

**Se você encontrar algum problema de segurança:**

1. **NÃO abra uma Issue pública** — isso pode expor a vulnerabilidade antes de ser corrigida
2. Envie um e-mail para: **morekaik27@gmail.com**
3. Inclua: descrição do problema, passos para reproduzir, impacto potencial

**Tempo de resposta esperado:** até 48 horas úteis.

## Escopo

### ✅ Em escopo
- Injeção de comandos via títulos de Issue (ex: tentativa de `rpg:../../../etc/passwd`)
- Manipulação do estado do jogo via conteúdo de Issue
- Vulnerabilidades no workflow do GitHub Actions

### ❌ Fora de escopo
- Trapaça no jogo (alterar score, fabricar conquistas) — é um jogo, não tem punição
- Ataques de engenharia social
- Issues sobre performance (latência da Action é esperada)

## Dados Armazenados

Os únicos dados armazenados são:
- `username` do GitHub (público por definição)
- Dados de jogo (nível, kills, posição, etc.) — sem dados pessoais
- Informações do perfil GitHub público (repos, stars, seguidores, linguagem) — já públicas

**Não há senhas, tokens, e-mails ou dados privados armazenados.**

O `GITHUB_TOKEN` usado pelo Actions tem escopo limitado a este repositório e é gerenciado pelo próprio GitHub.
