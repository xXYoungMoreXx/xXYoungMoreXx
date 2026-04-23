# 📋 PRD — Product Requirements Document
## Aethoria: O Reino Fragmentado × Portfolio de Mauricio Caique

**Versão:** 3.0  
**Autor:** Mauricio Caique ([@xXYoungMoreXx](https://github.com/xXYoungMoreXx))  
**Status:** Ativo — Em Produção  
**Última atualização:** 2026

---

## 1. Visão Geral

### 1.1 Problema
Portfólios estáticos no GitHub são ignorados. Recrutadores e devs visitam um perfil, veem um README com texto e links, e partem. O tempo médio de atenção é de 8 segundos.

### 1.2 Solução
Transformar o README do perfil GitHub em uma **experiência interativa multi-usuário** que:
- Apresenta o portfólio profissional de forma cativante
- Engaja visitantes com um RPG jogável diretamente no browser
- Demonstra competências técnicas avançadas na própria infraestrutura do jogo
- Persiste saves individuais por visitante
- Integra dados reais do GitHub de cada jogador para personalização

### 1.3 Proposta de Valor
> *"Um portfólio que você joga, não só lê."*

---

## 2. Objetivos

### 2.1 Objetivos de Negócio
- [ ] Aumentar o tempo médio de visita ao perfil GitHub de <1 min para >5 min
- [ ] Gerar conversas orgânicas em entrevistas técnicas sobre a arquitetura do projeto
- [ ] Demonstrar proficiência em Python, CI/CD, GitHub Actions e API REST na prática
- [ ] Criar um diferencial de portfólio memorável e compartilhável

### 2.2 Objetivos Técnicos
- [ ] Engine RPG em Python puro (zero dependências externas)
- [ ] Execução completa em <60 segundos por Action (GitHub free tier)
- [ ] Save por usuário com memória persistente via arquivos JSON commitados
- [ ] Integração com GitHub API para personalização por perfil
- [ ] Zero custo mensal (repositório público = Actions ilimitadas)

---

## 3. Usuários

### 3.1 Personas

**Persona A — Recrutador Técnico**
- Visita dezenas de perfis por semana
- Quer entender stack e nível técnico rapidamente
- Diferencial: ver o portfólio em ação, não apenas listado

**Persona B — Desenvolvedor Curioso**
- Visitou o perfil por indicação ou trending
- Quer explorar a implementação técnica
- Diferencial: o jogo em si + pode ver o código do engine

**Persona C — Colaborador Potencial**
- Procura alguém para um projeto/startup
- Quer entender forma de pensar e criatividade
- Diferencial: a arquitetura do projeto demonstra capacidade de sistema

---

## 4. Funcionalidades — Fases Implementadas

### Fase 1 — Engine Base ✅
| Feature | Descrição | Status |
|---------|-----------|--------|
| Mapa 5×5 | 25 locais únicos com lore individual | ✅ |
| 4 Classes | Guerreiro, Mago, Caçador, Ladino | ✅ |
| Sistema de Combate | ATK/DEF/Mana/HP + contra-ataque | ✅ |
| 4 Chefões | Vel'Krath, Malachar, Drakar, Xal'thar | ✅ |
| 5 Missões | Narrativa conectada à lore | ✅ |
| Sistema de XP e Level | 10 níveis + tabela progressiva | ✅ |

### Fase 2 — Multi-User + Leaderboard ✅
| Feature | Descrição | Status |
|---------|-----------|--------|
| Save por usuário | `rpg/players/{username}.json` | ✅ |
| Leaderboard Top 20 | Score por XP + kills + bosses + conquistas + prestígio | ✅ |
| Log individual | 7 entradas por jogador | ✅ |
| Log global | 8 eventos do mundo compartilhados | ✅ |
| Concorrência | `concurrency: cancel-in-progress: false` | ✅ |

### Fase 3 — GitHub Profile Integration ✅
| Feature | Descrição | Status |
|---------|-----------|--------|
| Fetch de perfil | GitHub REST API via `urllib` (stdlib) | ✅ |
| Bônus por stars | Até +80 ouro inicial | ✅ |
| Bônus por seguidores | Até +80 XP inicial | ✅ |
| Afinidade de classe | Linguagem principal → classe recomendada | ✅ |
| Bônus veterano | Conta com 7+ anos → título especial | ✅ |
| Bônus repos | 15+ repos → +2 poções | ✅ |
| Skip de bots | Ignora `[bot]` automaticamente | ✅ |

### Fase 4 — Advanced RPG Systems ✅
| Feature | Descrição | Status |
|---------|-----------|--------|
| Skill Trees | 6 habilidades por classe (3 ramos × 2 tiers) | ✅ |
| Chefões Multi-fase | Vel'Krath 2F · Malachar 3F · Drakar 3F · Xal'thar 3F | ✅ |
| Eventos Mundiais | 7 eventos rotativos (a cada 15 turnos) afetam todos | ✅ |
| Sistema de Clima | Noite aumenta encontros | ✅ |
| Crafting | 3 receitas (pocao_maior, elixir_wyrd, po_reliquias) | ✅ |
| Relíquias | Drop único de cada chefão com passivo permanente | ✅ |
| Prestígio | Reset nível 10 → bônus permanente + badge | ✅ |
| Montaria Dracônica | Post-Drakar: teleporte para zonas seguras | ✅ |
| Economia por Facção | Preços variam por reputação (-20% a +40%) | ✅ |
| Taverna/Rumores | Hints de lore + recompensas aleatórias | ✅ |
| NPCs com Memória | 4 NPCs com diálogos contextuais por jogador | ✅ |
| Sistema de Veneno | DoT com stacks + antídoto | ✅ |
| PvP Fantasma | `rpg:desafiar:username` compara scores | ✅ |
| 17 Conquistas | Sistema de achievements persistentes | ✅ |
| Companheira Lyra | Companion que dá ATK bônus | ✅ |

---

## 5. Arquitetura Técnica

### 5.1 Stack
```
Linguagem:    Python 3.11 (stdlib only — zero pip installs)
Storage:      JSON files commitados no repositório
CI/CD:        GitHub Actions (gratuito para repos públicos)
API:          GitHub REST API v3 (via urllib, sem libs externas)
Rendering:    Markdown + GitHub README rendering
```

### 5.2 Fluxo de uma Jogada
```
Visitante clica num link no README
         ↓
Abre Issue com título: "rpg:norte"
         ↓
GitHub Actions detecta (on: issues: types: [opened])
         ↓
[concurrency group garante fila sequencial]
         ↓
Checkout do repositório
         ↓
engine.py recebe: title="rpg:norte" username="visitante"
         ↓
[Se novo jogador: fetch GitHub API → calcula bônus]
         ↓
Carrega: state.json + players/visitante.json + leaderboard.json
         ↓
Processa ação → atualiza estado → checa conquistas → atualiza leaderboard
         ↓
Re-renderiza bloco RPG_START...RPG_END no README.md
         ↓
git add + git commit + git push
         ↓
Comenta na Issue + fecha Issue
         ↓
Visitante vê README atualizado (~30-60s depois)
```

### 5.3 Estrutura de Arquivos
```
xXYoungMoreXx/
├── README.md                           ← portfólio + RPG
├── PRD.md                              ← este documento
├── CHANGELOG.md                        ← histórico de versões
├── CONTRIBUTING.md                     ← guia de contribuição
├── CODE_OF_CONDUCT.md                  ← código de conduta
├── SECURITY.md                         ← política de segurança
├── SETUP.md                            ← guia de instalação
├── rpg/
│   ├── engine.py                       ← motor v3 (~1150 linhas)
│   ├── state.json                      ← estado global (mundo, eventos, NPCs)
│   ├── leaderboard.json                ← ranking top 20
│   └── players/
│       ├── .gitkeep
│       └── {username}.json             ← save individual por jogador
└── .github/
    ├── workflows/
    │   ├── rpg.yml                     ← action principal (otimizada)
    │   └── snake.yml                   ← animação de contribuições
    └── ISSUE_TEMPLATE/
        └── rpg_action.yml              ← template de issue para o jogo
```

---

## 6. Métricas de Sucesso

| Métrica | Meta | Como medir |
|---------|------|------------|
| Jogadas únicas | >50 jogadores distintos | Arquivos em `rpg/players/` |
| Tempo médio de sessão | >5 min | Timestamps em `last_played` |
| Chefões derrotados | Pelo menos 1 de cada | `bosses_defeated` nos saves |
| Leaderboard ativo | Top 10 com score > 500 | `leaderboard.json` |
| Issues abertas | >100 issues de RPG | GitHub Insights |

---

## 7. Limitações Conhecidas

| Limitação | Impacto | Mitigação |
|-----------|---------|-----------|
| Latência 30-90s | Jogo assíncrono, não tempo real | Esperado para o formato |
| README cache GitHub | Pode demorar ~2min para atualizar | Instruir jogador a dar F5 |
| Conflito de commits | Dois jogadores simultâneos | `concurrency` group resolve via fila |
| Rate limit GitHub API | 5k req/hora (com token) | Mais do que suficiente |
| GitHub API offline | Novo jogador não recebe bônus | Tratado com try/except silencioso |

---

## 8. Roadmap Futuro

- [ ] v3.1 — Sistema de Guildas: jogadores podem criar grupos
- [ ] v3.2 — World Boss semanal: todos combatem o mesmo inimigo
- [ ] v3.3 — Marketplace: jogadores trocam itens entre si
- [x] v3.4 — Dungeons cooperativas (Raids): múltiplos jogadores atacam World Bosses via Issues `[RAID]` com sistema MVP, escalonamento de HP, 4 conquistas, auto-spawn e criação manual (`rpg:criar_raid:<slug>`)
- [ ] v3.5 — Lore expansível: sistema de capítulos da história principal

---

## 9. Referências e Inspiração

**Projetos similares:**
- [timburgan/multi-user-blog](https://github.com/timburgan/multi-user-blog) — Xadrez no README
- [JonathanGin42/JonathanGin42](https://github.com/JonathanGin42) — Connect Four no README
- [Platane/snk](https://github.com/Platane/snk) — Snake animation

**Literatura que inspirou a lore:**
- The Witcher — Andrzej Sapkowski
- A Song of Ice and Fire — George R.R. Martin
- The Lord of the Rings — J.R.R. Tolkien
- Eragon (Inheritance Cycle) — Christopher Paolini
- Throne of Glass — Sarah J. Maas
- A Court of Thorns and Roses — Sarah J. Maas
