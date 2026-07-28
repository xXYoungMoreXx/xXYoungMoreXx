# PLAN v3.1 — Hardening do Aethoria RPG Portfolio

**Status:** em execução
**Origem:** revisão cirúrgica de 2026-07-28 (segurança, desempenho, escalabilidade, funcionalidade, UI/UX)
**Base:** `main` @ `525318c`

---

## 1. Objetivo

Deixar o jogo do README **funcional, seguro e persistente**. A revisão encontrou que
(a) o pipeline nunca commitou um turno, (b) o título da issue é interpolado direto no
shell do workflow, e (c) parte das mecânicas anunciadas no README é placebo.

## 2. Escopo

### Em escopo

| # | Item | Onde |
|---|------|------|
| P0 | `git add` com pathspec inexistente (`rpg/raids.json`) aborta o stage → nenhum turno é commitado | `.github/workflows/rpg.yml` |
| S1 | Command injection via `${{ github.event.issue.title }}` dentro de `run:` | `.github/workflows/rpg.yml` |
| S2 | Raid forjável por qualquer issue `[RAID] <boss>` + pool de recompensa não dividido | `rpg/engine.py` |
| S3 | Texto de jogador renderizado sem escape no README público | `rpg/engine.py` |
| S4 | Argumentos de ação sem validação (path traversal em `rpg:desafiar:`) | `rpg/engine.py` |
| P1 | `cache: pip` sem arquivo de dependência (projeto é stdlib-only) | `.github/workflows/rpg.yml` |
| P2 | `fetch-depth: 0`, `urlopen` sem timeout, releituras de `raids.json`, `sb()` recalculado | ambos |
| F1 | Mini-boss de masmorra grava `bosses_defeated[terreno]` → relíquia/montaria de graça | `rpg/engine.py` |
| F2 | `rpg:reiniciar` relê o save existente → não reinicia | `rpg/engine.py` |
| F3 | `def_flat` agregado e nunca aplicado → 14 nós de skill tree inertes | `rpg/engine.py` |
| F4 | Entrada inválida (`rpg:habilidade:x`, `\1` no título) mata o processo sem feedback | `rpg/engine.py` |
| F5 | Level-up ressoma bônus de árvore; `mana_max: 30` de base virando +40/nível | `rpg/engine.py` |
| F6 | `action_rest`/`action_mount` checam a chave legada `active_monster` | `rpg/engine.py` |
| F7 | `.lower()` no título inteiro quebra PvP e mensagens de taverna | `rpg/engine.py` |
| F8 | `stun`/`burn` gateados por `cls_key=="mago"` | `rpg/engine.py` |
| F9 | `free_escape`, `regen`, `tavern_bonus`, `death_immunity`, `inventory`, `RECIPES.result` mortos | `rpg/engine.py` |
| F10 | `shop_price` com ramo inalcançável; poções de preços diferentes e efeito igual | `rpg/engine.py` |
| F11 | `price_mult` sempre `+0%`, `boss_key` cru na tabela de raid, HP duplicado, `dungeon_flawless` sem reset, craft destruindo passivos | `rpg/engine.py` |
| E1 | Relógio do mundo derivado de `turn` (por ação) em vez de tempo | `rpg/engine.py` |
| E2 | `rpg.yml` e `update-projects.yml` escrevem `README.md` sem concurrency comum | `.github/workflows/*` |
| E3 | Sem testes, sem validação de save, sem clamp de sanidade | `tests/`, `rpg/engine.py` |
| U1 | Log da jogada abaixo de 8 tabelas; ações impossíveis exibidas; legenda do mapa incompleta; skill tree sem botões | `rpg/engine.py` |
| U2 | `<img>` sem `alt` nos projetos em destaque | `.github/workflows/update-projects.yml` |
| U3 | Saves de teste e `max_hp: 10035` no perfil público | `rpg/players/`, `rpg/leaderboard.json` |
| U4 | Drift de documentação (issue template, SETUP, PRD) | docs |

### Fora de escopo (débito registrado)

- **Extrair conteúdo (mapa/monstros/classes/lore) para JSON.** ~600 linhas de dados;
  refactor mecânico de alto alcance sem ganho funcional. Fica para v3.2, depois que a
  suíte de testes estiver estabelecida como rede de segurança.
- **Dividir `engine.py` em pacote.** Mesma justificativa.
- **Rate limit por autor.** Precisa de decisão de produto (quantas ações/hora por
  jogador) antes de código.

## 3. Critérios de aceite

1. `python3 -m pytest tests/ -q` verde, cobrindo: todas as ações despachadas em `main()`,
   os 20 bugs acima como teste de regressão, e um teste de caracterização que renderiza
   o README de ponta a ponta.
2. Nenhuma expressão `${{ }}` com dado controlado por usuário dentro de um bloco `run:`.
3. `git add` do workflow stage-a de fato (verificado com `raids.json` ausente **e** presente).
4. Um turno completo (`rpg:classe:*` → `rpg:norte` → `rpg:atacar`) roda sem exceção e
   produz README, save, leaderboard e state consistentes.
5. `rpg/players/` sem usuário de teste; nenhum save com stat fora de faixa plausível.
6. SETUP.md e o issue template listam exatamente as ações que `main()` despacha.

## 4. Rollback

Cada unidade é uma branch mergeada em `main` com merge commit próprio:

- `fix/v3.1-ci` — workflows, `.gitattributes`, este plano
- `fix/v3.1-engine` — `rpg/engine.py`, `tests/`, higiene de dados, docs

Reverter uma unidade: `git revert -m 1 <merge-commit>`. Nada é publicado sem `git push`
explícito do dono do repositório — o merge fica local até então.

## 5. Ordem de execução

P0 → S1 → P1/P2/E2/U2 (unidade CI) → F1/F2 → F4 → F3/F8 → F5..F11 → S2/S3/S4 → E1/U1 →
testes → higiene de dados → docs.

Motivo da ordem: P0 e S1 são os únicos itens que afetam o repositório *hoje* em produção;
os testes vêm depois do grosso das correções para não travar o trabalho, mas antes da
higiene de dados, que depende do engine corrigido para regenerar o README.

## 6. Nota de paralelismo

A unidade CI é independente e roda em worktree própria. As demais convergem todas em
`rpg/engine.py` (1819 linhas, um arquivo) — paralelizar em worktrees separadas só
produziria conflito, então são sequenciais na mesma branch.
