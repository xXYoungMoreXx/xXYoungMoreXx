#!/usr/bin/env python3
"""Suíte de regressão do Aethoria Engine.

Usa `unittest` da stdlib de propósito: o projeto é zero-dependência, então o CI roda
`python3 -m unittest discover -s tests` sem nenhum passo de instalação.

Cada teste da seção REGRESSÃO corresponde a um bug encontrado na revisão de 2026-07-28 e
falha na versão anterior do engine. A seção COBERTURA garante que toda ação despachável
sobrevive a uma execução completa, incluindo o render do README.

Rodar:  python3 -m unittest discover -s tests -v
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "rpg"))
import engine  # noqa: E402

README_SKELETON = """# Perfil

texto antes

<!-- RPG_START -->
placeholder
<!-- RPG_END -->

texto depois
"""


class EngineCase(unittest.TestCase):
    """Base: cada teste roda num diretório temporário com a mesma estrutura do repo."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aethoria-test-"))
        (self.tmp / "rpg" / "players").mkdir(parents=True)
        (self.tmp / "README.md").write_text(README_SKELETON, encoding="utf-8")
        self._cwd = os.getcwd()
        os.chdir(self.tmp)
        engine._raids_cache = None          # cache de processo não vaza entre testes
        engine.random.seed(1234)

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)
        engine._raids_cache = None

    # ── helpers ──────────────────────────────────────────────────────────────────
    def player(self, classe="guerreiro", **over):
        p = engine.new_player(over.pop("username", "Tester"))
        if classe:
            gs = engine.load_gs()
            engine.action_class(p, gs, classe)
        p.update(over)
        engine.recompute_maxima(p)
        return p

    def turn(self, title, user="Tester"):
        """Executa um turno pelo caminho real: parse -> dispatch -> render."""
        cmd, arg = engine.parse_action(title)
        gs = engine.load_gs()
        gs["turn"] = gs.get("turn", 0) + 1
        p = engine.load_player(user)
        p.pop("_new", None)
        # stderr também: o traceback que run_turn imprime ao conter um erro é
        # intencional, e poluiria a saída da suíte.
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            engine.run_turn(p, gs, cmd, arg, user)
            engine.check_conquistas(p, gs)
            lv = engine.check_lu(p)
            if lv:
                engine.push_log(p, lv)
            engine.apply_turn_regen(p)
            lb = engine.load_lb()
            engine.update_lb(lb, p)
            engine.save_lb(lb)
            engine.save_player(p)
            engine.save_gs(gs)
            engine.update_readme(p, gs, lb)
        return p, gs

    def readme(self):
        return (self.tmp / "README.md").read_text(encoding="utf-8")

    def patch(self, name, valor):
        """Substitui um atributo do engine e garante o restore.

        Precisa capturar o original ANTES de substituir: um cleanup que lê
        engine.__dict__[name] só roda depois, quando o valor já é o patch — e o
        vazamento contamina os testes seguintes."""
        original = getattr(engine, name)
        setattr(engine, name, valor)
        self.addCleanup(setattr, engine, name, original)
        return original

    def freeze_random(self, rand=0.99, randint=None):
        """Torna o combate determinístico. randint=None -> devolve o limite superior."""
        engine.random.random = lambda: rand
        engine.random.randint = (randint if randint is not None else (lambda a, b: b))
        engine.random.choice = lambda seq: seq[0]
        self.addCleanup(self._restore_random)

    def _restore_random(self):
        import random as _r
        engine.random.random = _r.random
        engine.random.randint = _r.randint
        engine.random.choice = _r.choice


