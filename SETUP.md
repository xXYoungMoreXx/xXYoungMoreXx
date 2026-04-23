# 🚀 Guia de Configuração — Aethoria RPG Portfolio v3

## 1. Criar o repositório especial do GitHub

Repositório com **mesmo nome do usuário** = aparece no perfil público.

1. https://github.com/new → Nome: `xXYoungMoreXx` → **Public** → Create
2. NÃO inicialize com README

## 2. Upload dos arquivos

```bash
git clone https://github.com/xXYoungMoreXx/xXYoungMoreXx.git
cd xXYoungMoreXx

# Copie TODA a estrutura:
# README.md, PRD.md, CHANGELOG.md, SETUP.md
# SECURITY.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md
# rpg/engine.py, rpg/state.json, rpg/leaderboard.json
# rpg/players/.gitkeep
# .github/workflows/rpg.yml, .github/workflows/snake.yml
# .github/ISSUE_TEMPLATE/rpg_action.yml

git add .
git commit -m "🚀 Aethoria RPG Portfolio v3 — lançamento"
git push origin main
```

## 3. Permissões das Actions

**Settings → Actions → General:**
- ✅ Read and write permissions
- ✅ Allow GitHub Actions to create and approve pull requests
- Save

## 4. Gerar Snake pela primeira vez

**Actions → 🐍 Snake → Run workflow → Run workflow**

Aguarde ~1 min. Branch `output` será criado.

## 5. Criar label `rpg-action`

**Issues → Labels → New label:**
- Nome: `rpg-action` · Cor: `#7c3aed` · Save

## 6. Repositórios em Destaque (já configurados)

Os 4 repositórios em destaque já estão preenchidos no README:
- `WP_Cogitari_Theme` · `RAG_Agent` · `xXYoungMoreXx.github.io` · `Curso-Em-V-deo---Python-3`

---

## ✅ Checklist

- [ ] Repositório `xXYoungMoreXx` criado como **público**
- [ ] Todos os arquivos no `git push`
- [ ] Read/write permissions ativadas
- [ ] Snake rodou (branch `output` existe)
- [ ] Label `rpg-action` criada
- [ ] Repositórios em destaque configurados

---

## 🎮 Referência Completa de Ações

### Movimento
| Issue | Efeito |
|-------|--------|
| `rpg:norte/sul/leste/oeste` | Move no mapa 5×5 |
| `rpg:montar:ironhold` | Teleporte dracônico para Ironhold |
| `rpg:montar:ashenvale` | Teleporte para Aldeia de Ashenvale |
| `rpg:montar:porto` | Teleporte para Porto da Perdição |

### Personagem
| Issue | Efeito |
|-------|--------|
| `rpg:classe:guerreiro` | Escolhe Guerreiro (HP:130, DEF:10) |
| `rpg:classe:mago` | Escolhe Mago (HP:85, MANA:100) |
| `rpg:classe:cacador` | Escolhe Caçador (HP:105, equilibrado) |
| `rpg:classe:ladino` | Escolhe Ladino (HP:95, críticos altos) |
| `rpg:classe:paladino` | Escolhe Paladino (HP:140, DEF:12) |
| `rpg:classe:necromante` | Escolhe Necromante (HP:85, MANA:120) |
| `rpg:classe:bardo` | Escolhe Bardo (HP:95, equilibrado) |
| `rpg:prestigio` | Prestígio (requer nível 10) |
| `rpg:reiniciar` | Reseta seu personagem |

### Combate
| Issue | Efeito |
|-------|--------|
| `rpg:atacar` | Ataque básico |
| `rpg:habilidade` | Habilidade especial (consome mana) |
| `rpg:pocao` | Usa uma poção de cura |

### Exploração
| Issue | Efeito |
|-------|--------|
| `rpg:interagir` | Interage com NPC ou local |
| `rpg:descansar` | Descansa em zona segura (+HP +Mana) |
| `rpg:taverna` | Ouve rumores (dica de lore + recompensa) |

### Compras (em Ironhold, Ashenvale, Porto, Mercado)
| Issue | Preço Base |
|-------|------------|
| `rpg:comprar:pocao_menor` | 8g |
| `rpg:comprar:pocao` | 15g |
| `rpg:comprar:elixir_mana` | 12g |
| `rpg:comprar:antidoto` | 10g |

