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

Boa jornada em Aethoria! ⚔️