# ══════════════════════════════════════════════════════════════════════════════════
#  COBERTURA — toda ação despachável sobrevive a um turno completo
# ══════════════════════════════════════════════════════════════════════════════════
class TestCoverage(EngineCase):

    ALL_ACTIONS = [
        "rpg:classe:guerreiro", "rpg:norte", "rpg:sul", "rpg:leste", "rpg:oeste",
        "rpg:atacar", "rpg:habilidade", "rpg:habilidade:0", "rpg:habilidade:1",
        "rpg:pocao", "rpg:interagir", "rpg:descansar", "rpg:taverna",
        "rpg:mensagem:ola aventureiros", "rpg:karma:good", "rpg:karma:bad",
        "rpg:comprar:pocao_menor", "rpg:comprar:pocao", "rpg:comprar:elixir_mana",
        "rpg:comprar:antidoto", "rpg:craftar:pocao_maior", "rpg:craftar:elixir_wyrd",
        "rpg:craftar:po_reliquias", "rpg:skill:gf1", "rpg:skill:gd1",
        "rpg:masmorra", "rpg:avancar", "rpg:fugir", "rpg:montar",
        "rpg:montar:ironhold", "rpg:desafiar:Alguem", "rpg:prestigio",
        "rpg:criar_raid:tita_de_gelo", "rpg:reiniciar",
    ]

    def test_every_action_completes_and_renders(self):
        for title in self.ALL_ACTIONS:
            with self.subTest(action=title):
                p, _ = self.turn(title)
                md = self.readme()
                self.assertIn("<!-- RPG_START -->", md)
                self.assertIn("<!-- RPG_END -->", md)
                self.assertIn("texto antes", md, "conteúdo fora dos marcadores foi perdido")
                self.assertIn("texto depois", md)
                self.assertTrue(p["log"], "nenhum feedback no log")

    def test_garbage_titles_never_crash(self):
        lixo = [
            "rpg:habilidade:naoumnumero", "rpg:habilidade:-5", "rpg:habilidade:999",
            "rpg:classe:inexistente", "rpg:skill:zzz", "rpg:comprar:nada",
            "rpg:craftar:nada", "rpg:montar:lua", "rpg:karma:talvez",
            "rpg:desafiar:../../../etc/passwd", "rpg:acaoquenaoexiste",
            "rpg:", "rpg:mensagem:", "rpg:raid_attack:naoumnumero",
        ]
        self.turn("rpg:classe:mago")
        for title in lixo:
            with self.subTest(action=title):
                p, _ = self.turn(title)
                self.assertIn("<!-- RPG_END -->", self.readme())

    def test_end_to_end_via_subprocess(self):
        """O caminho que o workflow realmente usa: python3 rpg/engine.py <titulo> <user>."""
        shutil.copytree(REPO / "rpg", self.tmp / "rpg", dirs_exist_ok=True)
        for f in (self.tmp / "rpg" / "players").glob("*.json"):
            f.unlink()
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        for title in ("rpg:classe:barbaro", "rpg:norte", "rpg:atacar", "rpg:taverna"):
            r = subprocess.run([sys.executable, "rpg/engine.py", title, "Tester"],
                               cwd=self.tmp, capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 0, f"{title} falhou:\n{r.stdout}\n{r.stderr}")
        save = json.loads((self.tmp / "rpg" / "players" / "Tester.json").read_text("utf-8"))
        self.assertEqual(save["classe"], "barbaro")
        self.assertIn("AETHORIA", self.readme())