> Preços variam -20% a +40% conforme reputação com a facção local.

### Crafting (combina itens do inventário)
| Issue | Ingredientes | Resultado |
|-------|-------------|-----------|
| `rpg:craftar:pocao_maior` | 3× Poção Menor | Poção Superior (+120 HP) |
| `rpg:craftar:elixir_wyrd` | 1× Poção + 1× Elixir Mana | Elixir Wyrd (+40 HP +40 Mana) |
| `rpg:craftar:po_reliquias` | 2× Relíquias | Pó de Relíquias (+200 XP) |

### Habilidades (Skill Tree)
Ganhe pontos ao subir de nível. Use `rpg:skill:ID` para desbloquear.

**⚔️ Guerreiro:**
| ID | Nome | Tier | Pré-req | Efeito |
|----|------|------|---------|--------|
| `gf1` | Lâmina Afiada | 1 | — | +6 ATK |
| `gf2` | Golpe Devastador | 2 | gf1 | +14 ATK · Crit +12% |
| `gd1` | Escudo de Ferro | 1 | — | +8 DEF |
| `gd2` | Muralha Viva | 2 | gd1 | +15 DEF · +35 HP máx |
| `gv1` | Sede de Sangue | 1 | — | Pós-kill: +20% dmg próximo |
| `gv2` | Berserker | 2 | gv1 | HP<30% → +80% ATK |

**🔮 Mago:**
| ID | Nome | Tier | Pré-req | Efeito |
|----|------|------|---------|--------|
| `mf1` | Chama Arcana | 1 | — | +8 ATK |
| `mf2` | Pilar de Fogo | 2 | mf1 | +18 ATK · Queima 6/turno |
| `mg1` | Armadura de Gelo | 1 | — | +7 DEF |
| `mg2` | Cristal de Inverno | 2 | mg1 | +12 DEF · Atordoa 30% |
| `mt1` | Canalização | 1 | — | +30 Mana máx |
| `mt2` | Relâmpago Duplo | 2 | mt1 | Habilidade -15 mana |

**🏹 Caçador:**
| ID | Nome | Tier | Pré-req | Efeito |
|----|------|------|---------|--------|
| `cp1` | Olho de Águia | 1 | — | Crit +22% |
| `cp2` | Tiro Fatal | 2 | cp1 | Precisão = 3× dano |
| `cs1` | Pele Dura | 1 | — | +28 HP máx |
| `cs2` | Regeneração | 2 | cs1 | +6 HP por turno vivo |
| `cb1` | Vínculo Animal | 1 | — | Companheiro +10 ATK |
| `cb2` | Chamado da Matilha | 2 | cb1 | 35% ataque duplo |

**🗡️ Ladino:**
| ID | Nome | Tier | Pré-req | Efeito |
|----|------|------|---------|--------|
| `ls1` | Passo Silencioso | 1 | — | Fuga sempre funciona |
| `ls2` | Assassino | 2 | ls1 | 1º ataque = Crit 2× |
| `lv1` | Lâmina Envenenada | 1 | — | 35% envenena (8 dmg/turno) |
| `lv2` | Nuvem Tóxica | 2 | lv1 | Veneno -20% ATK inimigo |
| `la1` | Reflexos Felinos | 1 | — | Esquiva 18% |
| `la2` | Dança das Lâminas | 2 | la1 | Ataque duplo sempre |

**🛡️ Paladino:**
| ID | Nome | Tier | Pré-req | Efeito |
|----|------|------|---------|--------|
| `paf1` | Arma Sagrada | 1 | — | +8 ATK |
| `paf2` | Golpe Purificador | 2 | paf1 | +14 ATK · Crítico +15% |
| `pad1` | Aura de Devoção | 1 | — | +10 DEF |
| `pad2` | Bastião da Luz | 2 | pad1 | +15 DEF · +40 HP máx |
| `pas1` | Fé Inabalável | 1 | — | +35 Mana máx |
| `pas2` | Cura Divina | 2 | pas1 | +8 HP por turno vivo |

