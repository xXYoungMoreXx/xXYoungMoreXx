# 📜 CHANGELOG — Aethoria: O Reino Fragmentado

Todas as mudanças notáveis são documentadas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

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