# ══════════════════════════════════════════════════════════════════════════════════
#  REGRESSÃO — um teste por bug corrigido
# ══════════════════════════════════════════════════════════════════════════════════
class TestRegressions(EngineCase):

    # ── F1: exploit da masmorra ──────────────────────────────────────────────────
    def test_dungeon_miniboss_does_not_credit_world_boss(self):
        """Matar o mestre de masmorra em Kragdor dava a relíquia de Drakar, a montaria
        dracônica e a conquista de chefão. O save do dono do repo tinha
        bosses_defeated={"Tundra Glacial": true} — terreno que não tem chefão."""
        p = self.player("barbaro", level=8)
        p["position"] = {"x": 3, "y": 2}                  # Masmorra de Kragdor
        self.assertEqual(engine.terrain(p), "Masmorra de Kragdor")
        p["in_dungeon"] = True
        p["dungeon_terrain"] = "Masmorra de Kragdor"
        p["dungeon_room"] = engine.DUNGEON_MAX_ROOMS
        gs = engine.load_gs()
        mini = {"nome": "Troll-Rei de Kragdor", "hp": 0, "max_hp": 200, "atk": 60,
                "xp_reward": 75, "gold_range": (35, 60), "emoji": "👹", "is_boss": True}
        engine.resolve_kill(p, mini, gs)

        self.assertEqual(p.get("bosses_defeated", {}), {},
                         "mini-boss de masmorra creditou chefão do mundo")
        self.assertEqual(p.get("relics", []), [], "mini-boss dropou relíquia de chefão")
        self.assertFalse(p.get("dragon_mount"), "mini-boss liberou montaria dracônica")
        self.assertIn("Troll-Rei de Kragdor", p.get("dungeon_bosses_killed", []))
        engine.check_conquistas(p, gs)
        self.assertNotIn("primeiro_chefao", p["conquistas"])

    def test_world_boss_still_credits_normally(self):
        """Contraprova de F1: o chefão real continua dando relíquia e crédito."""
        p = self.player("barbaro", level=8)
        p["position"] = {"x": 3, "y": 2}
        gs = engine.load_gs()
        bd = engine.BOSSES["Masmorra de Kragdor"]
        boss = {"nome": bd["nome"], "hp": 0, "max_hp": 200, "atk": 55,
                "xp_reward": bd["xp"], "gold_range": bd["gold_range"],
                "emoji": bd["emoji"], "is_boss": True}
        engine.resolve_kill(p, boss, gs)
        self.assertTrue(p["bosses_defeated"].get("Masmorra de Kragdor"))
        self.assertTrue(p["dragon_mount"])
        self.assertEqual([r["id"] for r in p["relics"]], ["escama_drakar"])

    def test_dungeon_miniboss_does_not_inherit_boss_phases(self):
        p = self.player("barbaro", level=8)
        p["position"] = {"x": 3, "y": 2}
        p["in_dungeon"] = True
        gs = engine.load_gs()
        mini = {"nome": "Troll-Rei de Kragdor", "hp": 50, "max_hp": 230, "atk": 65,
                "is_boss": True}
        engine._check_boss_phase(p, gs, mini)
        self.assertEqual(p.get("boss_phase", 0), 0)
        self.assertEqual(mini["atk"], 65, "mini-boss herdou ATK de fase do Drakar")

    # ── F2: reset ────────────────────────────────────────────────────────────────
    def test_reset_actually_resets(self):
        """action_reset chamava load_player(), que relê o arquivo do disco — o save
        antigo voltava inteiro. O README mostrava "Nova lenda começa" com nível 5."""
        self.turn("rpg:classe:guerreiro")
        p, _ = self.turn("rpg:norte")
        p["level"], p["gold"], p["kills"] = 5, 392, 16
        p["conquistas"] = ["primeiro_sangue", "rico"]
        engine.save_player(p)

        p2, _ = self.turn("rpg:reiniciar")
        self.assertEqual(p2["level"], 1)
        self.assertEqual(p2["gold"], 10)
        self.assertEqual(p2["kills"], 0)
        self.assertIsNone(p2["classe"])
        self.assertEqual(p2["conquistas"], [])
        self.assertEqual(p2["position"], {"x": 2, "y": 2})

    # ── F3: def_flat ─────────────────────────────────────────────────────────────
    def test_def_flat_reduces_incoming_damage(self):
        """14 nós defensivos eram agregados em sb() e nunca lidos: monster_hits usava
        só p["defense"]."""
        self.freeze_random()
        base = self.player("guerreiro")
        armored = self.player("guerreiro", skills_unlocked=["gd1", "gd2"])   # +23 DEF
        self.assertEqual(engine.total_def(base), 10)
        self.assertEqual(engine.total_def(armored), 33)

        for p in (base, armored):
            p["hp"] = p["max_hp"]
            engine.monster_hits(p, {"nome": "Ogro", "atk": 60, "hp": 100, "max_hp": 100})
        self.assertGreater(armored["hp"], base["hp"],
                           "bônus de DEF da árvore não reduziu dano")

    # ── F4: entrada inválida ─────────────────────────────────────────────────────
    def test_invalid_skill_index_does_not_crash(self):
        self.turn("rpg:classe:mago")
        p, _ = self.turn("rpg:habilidade:naoumnumero")
        self.assertIn("<!-- RPG_END -->", self.readme())

    def test_regex_backreference_in_title_does_not_break_readme(self):
        r"""Um `\1` no título virava backreference no re.sub() do renderer e levantava
        re.error; `\g<0>` reinjetava o bloco antigo dentro de si mesmo."""
        self.turn("rpg:classe:mago")
        for payload in (r"rpg:mensagem:\1", r"rpg:mensagem:\g<0>", r"rpg:qualquer\1coisa"):
            with self.subTest(payload=payload):
                self.turn(payload)
                md = self.readme()
                self.assertEqual(md.count("<!-- RPG_START -->"), 1)
                self.assertEqual(md.count("<!-- RPG_END -->"), 1)

    def test_dispatch_exception_is_contained(self):
        """Exceção inesperada não pode matar o turno: o estado tem de ser salvo."""
        def explode(*a, **k):
            raise RuntimeError("boom")
        self.patch("action_attack", explode)
        self.turn("rpg:classe:mago")
        p, _ = self.turn("rpg:atacar")
        self.assertTrue(any("Erro interno" in l for l in p["log"]))
        self.assertIn("<!-- RPG_END -->", self.readme())

    # ── F5: máximos derivados ────────────────────────────────────────────────────
    def test_maxima_are_derived_not_accumulated(self):
        """`max_hp += 18 + sk["hp_max"]` ressomava o bônus da árvore a cada nível, e
        sb() semeava mana_max=30, dando +40 de mana por nível sem skill nenhuma."""
        p = self.player("guerreiro")
        self.assertEqual((p["max_hp"], p["max_mana"]), (130, 40))
        p["level"] = 5
        engine.recompute_maxima(p)
        self.assertEqual(p["max_hp"], 130 + 18 * 4)      # 202, não 10035
        self.assertEqual(p["max_mana"], 40 + 10 * 4)      # 80, não 200

    def test_check_lu_is_idempotent_and_multi_level(self):
        p = self.player("guerreiro")
        p["xp"] = engine.XP_TABLE[5]                      # pula direto para o nível 5
        msg = engine.check_lu(p)
        self.assertEqual(p["level"], 5, "check_lu subia só um nível por chamada")
        self.assertIn("4 pontos", msg)
        hp_depois = p["max_hp"]
        engine.check_lu(p); engine.check_lu(p)            # chamado 2x no mesmo turno
        self.assertEqual(p["max_hp"], hp_depois, "check_lu não é idempotente")

    def test_skill_hp_bonus_applies_immediately(self):
        p = self.player("guerreiro", skill_points=2, skills_unlocked=["gd1"])
        antes = p["max_hp"]
        engine.action_unlock_skill(p, "gd2")              # +15 DEF · +35 HP máx
        self.assertEqual(p["max_hp"], antes + 35)

    # ── F6: chave legada active_monster ──────────────────────────────────────────
    def test_cannot_rest_or_mount_while_fighting(self):
        p = self.player("guerreiro", dragon_mount=True)
        p["position"] = {"x": 2, "y": 2}                  # Ironhold, zona segura
        p["hp"] = 10
        p["active_monsters"] = [{"nome": "Bandido", "hp": 20, "max_hp": 20, "atk": 18}]
        gs = engine.load_gs()
        engine.action_rest(p)
        self.assertEqual(p["hp"], 10, "descansou no meio do combate")
        engine.action_mount_to(p, gs, "porto")
        self.assertEqual(p["position"], {"x": 2, "y": 2}, "teleportou no meio do combate")

    def test_legacy_singular_key_still_blocks(self):
        p = self.player("guerreiro")
        p["position"] = {"x": 2, "y": 2}
        p["hp"] = 10
        p["active_monster"] = {"nome": "Bandido", "hp": 20, "max_hp": 20, "atk": 18}
        engine.action_rest(p)
        self.assertEqual(p["hp"], 10)

    # ── F7: case do argumento ────────────────────────────────────────────────────
    def test_parse_preserves_argument_case(self):
        self.assertEqual(engine.parse_action("rpg:desafiar:xXYoungMoreXx"),
                         ("rpg:desafiar", "xXYoungMoreXx"))
        self.assertEqual(engine.parse_action("RPG:NORTE"), ("rpg:norte", ""))
        self.assertEqual(engine.parse_action("rpg:mensagem:Olá: tudo bem?"),
                         ("rpg:mensagem", "Olá: tudo bem?"))

    def test_pvp_finds_player_with_uppercase_login(self):
        """O título inteiro era lowercased, então procurava xxyoungmorexx.json."""
        alvo = self.player("mago", username="xXYoungMoreXx", level=3, kills=5)
        engine.save_player(alvo)
        p, _ = self.turn("rpg:desafiar:xXYoungMoreXx", user="Tester")
        self.assertFalse(any("não encontrado" in l for l in p["log"]),
                         f"PvP não achou o alvo: {p['log']}")
        self.assertTrue(any("PvP" in l for l in p["log"]))

    def test_tavern_message_keeps_case(self):
        p = self.player("mago")
        p["position"] = {"x": 2, "y": 2}
        gs = engine.load_gs()
        engine.action_message(p, gs, "Cuidado com Malachar")
        self.assertIn("Cuidado com Malachar", gs["tavern_messages"][-1])

    # ── F8: stun/burn desacoplados da classe ─────────────────────────────────────
    def test_stun_works_for_non_mago_classes(self):
        """O gate era `if cls_key == "mago"`, então Fender Crânios (bárbaro) e Prisão
        Óssea (necromante) nunca atordoavam."""
        self.freeze_random(rand=0.0)
        for classe, nodes in (("barbaro", ["baf1", "baf2"]), ("necromante", ["ns1", "ns2"])):
            with self.subTest(classe=classe):
                p = self.player(classe, skills_unlocked=nodes)
                sk = engine.sb(p)
                self.assertGreater(sk["stun"], 0)
                m = {"nome": "Alvo", "hp": 100, "max_hp": 100, "atk": 20}
                self.assertTrue(engine._apply_skill_effects(p, m, sk, classe))

    def test_burn_works_for_bruxo(self):
        p = self.player("bruxo", skills_unlocked=["wxf1", "wxf2"])
        sk = engine.sb(p)
        self.assertEqual(sk["burn"], 8)
        m = {"nome": "Alvo", "hp": 100, "max_hp": 100, "atk": 20}
        engine._apply_skill_effects(p, m, sk, "bruxo")
        self.assertTrue(m.get("burning"))

    # ── F9: features declaradas e nunca implementadas ────────────────────────────
    def test_free_escape_always_escapes(self):
        self.freeze_random(rand=0.99)                     # falharia na chance normal
        p = self.player("ladino", skills_unlocked=["ls1"])
        p["active_monsters"] = [{"nome": "Ogro", "hp": 50, "max_hp": 50, "atk": 30}]
        engine.action_flee(p, engine.load_gs())
        self.assertEqual(p["active_monsters"], [], "free_escape não funcionou")

    def test_regen_applies_every_turn(self):
        """"+X HP por turno vivo" só era aplicado ao matar um inimigo."""
        p = self.player("paladino", skills_unlocked=["pas1", "pas2"])   # regen 8
        p["hp"] = p["max_hp"] - 50
        engine.apply_turn_regen(p)
        self.assertEqual(p["hp"], p["max_hp"] - 42)

    def test_regen_does_not_overheal_or_revive(self):
        p = self.player("paladino", skills_unlocked=["pas1", "pas2"])
        p["hp"] = p["max_hp"]
        engine.apply_turn_regen(p)
        self.assertEqual(p["hp"], p["max_hp"])
        p["hp"] = 0
        engine.apply_turn_regen(p)
        self.assertEqual(p["hp"], 0, "regen ressuscitou o jogador")

    def test_tavern_boss_bonus_is_consumed(self):
        p = self.player("guerreiro", tavern_bonus={"boss_atk": 15})
        boss = {"nome": "Drakar", "is_boss": True}
        self.assertEqual(engine.consume_tavern_bonus(p, boss), 15)
        self.assertEqual(engine.consume_tavern_bonus(p, boss), 0, "bônus não foi gasto")
        p["tavern_bonus"] = {"boss_atk": 15}
        self.assertEqual(engine.consume_tavern_bonus(p, {"nome": "Rato"}), 0,
                         "bônus anti-chefão aplicou em inimigo comum")

    def test_death_immunity_relic(self):
        relic = engine.BOSSES["Ruínas de Vel'Moran"]["relic"]
        p = self.player("guerreiro", relics=[relic])
        p["hp"] = 0
        engine.death_reset(p)
        self.assertGreater(p["hp"], 0, "relíquia de imunidade não impediu a morte")
        self.assertEqual(p["deaths"], 0)
        p["hp"] = 0
        engine.death_reset(p)                             # imunidade já gasta
        self.assertEqual(p["deaths"], 1)
        engine.action_rest(p)                             # recarrega ao descansar
        self.assertFalse(p["death_immunity_used"])

    def test_crafting_creates_real_inventory_item(self):
        """`RECIPES[...]["result"]` era ignorado e `inventory` nunca era preenchido."""
        p = self.player("guerreiro", potions=3)
        engine.action_craft(p, "pocao_maior")
        self.assertEqual(len(p["inventory"]), 1)
        self.assertEqual(p["inventory"][0]["heal"], 120)
        self.assertEqual(p["potions"], 0, "ingredientes não foram consumidos")

        p["hp"] = 10
        engine.action_potion(p)
        self.assertEqual(p["hp"], min(p["max_hp"], 130))
        self.assertEqual(p["inventory"], [], "item não foi consumido")

    def test_relic_consumption_is_reported(self):
        relics = [engine.BOSSES["Fortaleza das Sombras"]["relic"],
                  engine.BOSSES["Ilhas do Exílio"]["relic"]]
        p = self.player("guerreiro", relics=list(relics))
        engine.action_craft(p, "po_reliquias")
        self.assertEqual(p["relics"], [])
        self.assertTrue(any("passivos perdidos" in l for l in p["log"]))

    def test_dragon_rider_relic_grants_atk(self):
        p_sem = self.player("guerreiro")
        p_com = self.player("guerreiro", relics=[engine.BOSSES["Masmorra de Kragdor"]["relic"]])
        self.assertEqual(engine.sb(p_com)["atk_flat"] - engine.sb(p_sem)["atk_flat"], 12)

    # ── F10: economia ────────────────────────────────────────────────────────────
    def test_shop_price_hostile_tier_is_reachable(self):
        """`rep<-1` era testado antes de `rep<-3`, tornando o +40% inalcançável."""
        p = self.player("guerreiro")
        preco = engine.SHOP_BASE["pocao"]["price"]
        for rep, esperado in ((5, 0.80), (2, 0.90), (0, 1.00), (-2, 1.20), (-5, 1.40)):
            p["factions"] = {"ordem": rep, "circulo": 0, "pacto": 0}
            self.assertEqual(engine.shop_price(p, preco, "Ironhold"), int(preco * esperado),
                             f"faixa de reputação {rep} errada")

    def test_big_potion_heals_more_than_small(self):
        """Poção Grande custava quase o dobro e curava exatamente o mesmo."""
        p = self.player("guerreiro", gold=100, potions=0)
        p["position"] = {"x": 2, "y": 2}
        engine.action_buy(p, "pocao")
        self.assertEqual(p["inventory"][0]["heal"], 65)
        self.assertEqual(p["potions"], 0)
        engine.action_buy(p, "pocao_menor")
        self.assertEqual(p["potions"], 1)

    # ── F11: cosméticos visíveis no perfil ───────────────────────────────────────
    def test_price_effect_is_rendered(self):
        """`int((price_mult)-1)*100` mostrava "+0%" em todo evento."""
        ev = next(e for e in engine.WORLD_EVENTS if e["price_mult"] == 1.4)
        self.patch("get_event", lambda *a, **k: ev)
        self.turn("rpg:classe:guerreiro")
        self.turn("rpg:norte")
        self.assertIn("Preços +40%", self.readme())

    def test_raid_table_uses_display_name(self):
        engine.save_raids({"7": {"boss_key": "Tita de Gelo", "hp": 800, "max_hp": 1000,
                                 "status": "active", "participants": {"a": {"damage": 1}}}})
        self.turn("rpg:classe:guerreiro")
        md = self.readme()
        self.assertIn("Titã de Gelo Ancestral", md, "tabela mostrou o slug interno")

    def test_dungeon_flawless_resets_per_run(self):
        p = self.player("guerreiro", level=5, dungeon_flawless=True)
        p["position"] = {"x": 0, "y": 0}
        engine.action_dungeon(p, engine.load_gs())
        self.assertFalse(p["dungeon_flawless"], "flawless ficou True de uma run anterior")

    def test_map_legend_lists_every_location(self):
        p = self.player("guerreiro")
        legenda = engine.render_legend(p)
        for row in engine.WORLD_MAP:
            for local in row:
                self.assertIn(local, legenda, f"{local} não está na legenda")

    # ── S2: raid forjável e recompensa não dividida ──────────────────────────────
    def _fake_issue(self, login):
        payload = json.dumps({"title": "[RAID] Destruidor de Mundos",
                              "user": {"login": login}}).encode()

        class R:
            def read(self): return payload
            def __enter__(self): return self
            def __exit__(self, *a): return False
        return lambda *a, **k: R()

    def test_raid_from_user_issue_is_rejected(self):
        """Bastava o título casar com um World Boss: qualquer um abria
        `[RAID] destruidor de mundos` e farmava a recompensa."""
        self.patch("urlopen", self._fake_issue("atacante"))
        raids = {}
        raid, err = engine._raid_init_from_issue("tok", "99", raids)
        self.assertIsNone(raid)
        self.assertIn("não foi convocada pelo sistema", err)
        self.assertEqual(raids, {})

    def test_raid_from_bot_issue_is_accepted(self):
        self.patch("urlopen", self._fake_issue("github-actions[bot]"))
        raid, err = engine._raid_init_from_issue("tok", "99", {})
        self.assertIsNone(err)
        self.assertEqual(raid["boss_key"], "Destruidor de Mundos")

    def test_raid_rewards_are_split_between_participants(self):
        """Cada participante recebia o pool INTEIRO: 5 jogadores num Azazel geravam
        6.000 XP do nada."""
        bd = engine.WORLD_BOSSES["Destruidor de Mundos"]
        p = self.player("guerreiro", username="Tester")
        raid = {"boss_key": "Destruidor de Mundos", "hp": 0, "max_hp": 3000,
                "status": "defeated",
                "participants": {"Tester": {"damage": 500, "level": 5},
                                 "Outro1": {"damage": 100, "level": 3},
                                 "Outro2": {"damage": 50, "level": 3},
                                 "Outro3": {"damage": 10, "level": 3}}}
        with redirect_stdout(io.StringIO()):
            engine._raid_distribute_rewards(raid, bd, "Tester", p, engine.load_gs())
        parte = bd["xp_pool"] // 4
        self.assertEqual(p["xp"], int(parte * 1.5), "MVP não recebeu a parte dividida")
        outro = json.loads((self.tmp / "rpg" / "players" / "Outro1.json").read_text("utf-8"))
        self.assertEqual(outro["xp"], parte)
        total = p["xp"] + parte * 3
        self.assertLess(total, bd["xp_pool"] * 2)

    # ── S3: injeção de markdown no README ────────────────────────────────────────
    def test_tavern_message_is_escaped(self):
        p = self.player("mago")
        p["position"] = {"x": 2, "y": 2}
        gs = engine.load_gs()
        engine.action_message(p, gs, "[clique aqui](https://phishing.tld) <img src=x>")
        msg = gs["tavern_messages"][-1]
        for char in "[]<>":
            self.assertNotIn(char, msg, f"caractere {char!r} passou pelo escape")

    def test_unknown_action_echo_cannot_form_html_or_markdown(self):
        """O título é ecoado no README. O que importa não é a palavra sobreviver, é
        nenhuma tag/link conseguir se formar: `<`, `>`, `[`, `]` e `` ` `` caem."""
        self.turn("rpg:classe:mago")
        self.turn("rpg:<img src=x onerror=alert(1)>")
        self.turn("rpg:[phishing](https://evil.tld)")
        bloco = self.readme().split("<!-- RPG_START -->")[1].split("<!-- RPG_END -->")[0]
        eco = [l for l in bloco.splitlines() if "desconhecida" in l]
        self.assertTrue(eco, "o eco da ação inválida não apareceu")
        for linha in eco:
            # `> ` é o marcador de blockquote do renderer, não conteúdo do jogador.
            payload = linha.lstrip("> ")
            for char in "<>[]":
                self.assertNotIn(char, payload, f"{char!r} passou pelo escape em: {linha}")

    def test_esc_strips_markdown_and_control_chars(self):
        self.assertEqual(engine.esc("a<b>[c]`d`|e*f_g~h\\i{j}"), "abcdefghij")
        self.assertEqual(engine.esc("linha1\nlinha2"), "linha1linha2")
        self.assertEqual(len(engine.esc("x" * 500, 100)), 100)

    # ── S4: validação de argumento / path traversal ──────────────────────────────
    def test_username_traversal_is_rejected(self):
        for mau in ("../../../etc/passwd", "a/b", "..", "", "-inicio", "fim-",
                    "x" * 40, "com espaco", "nome;rm -rf /"):
            with self.subTest(login=mau):
                self.assertEqual(engine.safe_username(mau), "anon")
        for bom in ("xXYoungMoreXx", "a", "user-name", "a1-b2-c3"):
            with self.subTest(login=bom):
                self.assertEqual(engine.safe_username(bom), bom)

    def test_pvp_traversal_does_not_read_outside_players(self):
        fora = self.tmp / "segredo.json"
        fora.write_text('{"kills":1,"level":9,"bosses_defeated":{}}', encoding="utf-8")
        p, _ = self.turn("rpg:desafiar:../segredo")
        self.assertTrue(any("Login inválido" in l or "não encontrado" in l for l in p["log"]))

    def test_save_path_stays_inside_players_dir(self):
        p = engine.new_player("../../evil")
        engine.save_player(p)
        self.assertFalse((self.tmp.parent / "evil.json").exists())
        self.assertTrue((self.tmp / "rpg" / "players" / "anon.json").exists())

    # ── E1: relógio por tempo ────────────────────────────────────────────────────
    def test_world_clock_is_time_based_not_turn_based(self):
        """dia/noite era `turn//3` e evento `turn//15`: com o contador global
        compartilhado, jogadores ativos faziam tudo rotacionar em minutos."""
        manha = datetime(2026, 3, 1, 12, tzinfo=timezone.utc)
        noite = datetime(2026, 3, 1, 22, tzinfo=timezone.utc)
        self.assertIn("Dia", engine.dn(now=manha))
        self.assertIn("Noite", engine.dn(now=noite))

        ev1 = engine.get_event(now=manha)
        self.assertIs(engine.get_event(now=manha + timedelta(minutes=59)), ev1,
                      "evento mudou dentro da mesma janela")
        self.assertIsNot(engine.get_event(now=manha + timedelta(hours=engine.EVENT_HOURS)), ev1)

    def test_event_does_not_depend_on_turn_counter(self):
        gs = {"turn": 1}
        agora = datetime(2026, 5, 5, 9, tzinfo=timezone.utc)
        a = engine.get_event(gs, now=agora)
        gs["turn"] = 999999
        self.assertIs(engine.get_event(gs, now=agora), a)

    # ── E3: migração e clamp de save ─────────────────────────────────────────────
    def test_migrate_clamps_corrupt_maxima(self):
        """O save real do dono do repo tinha max_hp 10035 e max_mana 10079 no nível 5,
        exposto no README público."""
        corrupto = {"username": "Tester", "classe": "guerreiro", "level": 5,
                    "max_hp": 10035, "hp": 10035, "max_mana": 10079, "mana": 10079,
                    "xp": 655, "gold": 392, "kills": 16}
        (self.tmp / "rpg" / "players" / "Tester.json").write_text(
            json.dumps(corrupto), encoding="utf-8")
        p = engine.load_player("Tester")
        self.assertEqual(p["max_hp"], 130 + 18 * 4)
        self.assertEqual(p["max_mana"], 40 + 10 * 4)
        self.assertLessEqual(p["hp"], p["max_hp"])

    def test_migrate_fills_missing_keys_from_old_save(self):
        antigo = {"username": "Velho", "classe": "mago", "level": 2, "xp": 70}
        (self.tmp / "rpg" / "players" / "Velho.json").write_text(
            json.dumps(antigo), encoding="utf-8")
        p = engine.load_player("Velho")
        for k in ("karma", "factions", "inventory", "quests", "conquistas",
                  "raid_bosses_killed", "dungeons_cleared", "tavern_bonus"):
            self.assertIn(k, p, f"chave {k} não foi preenchida pela migração")
        self.assertEqual(p["level"], 2)

    def test_migrate_does_not_alias_defaults_between_saves(self):
        for nome in ("A", "B"):
            (self.tmp / "rpg" / "players" / f"{nome}.json").write_text(
                json.dumps({"username": nome, "classe": "mago", "level": 1}), encoding="utf-8")
        a = engine.load_player("A")
        b = engine.load_player("B")
        a["quests"][0]["concluida"] = True
        self.assertFalse(b["quests"][0]["concluida"], "saves compartilharam o mesmo objeto")

    def test_negative_values_are_clamped(self):
        ruim = {"username": "Tester", "classe": "mago", "level": 99,
                "gold": -50, "kills": -3, "potions": -1}
        (self.tmp / "rpg" / "players" / "Tester.json").write_text(
            json.dumps(ruim), encoding="utf-8")
        p = engine.load_player("Tester")
        self.assertEqual(p["level"], 10)
        self.assertEqual((p["gold"], p["kills"], p["potions"]), (0, 0, 0))

    # ── P2: cache de raids ───────────────────────────────────────────────────────
    def test_raids_are_read_from_disk_once(self):
        engine.save_raids({"1": {"boss_key": "Tita de Gelo", "hp": 10, "max_hp": 10,
                                 "status": "active", "participants": {}}})
        engine._raids_cache = None
        leituras = []
        orig = engine._rw

        def spy(path, data=None):
            if str(path).endswith("raids.json") and data is None:
                leituras.append(path)
            return orig(path, data)

        engine._rw = spy
        self.addCleanup(lambda: setattr(engine, "_rw", orig))
        engine.load_raids(); engine.load_raids(); engine.load_raids()
        self.assertEqual(len(leituras), 1, "raids.json foi lido do disco mais de uma vez")

    # ── I/O: newline estável ─────────────────────────────────────────────────────
    def test_json_written_with_lf(self):
        p = self.player("guerreiro")
        engine.save_player(p)
        raw = (self.tmp / "rpg" / "players" / "Tester.json").read_bytes()
        self.assertNotIn(b"\r\n", raw, "JSON gravado com CRLF")


if __name__ == "__main__":
    unittest.main(verbosity=2)