**💀 Necromante:**
| ID | Nome | Tier | Pré-req | Efeito |
|----|------|------|---------|--------|
| `nf1` | Toque da Morte | 1 | — | +9 ATK |
| `nf2` | Ceifador de Almas | 2 | nf1 | +18 ATK · Ao matar: próx. atk +25% |
| `ns1` | Escudo de Ossos | 1 | — | +8 DEF |
| `ns2` | Prisão Óssea | 2 | ns1 | +12 DEF · Atordoa 30% |
| `nm1` | Pacto Sombrio | 1 | — | +40 Mana máx |
| `nm2` | Lorde Lich | 2 | nm1 | HP<30% → +85% ATK |

**🎵 Bardo:**
| ID | Nome | Tier | Pré-req | Efeito |
|----|------|------|---------|--------|
| `bf1` | Acorde Dissonante | 1 | — | +7 ATK base |
| `bf2` | Sinfonia da Ruína | 2 | bf1 | +12 ATK · Crítico +15% |
| `bs1` | Inspiração | 1 | — | Esquiva 18% |
| `bs2` | Dança Festiva | 2 | bs1 | Fuga sempre funciona |
| `bg1` | Canto de Cura | 1 | — | +6 HP por turno vivo |
| `bg2` | Bis | 2 | bg1 | 30% de ataque duplo |

### Social
| Issue | Efeito |
|-------|--------|
| `rpg:desafiar:USERNAME` | PvP fantasma vs outro jogador |

---

## 🗺️ Guia do Mapa

```
🌨️🏔️🗼🌊🏝️   ← Linha 0 (Norte extremo)
🌲🏘️🏚️🏰⛵   ← Linha 1
🌑🌾🏙️⛏️🌊   ← Linha 2 (começo: 🏙️ Ironhold x=2,y=2)
🌳🛕🏡⚙️⚓   ← Linha 3
🕳️💀⛪🕵️🔱   ← Linha 4 (Sul extremo)
```

**Zonas seguras** (sem encontros, compra, descanso): 🏙️ Ironhold · 🏘️ Ashenvale · 🏡 Ravenford · 🕵️ Mercado Negro · ⚓ Porto da Perdição

**Chefões**: 🏚️ Vel'Krath · 🏰 Lord Malachar · ⛏️ Drakar · 🏝️ Xal'thar

---

## ⚔️ Dungeons Cooperativas (Raids)

Raids são combates cooperativos contra **World Bosses** onde múltiplos jogadores unem forças!

### Como Participar
1. Crie uma issue com título `rpg:criar_raid:<slug>` (requer nível 5+)
2. Ou espere o sistema gerar uma Raid automaticamente a cada 30 turnos
3. Na Issue `[RAID]` criada, comente `/atacar` para causar dano ao Boss
4. Cada ataque usa seu dano de classe — o Boss contra-ataca com 60% de chance

### Mecânicas
| Mecânica | Descrição |
|----------|-----------|
| **Escalonamento** | Boss ganha HP extra por nível de cada novo participante |
| **Contra-ataque** | 60% de chance do Boss revidar após seu ataque |
| **MVP** | Quem causar mais dano total ganha +50% de recompensas |
| **Golpe Final** | Quem derrotar o Boss ganha +2 poções extras |
| **Recompensas** | Todos os participantes recebem XP e Gold ao vencer |
| **Cleanup** | Raids derrotadas são limpas automaticamente após 24h |

### World Bosses Disponíveis
| Boss | Slug | HP Base | ATK | XP | Gold |
|------|------|---------|-----|----|------|
| 🥶 Titã de Gelo Ancestral | `tita_de_gelo` | 1.000 | 40 | 500 | 200 |
| 🌋 Azazel, O Destruidor | `destruidor_de_mundos` | 2.500 | 65 | 1.200 | 500 |
| 👻 Drakon, O Dragão Fantasma | `drakon_fantasma` | 1.500 | 50 | 800 | 350 |
| 🦑 Thal'Zuun, O Kraken Abissal | `kraken_abissal` | 2.000 | 55 | 1.000 | 400 |
| 🌿 Ygdra, Guardiã Corrompida | `guardiao_corrompido` | 1.800 | 45 | 900 | 380 |

### Conquistas de Raid
| Conquista | Condição |
|-----------|----------|
| 🔥 Raider | Participar da primeira Raid |
| 🌟 MVP da Raid | Ser MVP em uma Raid |
| ⚔️ Veterano de Raids | Completar 5 Raids |
| 👑 Matador de Titãs | Derrotar todos os World Bosses |

---

Boa jornada em Aethoria! ⚔️
