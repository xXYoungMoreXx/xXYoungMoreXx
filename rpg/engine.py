#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   AETHORIA: O REINO FRAGMENTADO — Engine v3.0                               ║
║   Portfólio de Mauricio Caique (@xXYoungMoreXx)                             ║
║                                                                              ║
║   Fases implementadas:                                                       ║
║   [1] Engine base · Classes · Mapa · Chefões · Missões                      ║
║   [2] Save/usuário · Leaderboard · Guilda                                   ║
║   [3] GitHub Profile Integration · Bônus por métricas reais                 ║
║   [4] Skill Trees · Builds · Chefões Multi-fase · Eventos Globais           ║
║       Clima · Crafting · Prestígio · Montaria · Facções · Taverna · PvP     ║
║                                                                              ║
║   Inspirado em: The Witcher · Game of Thrones · Senhor dos Anéis            ║
║                 Eragon · Trono de Vidro · Corte de Espinhos e Rosas         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json, sys, random, re, os, unicodedata
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen

# ══════════════════════════════════════════════════════════════════════════════
#  WORLD MAP
# ══════════════════════════════════════════════════════════════════════════════
WORLD_MAP = [
    ["Tundra Glacial",       "Pico de Frostmourne",   "Torre do Oráculo",      "Mar Cinzento",          "Ilhas do Exílio"       ],
    ["Floresta de Mirewood", "Aldeia de Ashenvale",   "Ruínas de Vel'Moran",   "Fortaleza das Sombras", "Costa dos Náufragos"   ],
    ["Pântano de Morgraen",  "Planície Dourada",      "Ironhold",              "Masmorra de Kragdor",   "Mar do Sul"            ],
    ["Floresta Profunda",    "Templo Esquecido",      "Vilarejo de Ravenford", "Minas de Ferro",        "Porto da Perdição"     ],
    ["Cavernas Abissais",    "Floresta Amaldiçoada",  "Catedral em Ruínas",    "Mercado Negro",         "Litoral Proibido"      ],
]
MAP_EMOJI = {
    "Tundra Glacial":"🌨️","Pico de Frostmourne":"🏔️","Torre do Oráculo":"🗼",
    "Mar Cinzento":"🌊","Ilhas do Exílio":"🏝️","Floresta de Mirewood":"🌲",
    "Aldeia de Ashenvale":"🏘️","Ruínas de Vel'Moran":"🏚️","Fortaleza das Sombras":"🏰",
    "Costa dos Náufragos":"⛵","Pântano de Morgraen":"🌑","Planície Dourada":"🌾",
    "Ironhold":"🏙️","Masmorra de Kragdor":"⛏️","Mar do Sul":"🌊",
    "Floresta Profunda":"🌳","Templo Esquecido":"🛕","Vilarejo de Ravenford":"🏡",
    "Minas de Ferro":"⚙️","Porto da Perdição":"⚓","Cavernas Abissais":"🕳️",
    "Floresta Amaldiçoada":"💀","Catedral em Ruínas":"⛪","Mercado Negro":"🕵️",
    "Litoral Proibido":"🔱",
}
SAFE_ZONES  = {"Ironhold","Aldeia de Ashenvale","Vilarejo de Ravenford","Mercado Negro","Porto da Perdição"}
FACTION_ZONES = {"Ironhold":"ordem","Aldeia de Ashenvale":"circulo","Vilarejo de Ravenford":"circulo",
                  "Mercado Negro":"pacto","Porto da Perdição":"pacto"}
LOCATION_LORE = {
    "Tundra Glacial":"Ventos cortantes. Crânios de criaturas antigas emergem do gelo como avisos.",
    "Pico de Frostmourne":"O último Rei-Dragão desceu aqui para sua batalha final.",
    "Torre do Oráculo":"Paredes que sussurram em línguas mortas. Algo te conhece pelo nome.",
    "Mar Cinzento":"Águas cor de chumbo. Quem navega aqui não volta o mesmo.",
    "Ilhas do Exílio":"Para cá foram banidos os piores — e algo anterior a eles.",
    "Floresta de Mirewood":"Os elfos sumiram há três gerações. Mas algo ficou.",
    "Aldeia de Ashenvale":"A última comunidade livre. Há esperança aqui, e também medo.",
    "Ruínas de Vel'Moran":"A capital traída. O ar cheira a cinza e promessas quebradas.",
    "Fortaleza das Sombras":"Daqui partiu a ordem que destruiu os Reis-Dragão.",
    "Costa dos Náufragos":"Figuras vasculham destroços em busca do que não pode ser encontrado.",
    "Pântano de Morgraen":"Névoa permanente. Criaturas sussurram seu nome verdadeiro.",
    "Planície Dourada":"Campos que alimentavam o reino. Metade queimada pela guerra.",
    "Ironhold":"A Cidade de Ferro. Neutros — mas nem todos são o que parecem.",
    "Masmorra de Kragdor":"Algo respira nas profundezas. E está desperto há séculos.",
    "Mar do Sul":"Criaturas de outro mundo surfam suas ondas negras e frias.",
    "Floresta Profunda":"As árvores se movem. Os animais têm olhos demais.",
    "Templo Esquecido":"Anterior aos próprios deuses. O idioma nas paredes é indizível.",
    "Vilarejo de Ravenford":"Sabem de algo que se recusam obstinadamente a contar.",
    "Minas de Ferro":"Desceram fundo demais. Voltaram diferentes. Não dormem.",
    "Porto da Perdição":"Perguntas respondidas com facas. Informação tem preço aqui.",
    "Cavernas Abissais":"O silêncio aqui tem peso, textura e dentes.",
    "Floresta Amaldiçoada":"Almas queimadas ainda vagam entre as árvores carbonizadas.",
    "Catedral em Ruínas":"Seres que corrompem tudo o que tocam habitam este lugar.",
    "Mercado Negro":"Tudo à venda — memórias, almas, segredos de reis mortos.",
    "Litoral Proibido":"Além daqui, nenhum mapa existe. Apenas o fim do mundo conhecido.",
}
MONSTERS = {
    "Tundra Glacial":        [("Wendigo das Neves",35,28,18,0.40),("Lobo-Fantasma",25,20,12,0.35)],
    "Pico de Frostmourne":   [("Grifo das Alturas",50,38,22,0.40),("Troll de Gelo",60,30,25,0.35)],
    "Torre do Oráculo":      [("Golem do Oráculo",55,35,28,0.35),("Espectro Vidente",30,42,20,0.40)],
    "Mar Cinzento":          [("Leviatã Sombrio",70,45,30,0.30),("Sereia das Profundezas",40,38,22,0.40)],
    "Ilhas do Exílio":       [],
    "Floresta de Mirewood":  [("Demônio Florestal",30,22,12,0.45),("Goblin Arqueiro",20,25,8,0.50)],
    "Aldeia de Ashenvale":   [("Bandido da Estrada",22,18,8,0.20)],
    "Ruínas de Vel'Moran":   [("Cavaleiro Espectral",45,35,20,0.45),("Lich Menor",35,42,18,0.40)],
    "Fortaleza das Sombras": [("Soldado das Trevas",55,40,25,0.50),("Cultista Corrompido",40,45,20,0.45)],
    "Costa dos Náufragos":   [("Mercenário",28,20,10,0.35),("Morto-Vivo Marinho",32,22,12,0.40)],
    "Pântano de Morgraen":   [("Treant Corrompido",40,25,18,0.45),("Víbora Pantanosa",25,30,10,0.50)],
    "Planície Dourada":      [("Salteador",25,20,10,0.40),("Javali Feroz",30,22,12,0.35)],
    "Ironhold":              [],
    "Masmorra de Kragdor":   [("Ogro das Cavernas",65,38,28,0.40),("Mineiro Corrompido",40,30,18,0.45)],
    "Mar do Sul":            [("Tubarão-Fantasma",45,35,20,0.35)],
    "Floresta Profunda":     [("Aranha-Demoníaca",35,32,15,0.45),("Espírito da Floresta",28,38,12,0.40)],
    "Templo Esquecido":      [("Guardião de Pedra",50,30,22,0.40),("Cultista Antigo",30,35,16,0.45)],
    "Vilarejo de Ravenford": [("Zumbi Errante",28,18,10,0.25),("Bandido Noturno",25,22,10,0.20)],
    "Minas de Ferro":        [("Golem de Ferro",60,32,28,0.40),("Mineiro Possuído",35,28,15,0.45)],
    "Porto da Perdição":     [("Pirata Renegado",30,25,12,0.25),("Assassino de Aluguel",25,35,14,0.30)],
    "Cavernas Abissais":     [("Basilisco das Trevas",55,40,25,0.45),("Morcego Colossal",35,30,16,0.50)],
    "Floresta Amaldiçoada":  [("Banshee",38,45,20,0.45),("Lobo Amaldiçoado",30,28,14,0.50)],
    "Catedral em Ruínas":    [("Vampiro Nobre",50,42,22,0.45),("Servo das Trevas",35,30,16,0.40)],
    "Mercado Negro":         [],
    "Litoral Proibido":      [("Kraken Juvenil",70,45,32,0.35),("Sereia Cruel",40,40,20,0.40)],
}

# ══════════════════════════════════════════════════════════════════════════════
#  BOSSES — MULTI-FASE
# ══════════════════════════════════════════════════════════════════════════════
BOSSES = {
    "Ruínas de Vel'Moran": {
        "nome":"Vel'Krath, o Não-Morto","emoji":"💀","xp":80,"gold_range":(20,40),
        "phases":[
            {"hp":120,"atk":45,"desc":"_'Você ousa profanar estas ruínas?'_ Vel'Krath ergue sua espada espectral."},
            {"hp":80, "atk":65,"desc":"💀 **FASE 2 — Forma Ascendida!** Vel'Krath absorve a energia das ruínas. Seu corpo se reconstrói em sombra pura!"},
        ],
        "relic":{"id":"espirito_velmoran","nome":"Espírito de Vel'Moran","emoji":"👻","effect":"Imune a 1 morte por sessão","passive":"death_immunity"},
    },
    "Fortaleza das Sombras": {
        "nome":"Lord Malachar, das Trevas","emoji":"🧟","xp":150,"gold_range":(35,60),
        "phases":[
            {"hp":200,"atk":60,"desc":"_'A profecia termina aqui, Escolhido.'_ Malachar invoca a Armadura das Trevas."},
            {"hp":120,"atk":80,"desc":"🧟 **FASE 2 — Ritual de Sangue!** Malachar sacrifica seus soldados para se regenerar!"},
            {"hp":60, "atk":100,"desc":"🔥 **FASE 3 — FORMA FINAL!** _'EU SOU O PACTO!'_ Malachar funde-se com a própria escuridão!"},
        ],
        "relic":{"id":"coroa_malachar","nome":"Coroa de Malachar","emoji":"👑","effect":"+20 ATK permanente","passive":"atk_flat_20"},
    },
    "Masmorra de Kragdor": {
        "nome":"Drakar, o Dragão Ancião","emoji":"🐉","xp":150,"gold_range":(40,70),
        "phases":[
            {"hp":200,"atk":55,"desc":"🐉 Drakar abre os olhos pela primeira vez em mil anos. O chão derrete sob suas garras."},
            {"hp":120,"atk":70,"desc":"🔥 **FASE 2 — Fúria Dracônica!** Drakar ergue voo. Chamas cobrem o teto inteiro da caverna!"},
            {"hp":60, "atk":90,"desc":"💎 **FASE 3 — Sangue Ancião!** _'Você merece morrer de pé.'_ Drakar usa toda sua magia ancestral!"},
        ],
        "relic":{"id":"escama_drakar","nome":"Escama de Drakar","emoji":"🐉","effect":"Montaria Dracônica desbloqueada + +12 ATK","passive":"dragon_rider"},
        "post_kill_unlock":"dragon_mount",
    },
    "Ilhas do Exílio": {
        "nome":"Xal'thar, o Deus Esquecido","emoji":"👁️","xp":300,"gold_range":(60,100),
        "phases":[
            {"hp":300,"atk":80,"desc":"👁️ _'Eu esperei mil anos. Você não é o primeiro Escolhido. E não será o último.'_ Xal'thar abre seu olho primordial."},
            {"hp":200,"atk":100,"desc":"🌀 **FASE 2 — Distorção da Realidade!** O mundo ao redor se dobra. Xal'thar existe em múltiplos planos simultaneamente!"},
            {"hp":100,"atk":120,"desc":"🌑 **FASE 3 — ANIQUILAÇÃO!** _'ENTÃO VOCÊ É O FIM DA MINHA ESPERA!'_ Xal'thar concentra mil anos de poder em um único ataque!"},
        ],
        "relic":{"id":"olho_xalthar","nome":"Olho de Xal'thar","emoji":"👁️","effect":"+30% XP de todos os inimigos","passive":"xp_boost_30"},
    },
}

# ══════════════════════════════════════════════════════════════════════════════
#  WORLD BOSSES (RAIDS COOPERATIVAS)
# ══════════════════════════════════════════════════════════════════════════════
WORLD_BOSSES = {
    "Tita de Gelo": {
        "nome": "Titã de Gelo Ancestral",
        "emoji": "🥶",
        "base_hp": 1000,
        "hp_per_level": 200,
        "base_atk": 40,
        "desc": "🥶 **[RAID]** O Titã despertou. Ele esmaga tudo em seu caminho! (Dano Base: 40)",
        "xp_pool": 500,
        "gold_pool": 200
    },
    "Destruidor de Mundos": {
        "nome": "Azazel, O Destruidor",
        "emoji": "🌋",
        "base_hp": 2500,
        "hp_per_level": 300,
        "base_atk": 65,
        "desc": "🌋 **[RAID]** A terra se abre. Azazel emergiu do núcleo para queimar Aethoria! (Dano Base: 65)",
        "xp_pool": 1200,
        "gold_pool": 500
    },
    "Drakon Fantasma": {
        "nome": "Drakon, O Dragão Fantasma",
        "emoji": "👻",
        "base_hp": 1500,
        "hp_per_level": 250,
        "base_atk": 50,
        "desc": "👻 **[RAID]** O espectro de um Rei-Dragão se materializou! Seus ataques atravessam armaduras. (Dano Base: 50)",
        "xp_pool": 800,
        "gold_pool": 350
    },
    "Kraken Abissal": {
        "nome": "Thal'Zuun, O Kraken Abissal",
        "emoji": "🦑",
        "base_hp": 2000,
        "hp_per_level": 280,
        "base_atk": 55,
        "desc": "🦑 **[RAID]** Das profundezas do Mar Fragmentado, tentáculos colossais emergem! (Dano Base: 55)",
        "xp_pool": 1000,
        "gold_pool": 400
    },
    "Guardiao Corrompido": {
        "nome": "Ygdra, Guardiã Corrompida",
        "emoji": "🌿",
        "base_hp": 1800,
        "hp_per_level": 220,
        "base_atk": 45,
        "desc": "🌿 **[RAID]** A antiga protetora da floresta foi consumida pelas Sombras! (Dano Base: 45)",
        "xp_pool": 900,
        "gold_pool": 380
    }
}

BOSS_SLUGS = {
    "tita_de_gelo": "Tita de Gelo",
    "destruidor_de_mundos": "Destruidor de Mundos",
    "drakon_fantasma": "Drakon Fantasma",
    "kraken_abissal": "Kraken Abissal",
    "guardiao_corrompido": "Guardiao Corrompido",
}

# ══════════════════════════════════════════════════════════════════════════════
#  CLASSES & SKILL TREES
# ══════════════════════════════════════════════════════════════════════════════
CLASSES = {
    "guerreiro":{"nome":"Guerreiro","emoji":"⚔️","hp":130,"mana":40,"atk":(12,22),"def":10,
                 "skill":"Investida Furiosa","skill_e":"💥","skill_cost":20,"skill_multi":2.0,
                 "weapon":"Espada de Aço","armor":"Cota de Malha",
                 "lore":"Forjado na guerra. Resistente como o aço de Ironhold."},
    "mago":     {"nome":"Mago","emoji":"🔮","hp":85,"mana":100,"atk":(8,16),"def":4,
                 "skill":"Tempestade Arcana","skill_e":"⚡","skill_cost":30,"skill_multi":3.0,
                 "weapon":"Cetro do Wyrd","armor":"Manto Rúnico",
                 "lore":"Portador de magia proibida desde a queda dos Reis-Dragão."},
    "cacador":  {"nome":"Caçador","emoji":"🏹","hp":105,"mana":60,"atk":(10,20),"def":7,
                 "skill":"Tiro de Precisão","skill_e":"🎯","skill_cost":25,"skill_multi":2.2,
                 "weapon":"Arco de Teixo Élfio","armor":"Couro Endurecido",
                 "lore":"Solitário como os Witchers do norte. Caça o que outros temem."},
    "ladino":   {"nome":"Ladino","emoji":"🗡️","hp":95,"mana":70,"atk":(14,26),"def":5,
                 "skill":"Golpe Furtivo","skill_e":"🌑","skill_cost":20,"skill_multi":2.0,
                 "weapon":"Adagas Gêmeas","armor":"Roupa das Sombras",
                 "lore":"Das sombras do Mercado Negro. Sabe o que reis pagam fortunas para ocultar."},
    "paladino": {"nome":"Paladino","emoji":"🛡️","hp":140,"mana":70,"atk":(10,18),"def":12,
                 "skill":"Julgamento Divino","skill_e":"✨","skill_cost":25,"skill_multi":1.8,
                 "weapon":"Martelo da Luz","armor":"Placas Abençoadas",
                 "lore":"Guerreiros sagrados jurados à Ordem. Onde há trevas, eles trazem a luz."},
    "necromante":{"nome":"Necromante","emoji":"💀","hp":85,"mana":120,"atk":(9,15),"def":4,
                 "skill":"Exército de Ossos","skill_e":"🦴","skill_cost":35,"skill_multi":2.5,
                 "weapon":"Foice das Almas","armor":"Manto de Ossos",
                 "lore":"A morte não é o fim, mas apenas uma nova ferramenta no seu arsenal."},
    "bardo":    {"nome":"Bardo","emoji":"🎵","hp":95,"mana":85,"atk":(9,17),"def":6,
                 "skill":"Canção do Caos","skill_e":"🎶","skill_cost":20,"skill_multi":2.0,
                 "weapon":"Alaúde Encantado","armor":"Trajes Festivos",
                 "lore":"Tecelões da música e do destino. Uma canção certa muda o mundo."},
}
SKILL_TREES = {
    "guerreiro":[
        ("gf1","Lâmina Afiada",     "⚔️ Força",   1,1,None,  "+6 ATK base",                      {"atk_flat":6}),
        ("gf2","Golpe Devastador",  "⚔️ Força",   2,2,"gf1", "+14 ATK · Crítico +12%",            {"atk_flat":14,"crit":0.12}),
        ("gd1","Escudo de Ferro",   "🛡️ Defesa",  1,1,None,  "+8 DEF",                            {"def_flat":8}),
        ("gd2","Muralha Viva",      "🛡️ Defesa",  2,2,"gd1", "+15 DEF · +35 HP máx",             {"def_flat":15,"hp_max":35}),
        ("gv1","Sede de Sangue",    "🔥 Fúria",   1,1,None,  "Ao matar: próx. ataque +20%",       {"kill_fury":0.20}),
        ("gv2","Berserker",         "🔥 Fúria",   2,2,"gv1", "HP<30% → +80% ATK",                {"low_hp_bonus":0.80}),
    ],
    "mago":[
        ("mf1","Chama Arcana",      "🔥 Fogo",    1,1,None,  "+8 dano mágico",                    {"atk_flat":8}),
        ("mf2","Pilar de Fogo",     "🔥 Fogo",    2,2,"mf1", "+18 ATK · Queima 6/turno",          {"atk_flat":18,"burn":6}),
        ("mg1","Armadura de Gelo",  "❄️ Gelo",    1,1,None,  "+7 DEF arcana",                     {"def_flat":7}),
        ("mg2","Cristal de Inverno","❄️ Gelo",    2,2,"mg1", "+12 DEF · Atordoa 30%",             {"def_flat":12,"stun":0.30}),
        ("mt1","Canalização",       "⚡ Trovão",  1,1,None,  "+30 Mana máx",                      {"mana_max":30}),
        ("mt2","Relâmpago Duplo",   "⚡ Trovão",  2,2,"mt1", "Habilidade custa -15 mana",         {"skill_cost_off":15}),
    ],
    "cacador":[
        ("cp1","Olho de Águia",     "🎯 Precisão",1,1,None,  "Crítico +22%",                      {"crit":0.22}),
        ("cp2","Tiro Fatal",        "🎯 Precisão",2,2,"cp1", "Tiro de Precisão = 3× dano",        {"precision_multi":3.0}),
        ("cs1","Pele Dura",         "🌿 Sobrev.", 1,1,None,  "+28 HP máx",                        {"hp_max":28}),
        ("cs2","Regeneração",       "🌿 Sobrev.", 2,2,"cs1", "+6 HP por turno vivo",              {"regen":6}),
        ("cb1","Vínculo Animal",    "🐺 Bestas",  1,1,None,  "Companheiro +10 ATK",               {"companion_atk":10}),
        ("cb2","Chamado da Matilha","🐺 Bestas",  2,2,"cb1", "35% de ataque duplo",               {"double_atk":0.35}),
    ],
    "ladino":[
        ("ls1","Passo Silencioso",  "🌑 Sombras", 1,1,None,  "Fuga sempre funciona",              {"free_escape":True}),
        ("ls2","Assassino",         "🌑 Sombras", 2,2,"ls1", "1º ataque do combate = Crítico 2×", {"first_strike":True}),
        ("lv1","Lâmina Envenenada", "🐍 Veneno",  1,1,None,  "35% de envenenar (8 dmg/turno)",    {"poison_chance":0.35}),
        ("lv2","Nuvem Tóxica",      "🐍 Veneno",  2,2,"lv1", "Veneno reduz ATK inimigo -20%",     {"poison_debuff":0.20}),
        ("la1","Reflexos Felinos",  "💨 Agilidade",1,1,None, "Esquiva 18%",                       {"dodge":0.18}),
        ("la2","Dança das Lâminas", "💨 Agilidade",2,2,"la1","Ataque duplo sempre ativo",         {"always_double":True}),
    ],
    "paladino":[
        ("paf1","Arma Sagrada",     "✨ Divino",  1,1,None,  "+8 ATK",                            {"atk_flat":8}),
        ("paf2","Golpe Purificador","✨ Divino",  2,2,"paf1", "+14 ATK · Crítico +15%",           {"atk_flat":14,"crit":0.15}),
        ("pad1","Aura de Devoção",  "🛡️ Proteção",1,1,None,  "+10 DEF",                           {"def_flat":10}),
        ("pad2","Bastião da Luz",   "🛡️ Proteção",2,2,"pad1", "+15 DEF · +40 HP máx",            {"def_flat":15,"hp_max":40}),
        ("pas1","Fé Inabalável",    "🌟 Fé",      1,1,None,  "+35 Mana máx",                      {"mana_max":35}),
        ("pas2","Cura Divina",      "🌟 Fé",      2,2,"pas1", "+8 HP por turno vivo",             {"regen":8}),
    ],
    "necromante":[
        ("nf1","Toque da Morte",    "💀 Decadência",1,1,None, "+9 ATK",                           {"atk_flat":9}),
        ("nf2","Ceifador de Almas", "💀 Decadência",2,2,"nf1","+18 ATK · Ao matar: próx. atk +25%",{"atk_flat":18,"kill_fury":0.25}),
        ("ns1","Escudo de Ossos",   "🦴 Ossos",   1,1,None,   "+8 DEF",                           {"def_flat":8}),
        ("ns2","Prisão Óssea",      "🦴 Ossos",   2,2,"ns1",  "+12 DEF · Atordoa 30%",            {"def_flat":12,"stun":0.30}),
        ("nm1","Pacto Sombrio",     "🩸 Magia",   1,1,None,   "+40 Mana máx",                     {"mana_max":40}),
        ("nm2","Lorde Lich",        "🩸 Magia",   2,2,"nm1",  "HP<30% → +85% ATK",               {"low_hp_bonus":0.85}),
    ],
    "bardo":[
        ("bf1","Acorde Dissonante", "🎵 Som",     1,1,None,   "+7 ATK base",                      {"atk_flat":7}),
        ("bf2","Sinfonia da Ruína", "🎵 Som",     2,2,"bf1",  "+12 ATK · Crítico +15%",           {"atk_flat":12,"crit":0.15}),
        ("bs1","Inspiração",        "✨ Charme",  1,1,None,   "Esquiva 18%",                      {"dodge":0.18}),
        ("bs2","Dança Festiva",     "✨ Charme",  2,2,"bs1",  "Fuga sempre funciona",             {"free_escape":True}),
        ("bg1","Canto de Cura",     "💚 Melodia", 1,1,None,   "+6 HP por turno vivo",             {"regen":6}),
        ("bg2","Bis",               "💚 Melodia", 2,2,"bg1",  "30% de ataque duplo",              {"double_atk":0.30}),
    ],
}
XP_TABLE = [0,0,60,150,280,450,680,980,1360,1840,2500]

# ══════════════════════════════════════════════════════════════════════════════
#  SHOP — prices affected by faction rep
# ══════════════════════════════════════════════════════════════════════════════
SHOP_BASE = {
    "pocao_menor":  {"nome":"Poção Menor",   "emoji":"🧪","heal":30, "price":8},
    "pocao":        {"nome":"Poção Grande",  "emoji":"💊","heal":65, "price":15},
    "elixir_mana":  {"nome":"Elixir de Mana","emoji":"💙","mana":45, "price":12},
    "antidoto":     {"nome":"Antídoto",      "emoji":"🌿","cure_poison":True,"price":10},
}

# ══════════════════════════════════════════════════════════════════════════════
#  CRAFTING RECIPES
# ══════════════════════════════════════════════════════════════════════════════
RECIPES = {
    "pocao_maior":{"nome":"Poção Superior","emoji":"🔴","requires":{"pocao_menor":3},"result":{"heal":120},"type":"consumable"},
    "elixir_wyrd": {"nome":"Elixir de Wyrd","emoji":"✨","requires":{"pocao_menor":1,"mana_elixirs":1},"result":{"heal":40,"mana":40},"type":"consumable"},
    "po_reliquias": {"nome":"Pó de Relíquias","emoji":"💠","requires_relic":2,"result":{"xp":200},"type":"special"},
}

# ══════════════════════════════════════════════════════════════════════════════
#  WORLD EVENTS (rotacionam a cada 15 turnos)
# ══════════════════════════════════════════════════════════════════════════════
WORLD_EVENTS = [
    {"nome":"Lua de Sangue","emoji":"🌑","desc":"A Lua de Sangue banha Aethoria. Monstros emergem mais fortes e frequentes.",
     "monster_hp_mult":1.25,"encounter_rate_bonus":0.15,"xp_mult":1.3,"price_mult":1.0},
    {"nome":"Festival de Ironhold","emoji":"🎉","desc":"Ironhold celebra o Dia da Fundação. Preços reduzidos e XP em alta!",
     "monster_hp_mult":1.0,"encounter_rate_bonus":-0.1,"xp_mult":1.5,"price_mult":0.7},
    {"nome":"Névoa do Esquecimento","emoji":"🌫️","desc":"Uma névoa arcana cobre Aethoria. Monstros ficam confusos — mais fracos.",
     "monster_hp_mult":0.75,"encounter_rate_bonus":0.0,"xp_mult":1.1,"price_mult":1.0},
    {"nome":"Invasão do Pacto","emoji":"⚔️","desc":"O Pacto das Sombras ataca rotas comerciais. Preços sobem em todo o reino.",
     "monster_hp_mult":1.15,"encounter_rate_bonus":0.10,"xp_mult":1.2,"price_mult":1.4},
    {"nome":"Primavera de Mirewood","emoji":"🌸","desc":"Flores mágicas de Mirewood curam os aventureiros. Descanso é mais eficiente.",
     "monster_hp_mult":0.9,"encounter_rate_bonus":-0.05,"xp_mult":1.0,"price_mult":1.0},
    {"nome":"Tormenta Arcana","emoji":"🌩️","desc":"Energia mágica instável amplifica todos os poderes mágicos.",
     "monster_hp_mult":1.1,"encounter_rate_bonus":0.05,"xp_mult":1.4,"price_mult":1.1},
    {"nome":"Paz Relativa","emoji":"☮️","desc":"Uma trégua temporária acalma Aethoria. Exploradores viajam com mais segurança.",
     "monster_hp_mult":0.8,"encounter_rate_bonus":-0.2,"xp_mult":0.9,"price_mult":0.9},
]

# ══════════════════════════════════════════════════════════════════════════════
#  TAVERN RUMORS (por zona segura)
# ══════════════════════════════════════════════════════════════════════════════
TAVERN_RUMORS = {
    "Ironhold":[
        ("🍺 O taverneiro cochila: _'Drakar acordou há um mês. Ninguém que entrou em Kragdor voltou para contar.'_","xp",8),
        ("🍺 _'Dizem que Malachar foi traído por seu próprio irmão. E que esse irmão ainda vive... aqui em Ironhold.'_","xp",10),
        ("🍺 Um bêbado grita: _'A Torre do Oráculo não é de pedra! É feita dos ossos dos primeiros Reis-Dragão!'_","xp",5),
        ("🍺 Um mercador suspeito oferece: _'Informação sobre Xal'thar: ele teme o som de sinos. +15 ATK contra ele na próxima batalha.'_","atk_bonus_boss",15),
    ],
    "Aldeia de Ashenvale":[
        ("🌿 Miriel murmura: _'A profecia tem quatro linhas. Só três foram traduzidas. A quarta... ninguém sobreviveu para lê-la.'_","xp",12),
        ("🌿 Uma criança aponta para o norte: _'A Tundra Glacial esconde um dragão diferente. Nem inimigo, nem aliado.'_","xp",8),
        ("🌿 _'Lyra era estudante de Miriel antes de se tornar guerreira. Ela sabe algo sobre a sua tatuagem que ainda não contou.'_","xp",10),
    ],
    "Porto da Perdição":[
        ("⚓ Capitão Heron: _'Fui às Ilhas uma vez. Xal'thar não ataca imediatamente. Ele OBSERVA. Isso é mais aterrorizante.'_","xp",10),
        ("⚓ Uma piratas ri: _'O Mercado Negro vende mapas falsos das Ilhas do Exílio. Os verdadeiros estão na Torre do Oráculo.'_","xp",8),
        ("⚓ _'Há um tesouro enterrado nas Cavernas Abissais. Três aventureiros morreram tentando. O quarto ficou lá.'_","gold",15),
    ],
    "Mercado Negro":[
        ("🕵️ Uma voz encapuzada: _'Malachar não é humano há quarenta anos. O que habita aquele corpo é muito mais antigo.'_","xp",12),
        ("🕵️ _'Vel'Krath foi o general mais leal dos Reis-Dragão antes da traição. Alguém o corrompeu primeiro.'_","xp",10),
        ("🕵️ Uma figura oferece: _'Por 20 ouros, a localização de um baú escondido em Vel'Moran.'_ _(você recusa — mas anota mentalmente)_","xp",6),
    ],
    "Vilarejo de Ravenford":[
        ("🏡 Um fazendeiro: _'O rio mudou de direção há três noites. Corre para Kragdor agora. Isso nunca aconteceu antes.'_","xp",6),
        ("🏡 _'Minha avó dizia que a Floresta Amaldiçoada era uma cidade antes. Com um milhão de habitantes. Em uma noite, sumiu.'_","xp",8),
        ("🏡 Uma criança te dá uma flor estranha. _Você sente que ela é importante, mas não sabe por quê._ +12 XP","xp",12),
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  CONQUISTAS
# ══════════════════════════════════════════════════════════════════════════════
CONQUISTAS = [
    ("primeiro_sangue",   "🩸 Primeiro Sangue",     "Primeiro inimigo derrotado",              lambda p:p["kills"]>=1),
    ("caçador_10",        "🗡️ Caçador",              "10 inimigos derrotados",                  lambda p:p["kills"]>=10),
    ("caçador_50",        "⚔️ Veterano de Batalha",  "50 inimigos derrotados",                  lambda p:p["kills"]>=50),
    ("caçador_100",       "💀 Lenda do Campo",       "100 inimigos derrotados",                 lambda p:p["kills"]>=100),
    ("primeiro_chefao",   "👑 Caçador de Chefões",   "Primeiro chefão derrotado",               lambda p:len(p.get("bosses_defeated",{}))>=1),
    ("todos_chefoes",     "🌟 Lenda de Aethoria",    "Todos os 4 chefões derrotados",           lambda p:len(p.get("bosses_defeated",{}))>=4),
    ("explorador",        "🗺️ Explorador",            "15 locais diferentes visitados",          lambda p:len(p.get("visited",[]))>=15),
    ("cartografo",        "📜 Cartógrafo",            "Todos os 25 locais visitados",            lambda p:len(p.get("visited",[]))>=25),
    ("nivel_5",           "⭐ Aventureiro",           "Atingiu nível 5",                         lambda p:p["level"]>=5),
    ("nivel_10",          "💎 Lendário",              "Nível 10 — o máximo!",                    lambda p:p["level"]>=10),
    ("mestre_skills",     "✨ Mestre das Artes",      "4 habilidades desbloqueadas",             lambda p:len(p.get("skills_unlocked",[]))>=4),
    ("rico",              "💰 Barão do Ouro",         "200 ouros acumulados",                    lambda p:p["gold"]>=200),
    ("prestige",          "🔮 Transcendente",         "Prestígio atingido — além do nível 10",   lambda p:p.get("prestige_count",0)>=1),
    ("dragonrider",       "🐉 Cavaleiro Dracônico",   "Montaria dracônica desbloqueada",         lambda p:p.get("dragon_mount",False)),
    ("ressurreto_3",      "💀 Que Não Morre",         "Morreu e voltou 3 vezes",                 lambda p:p.get("deaths",0)>=3),
    ("artesao",           "🔨 Artesão",               "Primeiro item fabricado via crafting",    lambda p:p.get("crafted_count",0)>=1),
    ("gladiador",         "🥊 Gladiador",             "Venceu um desafio PvP",                   lambda p:p.get("pvp_wins",0)>=1),
    ("raid_first",        "🔥 Raider",                "Participou da primeira Raid",             lambda p:p.get("raid_count",0)>=1),
    ("raid_mvp",          "🌟 MVP da Raid",           "Foi MVP de uma Raid",                     lambda p:p.get("raid_mvp_count",0)>=1),
    ("raid_veteran",      "⚔️ Veterano de Raids",     "5 raids completadas",                     lambda p:p.get("raid_count",0)>=5),
    ("raid_titan",        "👑 Matador de Titãs",       "Derrotou ambos os World Bosses",          lambda p:len(p.get("raid_bosses_killed",[]))>=len(WORLD_BOSSES)),
]

# GitHub language → class affinity
LANG_CLASS = {
    "Python":"mago","Ruby":"mago","Elixir":"mago","Haskell":"mago","R":"mago","Lua":"mago",
    "C":"guerreiro","C++":"guerreiro","Rust":"guerreiro","Go":"guerreiro","Zig":"guerreiro","Assembly":"guerreiro",
    "Java":"paladino","C#":"paladino","Kotlin":"paladino","Swift":"paladino","TypeScript":"cacador","Scala":"cacador","Dart":"cacador",
    "JavaScript":"ladino","PHP":"ladino","Shell":"ladino","Perl":"ladino","HTML":"bardo","CSS":"bardo",
    "SQL":"necromante","GDScript":"bardo","Clojure":"necromante",
}

# ══════════════════════════════════════════════════════════════════════════════
#  I/O LAYER
# ══════════════════════════════════════════════════════════════════════════════
def _rw(path, data=None):
    p = Path(path)
    if data is None:
        return json.loads(p.read_text("utf-8")) if p.exists() else None
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")

def load_gs():
    s = _rw("rpg/state.json")
    if not s:
        s = {"turn":0,"world_log":[],"npc_memory":{},"world_events":[]}
    s.setdefault("world_log",[]); s.setdefault("npc_memory",{})
    return s

def save_gs(s): _rw("rpg/state.json", s)

def load_player(u):
    p = _rw(f"rpg/players/{u}.json")
    if p: p.pop("_new", None); return p
    return {
        "_new":True,"username":u,"github_profile":None,"profile_bonuses":{},
        "hp":0,"max_hp":0,"mana":0,"max_mana":0,
        "xp":0,"total_xp":0,"level":1,"gold":10,"potions":3,
        "kills":0,"deaths":0,"classe":None,"defense":5,"titulo":None,
        "position":{"x":2,"y":2},
        "inventory":[],"equipment":{"weapon":"Punhos","armor":"Roupa Simples"},
        "skills_unlocked":[],"skill_points":0,
        "quests":[
            {"id":"q1","titulo":"A Chama de Ashenvale","objetivo":"Visite Aldeia de Ashenvale","concluida":False,"xp":30,"gold":15},
            {"id":"q2","titulo":"O Segredo de Vel'Moran","objetivo":"Derrote Vel'Krath","concluida":False,"xp":80,"gold":0},
            {"id":"q3","titulo":"O Coração das Trevas","objetivo":"Derrote Lord Malachar","concluida":False,"xp":150,"gold":0},
            {"id":"q4","titulo":"O Dragão Ancião","objetivo":"Derrote Drakar em Kragdor","concluida":False,"xp":150,"gold":0},
            {"id":"q5","titulo":"O Deus Esquecido","objetivo":"Derrote Xal'thar nas Ilhas do Exílio","concluida":False,"xp":300,"gold":0},
        ],
        "bosses_defeated":{},"relics":[],"companion":None,
        "visited":["Ironhold"],"conquistas":[],"sessions":0,
        "log":["⚔️ Bem-vindo a Aethoria!","_Uma tatuagem arcana pulsa em seu pulso._","🧙 Escolha sua classe para começar!"],
        "active_monster":None,"boss_phase":0,"poison_stacks":0,"fury_bonus":False,
        "dragon_mount":False,"prestige_count":0,"crafted_count":0,"pvp_wins":0,
        "raid_count":0,"raid_mvp_count":0,"raid_bosses_killed":[],
        "last_played":datetime.now(timezone.utc).isoformat(),
    }

def save_player(p): _rw(f"rpg/players/{p['username']}.json", p)

def load_raids():
    r = _rw("rpg/raids.json")
    if not r:
        r = {}
    return r

def save_raids(r): _rw("rpg/raids.json", r)

def _cleanup_raids():
    """Remove defeated raids older than 24 hours."""
    raids = load_raids()
    now = datetime.now(timezone.utc)
    stale = [k for k, r in raids.items()
             if r.get("status") == "defeated" and r.get("defeated_at")
             and (now - datetime.fromisoformat(r["defeated_at"])).total_seconds() > 86400]
    for k in stale:
        del raids[k]
    if stale:
        save_raids(raids)

def load_lb():
    lb = _rw("rpg/leaderboard.json")
    return lb or {"players":[],"updated":""}
def save_lb(lb): _rw("rpg/leaderboard.json", lb)

# ══════════════════════════════════════════════════════════════════════════════
#  GITHUB API
# ══════════════════════════════════════════════════════════════════════════════
def gh_get(ep, tok=None):
    h = {"Accept":"application/vnd.github.v3+json","User-Agent":"Aethoria-RPG/3.0"}
    if tok: h["Authorization"]=f"token {tok}"
    try:
        with urlopen(Request(f"https://api.github.com{ep}",headers=h), timeout=8) as r:
            return json.loads(r.read().decode())
    except Exception: return None

def fetch_profile(u, tok=None):
    user=gh_get(f"/users/{u}",tok)
    if not user or "login" not in user: return None
    repos=gh_get(f"/users/{u}/repos?per_page=100&sort=updated",tok) or []
    langs,stars={},0
    for r in repos:
        stars+=r.get("stargazers_count",0)
        if r.get("language"): langs[r["language"]]=langs.get(r["language"],0)+1
    return {
        "login":u,"name":user.get("name") or u,"followers":user.get("followers",0),
        "public_repos":user.get("public_repos",0),"total_stars":stars,
        "top_language":max(langs,key=langs.get) if langs else None,
        "account_age":datetime.now().year-int(user.get("created_at","2020")[:4]),
        "bio":(user.get("bio") or "")[:80],"fetched_at":datetime.now(timezone.utc).isoformat(),
    }

def apply_profile_bonuses(profile, p):
    if not profile: return []
    msgs=[]; stars=profile.get("total_stars",0); followers=profile.get("followers",0)
    repos=profile.get("public_repos",0); age=profile.get("account_age",0); lang=profile.get("top_language")
    g=min(80,stars//3);
    if g: p["gold"]+=g; msgs.append(f"⭐ {stars} stars → **+{g} ouro** inicial!")
    x=min(80,followers//2)
    if x: p["xp"]+=x; p["total_xp"]+=x; msgs.append(f"👥 {followers} seguidores → **+{x} XP** inicial!")
    if lang and lang in LANG_CLASS:
        msgs.append(f"💻 Linguagem principal **{lang}** → afinidade com **{CLASSES[LANG_CLASS[lang]]['nome']}** _(bônus ao escolher esta classe!)_")
    if age>=7: msgs.append(f"🎖️ Conta com **{age} anos** → título _Veterano do Código_ disponível!")
    if repos>=15: p["potions"]+=2; msgs.append(f"📦 {repos} repos → **+2 poções** de boas-vindas!")
    return msgs

# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _normalize(s):
    """Remove accents and lowercase for safe comparison."""
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()

def terrain(p): return WORLD_MAP[p["position"]["y"]][p["position"]["x"]]
def cls(p): return CLASSES.get(p.get("classe",""),None)

def sb(p):
    """Aggregate skill tree passive bonuses."""
    b={"atk_flat":0,"def_flat":0,"hp_max":0,"mana_max":30,"crit":0.0,"dodge":0.0,
       "companion_atk":0,"kill_fury":0.0,"low_hp_bonus":0.0,"burn":0,
       "stun":0.0,"poison_chance":0.0,"poison_debuff":0.0,"skill_cost_off":0,
       "regen":0,"precision_multi":0.0,"double_atk":0.0,"always_double":False,
       "free_escape":False,"first_strike":False}
    unlocked=set(p.get("skills_unlocked",[]))
    for sk in SKILL_TREES.get(p.get("classe",""),[]):
        if sk[0] not in unlocked: continue
        for k,v in sk[7].items():
            cur=b.get(k,0)
            if isinstance(cur,bool) or v is True: b[k]=True
            elif isinstance(cur,float): b[k]=cur+(float(v) if not isinstance(v,bool) else 0)
            elif isinstance(cur,int): b[k]=cur+(int(v) if not isinstance(v,bool) else 0)
    # Relic passives
    for rel in p.get("relics",[]):
        pas=rel.get("passive","")
        if pas=="atk_flat_20": b["atk_flat"]+=20
        elif pas=="xp_boost_30": b["_xp_boost"]=1.30
    return b

def atk_dmg(p, bonuses=None):
    c=cls(p); sk=sb(p)
    lo,hi=c["atk"] if c else (8,15)
    lvl=p["level"]; flat=sk["atk_flat"]; dmg=random.randint(lo+lvl*2+flat,hi+lvl*2+flat)
    if sk["low_hp_bonus"]>0 and p["hp"]/max(1,p["max_hp"])<0.30: dmg=int(dmg*(1+sk["low_hp_bonus"]))
    if p.get("fury_bonus"): dmg=int(dmg*(1+sk["kill_fury"])); p["fury_bonus"]=False
    if sk["crit"]>0 and random.random()<sk["crit"]: dmg=int(dmg*1.80)
    if bonuses and bonuses.get("monster_hp_mult",1)>1.0: dmg=int(dmg*0.95)  # event harder monsters
    
    # Herança (Roguelite)
    legacy = p.get("legacy_stacks", 0)
    if legacy > 0: dmg += legacy * 2
    
    return dmg

def hp_bar(v,mx,n=10):
    f=round(max(0,v/max(1,mx))*n)
    return f"`[{'█'*f}{'░'*(n-f)}]` {v}/{mx}"

def mp_bar(v,mx):
    f=round(max(0,v/max(1,mx))*8)
    return f"`[{'▓'*f}{'░'*(8-f)}]` {v}/{mx}"

def render_map(p):
    px,py=p["position"]["x"],p["position"]["y"]
    return "\n".join("".join("🧙"if x==px and y==py else MAP_EMOJI.get(t,"❓")for x,t in enumerate(row))for y,row in enumerate(WORLD_MAP))

def dn(gs): return "🌙 Noite" if (gs["turn"]//3)%2 else "☀️ Dia"

def get_event(gs):
    idx=(gs["turn"]//15)%len(WORLD_EVENTS)
    return WORLD_EVENTS[idx]

def push_log(p,msg): p.setdefault("log",[]).insert(0,msg); p["log"]=p["log"][:7]
def push_world(gs,msg): gs.setdefault("world_log",[]).insert(0,msg); gs["world_log"]=gs["world_log"][:8]

def xp_gain(p,xp,sk_bonus=None):
    mult=sk_bonus.get("_xp_boost",1.0) if sk_bonus else 1.0
    final=int(xp*mult); p["xp"]+=final; p["total_xp"]+=final
    return final

def check_lu(p):
    if p["level"]>=10: return ""
    if p["xp"]>=XP_TABLE[p["level"]+1]:
        p["level"]+=1; p["skill_points"]+=1
        sk=sb(p); p["max_hp"]+=18+sk["hp_max"]; p["max_mana"]+=10+sk["mana_max"]
        p["hp"]=p["max_hp"]; p["mana"]=p["max_mana"]
        return f"🌟 **LEVEL UP → {p['level']}!** +1 ponto de habilidade · HP e Mana restaurados!"
    return ""

def check_quests(p,gs,t=None,boss=None):
    for q in p.get("quests",[]):
        if q["concluida"]: continue
        if q["id"]=="q1" and t=="Aldeia de Ashenvale":
            q["concluida"]=True; g=xp_gain(p,q["xp"]); p["gold"]+=q["gold"]
            push_log(p,f"📜 **MISSÃO:** A Chama de Ashenvale ✅ +{g} XP +{q['gold']}g")
            if not p.get("companion"):
                p["companion"]={"nome":"Lyra Moonwhisper","classe":"Arqueira Élfica","emoji":"🧝","atk_bonus":6}
                push_log(p,"🧝 **Lyra Moonwhisper** juntou-se a você! (+6 ATK)")
        if q["id"]=="q2" and boss=="Vel'Krath, o Não-Morto":
            q["concluida"]=True; g=xp_gain(p,q["xp"])
            push_log(p,f"📜 **MISSÃO:** O Segredo de Vel'Moran ✅ +{g} XP")
        if q["id"]=="q3" and boss=="Lord Malachar, das Trevas":
            q["concluida"]=True; g=xp_gain(p,q["xp"]); p["titulo"]="Destruidor das Sombras"
            push_log(p,f"📜 **MISSÃO:** O Coração das Trevas ✅ +{g} XP"); push_log(p,"👑 Título: _Destruidor das Sombras_")
        if q["id"]=="q4" and boss=="Drakar, o Dragão Ancião":
            q["concluida"]=True; g=xp_gain(p,q["xp"])
            push_log(p,f"📜 **MISSÃO:** O Dragão Ancião ✅ +{g} XP")
        if q["id"]=="q5" and boss=="Xal'thar, o Deus Esquecido":
            q["concluida"]=True; g=xp_gain(p,q["xp"])
            push_log(p,f"📜 **MISSÃO:** O Deus Esquecido ✅ +{g} XP · Aethoria está salva... por enquanto.")

def check_conquistas(p,gs):
    for cid,cname,_,check in CONQUISTAS:
        if cid not in p.get("conquistas",[]) and check(p):
            p.setdefault("conquistas",[]).append(cid)
            push_log(p,f"🏆 **CONQUISTA: {cname}**")
            push_world(gs,f"🏆 @{p['username']} conquistou **{cname}**!")

def shop_price(p,base_price,t):
    faction=FACTION_ZONES.get(t)
    if not faction: return base_price
    rep=p.get("factions",{}).get(faction,0)
    if rep>3: return int(base_price*0.80)
    if rep>1: return int(base_price*0.90)
    if rep<-1: return int(base_price*1.20)
    if rep<-3: return int(base_price*1.40)
    return base_price

# ══════════════════════════════════════════════════════════════════════════════
#  COMBAT
# ══════════════════════════════════════════════════════════════════════════════
def monster_hits(p,m):
    sk=sb(p)
    if sk["dodge"]>0 and random.random()<sk["dodge"]:
        push_log(p,f"💨 Você esquivou do ataque de **{m['nome']}**!"); return
    raw=random.randint(max(1,m["atk"]-5),m["atk"]); dmg=max(1,raw-p.get("defense",5))
    p["hp"]=max(0,p["hp"]-dmg); push_log(p,f"🩸 **{m['nome']}**: **-{dmg} HP** (defesa bloqueou {raw-dmg})")
    if p["hp"]<=0: push_log(p,"💀 **Você caiu...** Ironhold te recebe."); death_reset(p)

def death_reset(p):
    c=cls(p); p["hp"]=max(30,(c["hp"]if c else 100)//3); p["mana"]=max(10,p["max_mana"]//2)
    p["position"]={"x":2,"y":2}; p["gold"]=max(0,p["gold"]-12)
    p["active_monster"]=None; p["boss_phase"]=0; p["poison_stacks"]=0
    
    # Sistema de Herança (Roguelite)
    legacy = p.get("legacy_stacks", 0)
    if legacy < 10:
        p["legacy_stacks"] = legacy + 1
        push_log(p, f"🩸 **Herança Sombria**: Sua linhagem fica mais forte com a morte. (+{p['legacy_stacks']*2} ATK base permanente)")
        
    p["deaths"]=p.get("deaths",0)+1; push_log(p,"🏥 Acordou em Ironhold. -12 ouro (curandeiro).")

def resolve_kill(p,m,gs):
    ev=get_event(gs); xp_mult=ev.get("xp_mult",1.0); sk=sb(p)
    xp_base=m.get("xp_reward",20); gold=random.randint(*m.get("gold_range",(2,10)))
    xp_total=int(xp_base*xp_mult); g=xp_gain(p,xp_total,sk)
    p["gold"]+=gold; p["kills"]+=1; p["fury_bonus"]=True
    t=terrain(p); boss_data=BOSSES.get(t,{})
    if m.get("is_boss"):
        p.setdefault("bosses_defeated",{})[t]=True; p["boss_phase"]=0
        push_log(p,f"💀 **[CHEFÃO DERROTADO]** {m['emoji']} {m['nome']}! +{g} XP · +{gold}g")
        push_log(p,"_Esta vitória ecoará pelos corredores da história._")
        push_world(gs,f"⚔️ @{p['username']} derrotou **{m['nome']}** em {t}!")
        # Relic drop
        relic=boss_data.get("relic")
        if relic and not any(r["id"]==relic["id"] for r in p.get("relics",[])):
            p.setdefault("relics",[]).append(relic)
            push_log(p,f"{relic['emoji']} **Relíquia:** {relic['nome']} — _{relic['effect']}_")
        # Dragon mount
        if boss_data.get("post_kill_unlock")=="dragon_mount":
            p["dragon_mount"]=True; push_log(p,"🐉 **Montaria Dracônica desbloqueada!** Use `rpg:montar` para viajar!")
        check_quests(p,gs,boss=m["nome"])
        # Faction update — defeating Sombras bosses increases Ordem rep
        if t in ("Fortaleza das Sombras","Ruínas de Vel'Moran"):
            p.setdefault("factions",{"ordem":0,"circulo":0,"pacto":0}); p["factions"]["ordem"]=min(5,p["factions"].get("ordem",0)+1)
        # Regen from Caçador
        if sk.get("regen",0)>0: p["hp"]=min(p["max_hp"],p["hp"]+sk["regen"])
    else:
        push_log(p,f"💀 **{m['nome']} derrotado!** +{g} XP · +{gold}g")
        if random.random()<0.12: p["potions"]+=1; push_log(p,"🧪 Poção encontrada no corpo!")
        if sk.get("regen",0)>0: p["hp"]=min(p["max_hp"],p["hp"]+sk["regen"])
    p["active_monster"]=None

def action_create_raid(p, gs, boss_slug):
    """Create a new raid by opening a GitHub Issue and initializing raids.json."""
    boss_key = BOSS_SLUGS.get(boss_slug)
    if not boss_key:
        slugs = " · ".join(f"`{s}`" for s in BOSS_SLUGS)
        push_log(p, f"❓ Boss desconhecido: `{boss_slug}`. Disponíveis: {slugs}")
        return
    if not p.get("classe"):
        push_log(p, "⚠️ Escolha uma classe antes de convocar Raids!")
        return
    if p["level"] < 5:
        push_log(p, "⚠️ Você precisa ser nível 5+ para convocar uma Raid!")
        return
    raids = load_raids()
    for iss, r in raids.items():
        if r.get("boss_key") == boss_key and r.get("status") == "active":
            push_log(p, f"⚠️ Já existe uma Raid ativa contra **{WORLD_BOSSES[boss_key]['nome']}**!")
            return
    tok = os.environ.get("GITHUB_TOKEN")
    if not tok:
        push_log(p, "⚠️ Erro: GITHUB_TOKEN ausente."); return
    bd = WORLD_BOSSES[boss_key]
    repo = os.environ.get("GITHUB_REPOSITORY", "xXYoungMoreXx/xXYoungMoreXx")
    issue_body = (f"## {bd['emoji']} RAID: {bd['nome']}\n\n{bd['desc']}\n\n---\n"
                  f"### Como Participar\n1. Comente `/atacar` nesta issue\n"
                  f"2. Cada ataque causa dano baseado no seu nível e classe\n"
                  f"3. O Boss contra-ataca com 60% de chance\n"
                  f"4. MVP (maior dano) ganha +50% de recompensas\n\n"
                  f"| Atributo | Valor |\n|----------|-------|\n"
                  f"| HP Base | {bd['base_hp']} |\n| ATK | {bd['base_atk']} |\n"
                  f"| Scaling | +{bd['hp_per_level']} HP/nível |\n"
                  f"| XP Pool | {bd['xp_pool']} |\n| Gold Pool | {bd['gold_pool']} |\n\n"
                  f"> ⚔️ *Convocado por @{p['username']}*")
    try:
        url = f"https://api.github.com/repos/{repo}/issues"
        data = json.dumps({"title": f"[RAID] {boss_key}", "body": issue_body, "labels": ["rpg-action"]}).encode("utf-8")
        req = Request(url, data=data, headers={"Authorization": f"token {tok}", "Accept": "application/vnd.github.v3+json", "Content-Type": "application/json", "User-Agent": "Aethoria"})
        with urlopen(req) as resp:
            issue_number = str(json.loads(resp.read().decode())["number"])
    except Exception as e:
        push_log(p, f"⚠️ Erro ao criar Issue de Raid: {e}"); return
    raids[issue_number] = {
        "boss_key": boss_key, "hp": bd["base_hp"], "max_hp": bd["base_hp"],
        "status": "active", "participants": {},
        "created_by": p["username"], "created_at": datetime.now(timezone.utc).isoformat()
    }
    save_raids(raids)
    push_log(p, f"{bd['emoji']} **RAID CONVOCADA!** {bd['nome']} aguarda desafiantes! (Issue #{issue_number})")
    push_world(gs, f"{bd['emoji']} @{p['username']} convocou uma **RAID** contra **{bd['nome']}**! Issue #{issue_number}")

def _try_auto_spawn_raid(gs, tok):
    """Auto-spawn a raid if no active raids exist (called every 30 turns)."""
    raids = load_raids()
    if any(r.get("status") == "active" for r in raids.values()):
        return
    boss_key = random.choice(list(WORLD_BOSSES.keys()))
    bd = WORLD_BOSSES[boss_key]
    repo = os.environ.get("GITHUB_REPOSITORY", "xXYoungMoreXx/xXYoungMoreXx")
    try:
        body = (f"## {bd['emoji']} RAID: {bd['nome']}\n\n{bd['desc']}\n\n---\n"
                f"**Comente `/atacar` para participar!**\n\n"
                f"> ⚔️ *Raid gerada pelo sistema de eventos mundiais.*")
        url = f"https://api.github.com/repos/{repo}/issues"
        data = json.dumps({"title": f"[RAID] {boss_key}", "body": body, "labels": ["rpg-action"]}).encode("utf-8")
        req = Request(url, data=data, headers={"Authorization": f"token {tok}", "Accept": "application/vnd.github.v3+json", "Content-Type": "application/json", "User-Agent": "Aethoria"})
        with urlopen(req) as resp:
            issue_number = str(json.loads(resp.read().decode())["number"])
        raids[issue_number] = {
            "boss_key": boss_key, "hp": bd["base_hp"], "max_hp": bd["base_hp"],
            "status": "active", "participants": {},
            "created_by": "system", "created_at": datetime.now(timezone.utc).isoformat()
        }
        save_raids(raids)
        push_world(gs, f"{bd['emoji']} **RAID MUNDIAL!** {bd['nome']} emergiu das trevas! Issue #{issue_number}")
    except Exception as e:
        print(f"⚠️ Auto-spawn raid failed: {e}")

def _raid_init_from_issue(tok, issue_number, raids):
    """Lazy-init a raid from a GitHub Issue if not already in raids.json."""
    url = f"https://api.github.com/repos/{os.environ.get('GITHUB_REPOSITORY')}/issues/{issue_number}"
    req = Request(url, headers={"Authorization": f"token {tok}", "User-Agent": "Aethoria"})
    try:
        with urlopen(req) as resp:
            title = json.loads(resp.read().decode()).get("title", "")
    except Exception as e:
        return None, f"⚠️ Erro ao buscar dados da Raid {issue_number}: {e}"
    boss_key = None
    title_norm = _normalize(title)
    for k in WORLD_BOSSES:
        if _normalize(k) in title_norm:
            boss_key = k; break
    if not boss_key:
        return None, "⚠️ Chefão da Raid desconhecido ou issue inválida."
    bd = WORLD_BOSSES[boss_key]
    raid = {"boss_key": boss_key, "hp": bd["base_hp"], "max_hp": bd["base_hp"], "status": "active", "participants": {}}
    raids[issue_number] = raid
    return raid, None

def _raid_distribute_rewards(raid, bd, user, p, gs):
    """Distribute rewards to all raid participants after boss defeat."""
    mvp = max(raid["participants"].items(), key=lambda x: x[1]["damage"])[0]
    for p_user, stats in raid["participants"].items():
        other_p = p if p_user == user else load_player(p_user)
        p_xp, p_gold = bd["xp_pool"], bd["gold_pool"]
        if p_user == mvp:
            p_xp = int(p_xp * 1.5); p_gold = int(p_gold * 1.5)
        if p_user == user:
            other_p["potions"] += 2
        other_p["xp"] += p_xp; other_p["total_xp"] += p_xp; other_p["gold"] += p_gold
        other_p["raid_count"] = other_p.get("raid_count", 0) + 1
        if raid["boss_key"] not in other_p.get("raid_bosses_killed", []):
            other_p.setdefault("raid_bosses_killed", []).append(raid["boss_key"])
        push_log(other_p, f"🎉 **A RAID {bd['nome']} FOI VENCIDA!** Você ganhou {p_xp} XP e {p_gold}g!")
        if p_user == mvp:
            other_p["raid_mvp_count"] = other_p.get("raid_mvp_count", 0) + 1
            push_log(other_p, f"🌟 **VOCÊ FOI O MVP DA RAID!** (+50% recompensa)")
        check_lu(other_p)
        if p_user != user:
            save_player(other_p)
    push_world(gs, f"👑 **{bd['nome']}** foi derrotado na Raid! MVP: @{mvp}")

def _raid_post_comment(tok, issue_number, user, dmg, raid, bd):
    """Post attack status comment on the raid Issue."""
    try:
        url = f"https://api.github.com/repos/{os.environ.get('GITHUB_REPOSITORY')}/issues/{issue_number}/comments"
        msg = f"⚔️ **@{user}** atacou causando **{dmg}** de dano!\n\n"
        if raid["hp"] > 0:
            msg += f"### {bd['emoji']} {bd['nome']}\n**HP Global:** {hp_bar(raid['hp'], raid['max_hp'])} ({raid['hp']}/{raid['max_hp']})"
        else:
            msg += f"🎉 **A RAID {bd['nome']} FOI VENCIDA!** O Boss caiu!\nRecompensas distribuídas para todos os participantes."
        req = Request(url, data=json.dumps({"body": msg}).encode("utf-8"), headers={
            "Authorization": f"token {tok}", "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json", "User-Agent": "Aethoria"
        })
        urlopen(req)
    except Exception as e:
        print(f"⚠️ Erro ao postar comentário de Raid na issue {issue_number}: {e}")

def action_raid_attack(p, gs, issue_number):
    """Main raid attack flow: validate → init → combat → rewards → comment."""
    if not p.get("classe"):
        push_log(p, "⚠️ Escolha uma classe antes de participar de Raids! Use `rpg:classe:<nome>`."); return
    tok = os.environ.get("GITHUB_TOKEN")
    if not tok:
        push_log(p, "⚠️ Erro: GITHUB_TOKEN ausente."); return
    raids = load_raids()
    raid = raids.get(issue_number)
    if not raid:
        raid, err = _raid_init_from_issue(tok, issue_number, raids)
        if err: push_log(p, err); return
    if raid["status"] == "defeated":
        push_log(p, f"⚠️ Tarde demais! O Boss desta Raid (Issue #{issue_number}) já foi pulverizado."); return
    bd = WORLD_BOSSES[raid["boss_key"]]
    user = p["username"]
    # Join raid if new participant
    if user not in raid["participants"]:
        added_hp = p["level"] * bd["hp_per_level"]
        raid["max_hp"] += added_hp; raid["hp"] += added_hp
        raid["participants"][user] = {"damage": 0, "level": p["level"]}
        push_log(p, f"🔥 Você entrou na Raid! O Boss foi fortalecido em +{added_hp} HP (Escalonamento Nvl {p['level']})!")
        push_world(gs, f"⚔️ @{user} entrou na Raid contra **{bd['nome']}**!")
    # Combat
    dmg = atk_dmg(p)
    if random.random() < 0.6:
        boss_dmg = max(1, bd["base_atk"] - p.get("defense", 5))
        p["hp"] = max(0, p["hp"] - boss_dmg)
        push_log(p, f"🩸 O Boss da Raid revidou! **-{boss_dmg} HP**")
        if p["hp"] <= 0:
            push_log(p, "💀 Você caiu na Raid...")
            death_reset(p); save_raids(raids); return
    raid["participants"][user]["damage"] += dmg
    raid["hp"] -= dmg
    push_log(p, f"⚔️ Você causou **{dmg} de dano** ao Boss da Raid!")
    # Defeat
    if raid["hp"] <= 0:
        raid["status"] = "defeated"; raid["hp"] = 0
        raid["defeated_at"] = datetime.now(timezone.utc).isoformat()
        push_log(p, f"👑 **VOCÊ DEU O GOLPE FINAL NA RAID!** O Boss caiu!")
        _raid_distribute_rewards(raid, bd, user, p, gs)
    save_raids(raids)
    _raid_post_comment(tok, issue_number, user, dmg, raid, bd)


# ══════════════════════════════════════════════════════════════════════════════
#  ACTIONS
# ══════════════════════════════════════════════════════════════════════════════
def action_class(p,gs,cls_key):
    if p.get("classe"): push_log(p,"⚠️ Classe já escolhida. Use `rpg:reiniciar` para recomeçar."); return
    c=CLASSES.get(cls_key)
    if not c: push_log(p,f"❓ Classe inválida: `{cls_key}`"); return
    p.update({"classe":cls_key,"max_hp":c["hp"],"hp":c["hp"],"max_mana":c["mana"],"mana":c["mana"],"defense":c["def"]})
    p["equipment"]["weapon"]=c["weapon"]; p["equipment"]["armor"]=c["armor"]
    # Affinity bonus via github_profile
    gh = p.get("github_profile") or {}
    top_lang = gh.get("top_language","")
    if top_lang and LANG_CLASS.get(top_lang)==cls_key:
        p["max_hp"]+=15; p["hp"]=p["max_hp"]
        push_log(p,f"💻 **Bônus de Afinidade com {top_lang}:** +15 HP máx!")
    push_log(p,f"{c['emoji']} **Classe: {c['nome']}** — _{c['lore']}_")
    push_log(p,f"✨ Habilidade: **{c['skill']}** · `rpg:habilidade` em combate")
    push_world(gs,f"🌟 @{p['username']} escolheu a classe **{c['nome']}** e começa sua jornada!")

DIRS={"rpg:norte":(0,-1,"Norte ⬆️"),"rpg:sul":(0,1,"Sul ⬇️"),"rpg:leste":(1,0,"Leste ▶️"),"rpg:oeste":(-1,0,"Oeste ◀️")}

def action_move(p,gs,dx,dy,dname):
    if p.get("active_monster"): push_log(p,"⚔️ Termine o combate antes de mover!"); return
    nx,ny=p["position"]["x"]+dx,p["position"]["y"]+dy
    if not(0<=nx<5 and 0<=ny<5): push_log(p,"🚧 O mundo de Aethoria termina aqui."); return
    # Poison tick on move
    if p.get("poison_stacks",0)>0:
        dmg=p["poison_stacks"]*5; p["hp"]=max(0,p["hp"]-dmg)
        p["poison_stacks"]=max(0,p["poison_stacks"]-1)
        push_log(p,f"🐍 Veneno causa **{dmg} dmg** ao mover ({p['poison_stacks']} cargas)")
        if p["hp"]<=0: push_log(p,"💀 O veneno te matou enquanto viajava..."); death_reset(p); return
    p["position"]={"x":nx,"y":ny}; t=terrain(p)
    p.setdefault("visited",[]); 
    if t not in p["visited"]: p["visited"].append(t)
    push_log(p,f"🚶 Moveu para **{t}** ({dname}).")
    push_log(p,f"_{LOCATION_LORE.get(t,'...')}_")
    check_quests(p,gs,t=t)
    ev=get_event(gs); night_b=0.12 if "Noite" in dn(gs) else 0
    if t not in SAFE_ZONES:
        if t in BOSSES and not p.get("bosses_defeated",{}).get(t):
            bd=BOSSES[t]; ph=bd["phases"][0]
            p["active_monster"]={"nome":bd["nome"],"hp":ph["hp"],"max_hp":ph["hp"],"atk":ph["atk"],
                                  "xp_reward":bd["xp"],"gold_range":bd["gold_range"],"emoji":bd["emoji"],"is_boss":True}
            p["boss_phase"]=0
            push_log(p,f"{bd['emoji']} **[CHEFÃO]** __{bd['nome']}__ surge!"); push_log(p,ph["desc"])
        else:
            mons=MONSTERS.get(t,[])
            ev_enc=ev.get("encounter_rate_bonus",0)
            for m in mons:
                if random.random()<(m[4]+night_b+ev_enc):
                    ev_hp=ev.get("monster_hp_mult",1.0); mhp=int(m[1]*ev_hp)
                    p["active_monster"]={"nome":m[0],"hp":mhp,"max_hp":mhp,"atk":m[2],"xp_reward":m[3],"gold_range":(2,10),"emoji":"👹","is_boss":False}
                    push_log(p,f"⚠️ **{m[0]}** surge{' (fortalecido pelo evento mundial!)' if ev_hp>1 else ''}!"); break

def action_attack(p,gs):
    m=p.get("active_monster")
    if not m: push_log(p,"😅 Nenhum inimigo. Explore o mapa!"); return
    sk=sb(p); comp=p.get("companion"); ev=get_event(gs)
    first=m.get("hp")==m.get("max_hp") and sk.get("first_strike")
    dmg=atk_dmg(p); 
    if first: dmg=int(dmg*2.0); push_log(p,"🌑 **Primeiro Golpe Crítico!**")
    if comp: dmg+=comp.get("atk_bonus",0)+sk.get("companion_atk",0)
    # Burn from mago skill
    if sk.get("burn",0)>0 and m.get("burning"): m["hp"]-=sk["burn"]; push_log(p,f"🔥 Queima: **{sk['burn']} dmg**!")
    if sk.get("poison_chance",0)>0 and random.random()<sk["poison_chance"]:
        m["poison"]=m.get("poison",0)+1
        if sk.get("poison_debuff",0)>0: m["atk"]=int(m["atk"]*(1-sk["poison_debuff"]))
    if m.get("poison",0)>0: pdmg=m["poison"]*8; m["hp"]-=pdmg; push_log(p,f"🐍 Veneno: **{pdmg} dmg** em {m['nome']}!")
    doubles=sk.get("always_double",False) or (sk.get("double_atk",0)>0 and random.random()<sk["double_atk"])
    if doubles: total=dmg*2; m["hp"]-=total; push_log(p,f"⚔️⚔️ **Ataque Duplo!** 2×{dmg}={total}!")
    else: m["hp"]-=dmg; push_log(p,f"⚔️ **{dmg} de dano** em {m['nome']}!")
    # Boss phase check
    if m.get("is_boss") and m["hp"]>0: _check_boss_phase(p,gs,m)
    if m["hp"]<=0: resolve_kill(p,m,gs)
    else: monster_hits(p,m)

def _check_boss_phase(p,gs,m):
    t=terrain(p); bd=BOSSES.get(t)
    if not bd: return
    phases=bd["phases"]; cur_phase=p.get("boss_phase",0)
    if cur_phase+1>=len(phases): return
    next_ph=phases[cur_phase+1]
    threshold=next_ph["hp"]  # phase 2 triggers when HP drops to phase2 max
    if m["hp"]<=threshold and m.get("max_hp",0)>threshold:
        p["boss_phase"]=cur_phase+1
        m["atk"]=next_ph["atk"]
        push_log(p,next_ph["desc"])
        push_world(gs,f"⚠️ **{m['nome']}** entrou em nova fase durante batalha contra @{p['username']}!")

def action_skill(p,gs):
    cls_key=p.get("classe")
    if not cls_key: push_log(p,"⚠️ Escolha sua classe primeiro!"); return
    m=p.get("active_monster")
    if not m: push_log(p,"⚠️ Nenhum inimigo. Explore o mapa!"); return
    c=CLASSES[cls_key]; sk=sb(p)
    cost=max(5,c["skill_cost"]-sk.get("skill_cost_off",0))
    if p["mana"]<cost: push_log(p,f"💧 Mana insuficiente! Precisa {cost} (tem {p['mana']})."); return
    p["mana"]-=cost
    dmg=atk_dmg(p); multi=c["skill_multi"]
    if cls_key=="cacador" and sk.get("precision_multi",0)>0: multi=sk["precision_multi"]
    dmg=int(dmg*multi); stun=False
    if cls_key=="mago":
        if sk.get("burn",0)>0: m["burning"]=True
        if sk.get("stun",0)>0 and random.random()<sk["stun"]: stun=True
    if cls_key=="ladino" and random.random()<0.40: stun=True
    m["hp"]-=dmg; push_log(p,f"{c['skill_e']} **{c['skill']}!** **{dmg} de dano!**{' 😵 Atordoado!' if stun else ''}")
    if m.get("is_boss") and m["hp"]>0: _check_boss_phase(p,gs,m)
    if m["hp"]<=0: resolve_kill(p,m,gs)
    elif stun: push_log(p,f"😵 {m['nome']} perde o próximo ataque!")
    else: monster_hits(p,m)

def action_unlock_skill(p,sid):
    if p.get("skill_points",0)<=0: push_log(p,"❌ Sem pontos! Suba de nível para ganhar."); return
    tree=SKILL_TREES.get(p.get("classe",""),[])
    sk=next((s for s in tree if s[0]==sid),None)
    if not sk: push_log(p,f"❓ Habilidade `{sid}` não encontrada."); return
    if sid in p.get("skills_unlocked",[]): push_log(p,"⚠️ Habilidade já desbloqueada!"); return
    if sk[5] and sk[5] not in p.get("skills_unlocked",[]): push_log(p,f"🔒 Desbloqueie **{sk[5]}** primeiro!"); return
    if p["skill_points"]<sk[4]: push_log(p,f"❌ Precisa {sk[4]} ponto(s) (tem {p['skill_points']})."); return
    p["skill_points"]-=sk[4]; p.setdefault("skills_unlocked",[]).append(sid)
    push_log(p,f"✨ **{sk[1]}** desbloqueado! _{sk[6]}_")

def action_potion(p):
    if p.get("potions",0)<=0: push_log(p,"❌ Sem poções! Compre ou encontre em inimigos."); return
    heal=random.randint(32,56); p["hp"]=min(p["max_hp"],p["hp"]+heal); p["potions"]-=1
    push_log(p,f"🧪 +{heal} HP · {p['hp']}/{p['max_hp']} · {p['potions']} poções restantes")

def action_rest(p):
    t=terrain(p)
    if t not in SAFE_ZONES: push_log(p,f"⚠️ Não é seguro descansar em **{t}**."); return
    if p.get("active_monster"): push_log(p,"⚠️ Não pode descansar com inimigo!"); return
    h=min(p["max_hp"]-p["hp"],random.randint(28,48)); m=min(p["max_mana"]-p["mana"],random.randint(20,38))
    p["hp"]+=h; p["mana"]+=m; p["poison_stacks"]=0
    push_log(p,f"😴 Descansou em **{t}**: +{h} HP · +{m} Mana · veneno curado.")

def action_tavern(p,gs):
    t=terrain(p)
    rumors=TAVERN_RUMORS.get(t)
    if not rumors: push_log(p,f"🍺 Não há taverna em **{t}**. Vá a uma zona segura."); return
    
    player_msgs = gs.get("tavern_messages", [])
    if player_msgs and random.random() < 0.4:
        text = random.choice(player_msgs)
        push_log(p, text)
        push_log(p, "_(+5 XP por ouvir as histórias da comunidade)_")
        g = xp_gain(p, 5)
    else:
        rumor=random.choice(rumors); text,reward_type,reward_val=rumor
        push_log(p,text)
        if reward_type=="xp": g=xp_gain(p,reward_val); push_log(p,f"_(+{g} XP pelo conhecimento adquirido)_")
        elif reward_type=="gold": p["gold"]+=reward_val; push_log(p,f"_(+{reward_val} ouro encontrado durante a conversa)_")
        elif reward_type=="atk_bonus_boss": p.setdefault("tavern_bonus",{}); p["tavern_bonus"]["boss_atk"]=reward_val
    lv=check_lu(p)
    if lv: push_log(p,lv)

def action_message(p, gs, msg):
    t = terrain(p)
    if t not in TAVERN_RUMORS:
        push_log(p, f"🍺 Não há taverna em **{t}** para deixar uma mensagem. Vá a uma zona segura.")
        return
    msg = msg.strip()[:100]
    if not msg:
        return
    messages = gs.get("tavern_messages", [])
    messages.append(f"💬 \"{msg}\" — _{p['username']}_")
    gs["tavern_messages"] = messages[-20:]
    push_log(p, f"🍺 Você cravou uma mensagem na mesa da taverna em **{t}**!")

def action_interact(p,gs):
    t=terrain(p)
    NPC_MAP={"Aldeia de Ashenvale":"Miriel","Ironhold":"Aldric","Torre do Oráculo":"Oráculo","Porto da Perdição":"Capitão Heron"}
    GENERIC={
        "Templo Esquecido":("🛕 O altar drena 5 HP e concede 30 Mana.",lambda:_temple(p)),
        "Ruínas de Vel'Moran":("🏚️ Inscrições da profecia. +20 XP",lambda:xp_gain(p,20)),
        "Vilarejo de Ravenford":("🏡 Crianças falam de sombras em Kragdor. +10 XP",lambda:xp_gain(p,10)),
        "Cavernas Abissais":("🕳️ Ecos de idiomas perdidos. +12 XP",lambda:xp_gain(p,12)),
        "Floresta de Mirewood":("🌲 Runas élficas. +15 XP +15 Mana",lambda:_mirewood(p)),
        "Catedral em Ruínas":("⛪ Grimório proibido. +25 XP -10 HP",lambda:_catedral(p)),
        "Floresta Amaldiçoada":("💀 Uma alma perdida sussurra segredos. +18 XP",lambda:xp_gain(p,18)),
        "Minas de Ferro":("⚙️ Encontrou uma tocha abandonada. +8 XP",lambda:xp_gain(p,8)),
    }
    if t in NPC_MAP:
        npc=NPC_MAP[t]; dlg=npc_dialogue(npc,p,gs); push_log(p,dlg)
        if t=="Torre do Oráculo":
            xp_b=30 if p.get("titulo") else (20 if len(p.get("bosses_defeated",{}))>=3 else 15)
            g=xp_gain(p,xp_b); push_log(p,f"_(+{g} XP)_")
        lv=check_lu(p)
        if lv: push_log(p,lv)
    elif t in GENERIC:
        msg,effect=GENERIC[t]; push_log(p,msg); effect()
        lv=check_lu(p)
        if lv: push_log(p,lv)
    else:
        push_log(p,f"🔍 Você examina **{t}**. Nada de especial... ainda.")

def _temple(p): p["hp"]=max(1,p["hp"]-5); p["mana"]=min(p["max_mana"],p["mana"]+30)
def _mirewood(p): xp_gain(p,15); p["mana"]=min(p["max_mana"],p["mana"]+15)
def _catedral(p): xp_gain(p,25); p["hp"]=max(1,p["hp"]-10)

def action_buy(p,item_key):
    t=terrain(p)
    if t not in SAFE_ZONES: push_log(p,"🏪 Compre em Ironhold, Ashenvale, Ravenford, Porto ou Mercado."); return
    item=SHOP_BASE.get(item_key)
    if not item: push_log(p,"❓ Item inválido. Use: pocao_menor · pocao · elixir_mana · antidoto"); return
    price=shop_price(p,item["price"],t)
    if p["gold"]<price: push_log(p,f"💰 Ouro insuficiente! {item['nome']} custa {price}g (tem {p['gold']}g)."); return
    p["gold"]-=price
    if "heal" in item: p["potions"]+=1; push_log(p,f"🛒 {item['emoji']} {item['nome']} ({price}g) · Poções: {p['potions']}")
    elif "mana" in item:
        p["mana"]=min(p["max_mana"],p["mana"]+item["mana"]); p["mana_elixirs"]=p.get("mana_elixirs",0)+1
        push_log(p,f"🛒 {item['emoji']} {item['nome']} ({price}g) · +{item['mana']} Mana · Elixirs: {p['mana_elixirs']}")
    elif "cure_poison" in item: p["poison_stacks"]=0; push_log(p,f"🌿 Antídoto usado ({price}g) · Veneno curado!")

def action_craft(p,recipe_key):
    recipe=RECIPES.get(recipe_key)
    if not recipe: push_log(p,f"❓ Receita `{recipe_key}` desconhecida. Disponíveis: pocao_maior · elixir_wyrd · po_reliquias"); return
    # Check ingredients using counter-based system
    if "requires" in recipe:
        for item_id,qty in recipe["requires"].items():
            counter_key = "potions" if item_id == "pocao_menor" else item_id
            if p.get(counter_key, 0) < qty:
                ITEM_NAMES = {"pocao_menor": "Poção Menor", "mana_elixirs": "Elixir de Mana"}
                name = ITEM_NAMES.get(item_id, item_id)
                push_log(p, f"❌ Precisa de {qty}× {name} para fabricar {recipe['nome']}."); return
        # Consume ingredients after validation
        for item_id, qty in recipe["requires"].items():
            counter_key = "potions" if item_id == "pocao_menor" else item_id
            p[counter_key] = p.get(counter_key, 0) - qty
    if "requires_relic" in recipe:
        if len(p.get("relics",[]))<recipe["requires_relic"]: push_log(p,f"❌ Precisa de {recipe['requires_relic']} relíquias."); return
        p["relics"]=p["relics"][recipe["requires_relic"]:]
    result=recipe["result"]
    if recipe["type"]=="consumable":
        p["potions"]+=1; push_log(p,f"🔨 **{recipe['emoji']} {recipe['nome']}** fabricado! (+1 poção especial)")
    elif recipe["type"]=="special":
        if "xp" in result: g=xp_gain(p,result["xp"]); push_log(p,f"🔨 **{recipe['emoji']} {recipe['nome']}** → +{g} XP!")
    p["crafted_count"]=p.get("crafted_count",0)+1
    lv=check_lu(p)
    if lv: push_log(p,lv)

def action_mount(p,gs):
    if not p.get("dragon_mount"): push_log(p,"🐉 Montaria dracônica não disponível. Derrote Drakar em Kragdor primeiro!"); return
    if p.get("active_monster"): push_log(p,"⚔️ Termine o combate primeiro!"); return
    # Dragon mount: teleport to any safe zone
    MOUNT_DEST={"ironhold":{"x":2,"y":2},"ashenvale":{"x":1,"y":1},"porto":{"x":4,"y":3}}
    push_log(p,f"🐉 **Montaria Dracônica!** Para onde voar? Use: `rpg:montar:ironhold` · `rpg:montar:ashenvale` · `rpg:montar:porto`")

def action_mount_to(p,gs,dest):
    if not p.get("dragon_mount"): push_log(p,"🐉 Derrote Drakar primeiro!"); return
    dests={"ironhold":{"x":2,"y":2,"nome":"Ironhold"},"ashenvale":{"x":1,"y":1,"nome":"Aldeia de Ashenvale"},
           "porto":{"x":4,"y":3,"nome":"Porto da Perdição"}}
    d=dests.get(dest)
    if not d: push_log(p,f"❓ Destino inválido. Use: ironhold · ashenvale · porto"); return
    p["position"]={"x":d["x"],"y":d["y"]}; push_log(p,f"🐉 Voou em montaria dracônica para **{d['nome']}**!")
    push_log(p,"_As chamas do dragão iluminam a noite enquanto vocês pousam._")
    t=terrain(p)
    if t not in p.get("visited",[]): p.setdefault("visited",[]).append(t)

def action_prestige(p,gs):
    if p["level"]<10: push_log(p,"❌ Prestígio requer nível 10 máximo. Continue subindo!"); return
    count=p.get("prestige_count",0)+1
    p["prestige_count"]=count; p["level"]=1; p["xp"]=0; p["skill_points"]=2
    p["max_hp"]=cls(p)["hp"]+20*count if cls(p) else 100+20*count
    p["hp"]=p["max_hp"]; p["max_mana"]=cls(p)["mana"]+15*count if cls(p) else 60+15*count; p["mana"]=p["max_mana"]
    p["titulo"]=f"Transcendente {'I'*count}"
    push_log(p,f"🔮 **PRESTÍGIO {count}!** Você transcendeu os limites mortais de Aethoria.")
    push_log(p,f"_Título atualizado: **Transcendente {'I'*count}** · HP e Mana base aumentados permanentemente!_")
    push_world(gs,f"🔮 @{p['username']} atingiu **Prestígio {count}** — um ser além dos mortais!")

def action_pvp(p,gs,target_user):
    if target_user==p["username"]: push_log(p,"😅 Você não pode desafiar a si mesmo!"); return
    target=_rw(f"rpg/players/{target_user}.json")
    if not target: push_log(p,f"❌ Aventureiro **@{target_user}** não encontrado. Ele precisa ter jogado antes."); return
    p_score=p["kills"]*10+p["level"]*50+len(p.get("bosses_defeated",{}))*100
    t_score=target["kills"]*10+target["level"]*50+len(target.get("bosses_defeated",{}))*100
    diff=p_score-t_score
    if diff>50: result="vitória"; p["pvp_wins"]=p.get("pvp_wins",0)+1; xp_gain(p,40); push_log(p,f"🥊 **PvP vs @{target_user}: VITÓRIA!** Seu poder ({p_score}) supera o deles ({t_score}). +40 XP!")
    elif diff<-50: result="derrota"; push_log(p,f"🥊 **PvP vs @{target_user}: DERROTA.** Seu poder ({p_score}) < deles ({t_score}). Volte mais forte!")
    else: result="empate"; xp_gain(p,15); push_log(p,f"🥊 **PvP vs @{target_user}: EMPATE!** Forças equivalentes ({p_score} vs {t_score}). +15 XP!")
    push_world(gs,f"🥊 @{p['username']} desafiou **@{target_user}** em PvP — **{result}**!")

def action_reset(p,gs):
    u=p["username"]; gh=p.get("github_profile"); pb=p.get("profile_bonuses")
    p.clear(); p.update(load_player(u)); p.pop("_new",None)
    p["github_profile"]=gh; p["profile_bonuses"]=pb or []
    push_world(gs,f"🔄 @{u} reiniciou sua jornada."); push_log(p,"🔄 **Nova lenda começa em Aethoria...**")
    push_log(p,"⚔️ Escolha sua classe para começar!")

# ══════════════════════════════════════════════════════════════════════════════
#  NPC MEMORY
# ══════════════════════════════════════════════════════════════════════════════
def npc_dialogue(npc,p,gs):
    mem=gs.setdefault("npc_memory",{}); nm=mem.setdefault(npc,{"met":[]})
    u=p["username"]; first=u not in nm["met"]
    if first: nm["met"].append(u)
    bd=p.get("bosses_defeated",{}); kills=p["kills"]; lvl=p["level"]
    quests_done=sum(1 for q in p.get("quests",[]) if q["concluida"])
    title=p.get("titulo",""); cls_name=cls(p)["nome"] if cls(p) else "Desconhecido"
    prestige=p.get("prestige_count",0)
    D={
        "Miriel":{
            "prestige": f"🧝 **Miriel:** _'Transcendente... Você cruzou a fronteira que os Reis-Dragão nunca ousaram. Aethoria te pertence agora, {u}.'_",
            "all_bosses": f"🧝 **Miriel:** _'{u}... Vel'Krath, Malachar, Drakar, Xal'thar — todos caíram. A profecia se cumpriu. Mas há uma quinta linha que nunca foi traduzida...'_",
            "quest1": f"🧝 **Miriel:** _'Lyra é minha aluna há vinte anos. Ela sabe sobre sua tatuagem, {u}. Mas só contará quando você provar que vale.'_",
            "veteran": f"🧝 **Miriel:** _'Um {cls_name} de nível {lvl} com {kills} mortes. Você não é mais o {u} que chegou aqui. O que Aethoria fez de você é algo novo.'_",
            "first": f"🧝 **Miriel sussurra:** _'A Estrela de Wyrd brilha em você, {u}. Vel'Moran guarda o primeiro fragmento. Cuidado com o Não-Morto.'_",
            "default": f"🧝 **Miriel:** _'As sombras crescem, {u}. Malachar sente o que você carrega. Seja rápido.'_",
        },
        "Aldric":{
            "prestige": f"🔨 **Aldric:** _'Transcendente. Em quarenta anos de Ironhold nunca vi isso. Minha melhor obra é sua — de graça. {u}, você salvou o reino.'_",
            "rich": f"🔨 **Aldric:** _'{u}, com esse ouro você poderia comprar Ironhold. Mas metal vale menos que sobrevivência. Gaste bem.'_",
            "boss_slayer": f"🔨 **Aldric:** _'Ouvi que você derrubou {len(bd)} chefão/chefões. Merece o melhor aço desta forja, {u}.'_",
            "first": f"🔨 **Aldric:** _'Quarenta anos forjando aço e nunca vi uma marca como a sua, {u}. O que Kragdor esconde está acordando.'_",
            "default": f"🔨 **Aldric:** _'Ironhold resistiu a mil cercos. Malachar é diferente de tudo, {u}. Compre suprimentos antes de partir.'_",
        },
        "Oráculo":{
            "prestige": f"🗼 **O Oráculo:** _'Transcendente {u}... Você existe além da profecia agora. Há uma sexta relíquia — a que nunca foi criada — esperando por alguém como você.'_ +40 XP",
            "all_bosses": f"🗼 **O Oráculo:** _'Os quatro guardiões caíram, {u}. O reino respira. Mas Aethoria nunca terá paz permanente. Sempre haverá uma nova escuridão.'_ +30 XP",
            "first": f"🗼 **O Oráculo:** _'Três fragmentos. Três guardiões. Uma escolha irrevogável, {u}. E você já sabe qual é a quarta verdade — mesmo que não reconheça ainda.'_ +20 XP",
            "default": f"🗼 **O Oráculo:** _'O {cls_name} avança. {kills} criaturas. {len(bd)} guardiões. A profecia converge, {u}.'_ +15 XP",
        },
        "Capitão Heron":{
            "malachar_dead": f"⚓ **Capitão Heron:** _'Malachar caiu? Então você é mais do que parece, {u}. O barco está pronto. Xal'thar espera — e o que habita lá está acordado há séculos.'_",
            "first": f"⚓ **Capitão Heron:** _'Dez navios tentaram chegar às Ilhas, {u}. Nenhum voltou inteiro. Primeiro derrube Malachar. Então conversamos sobre preço.'_",
            "default": f"⚓ **Capitão Heron:** _'Porto da Perdição tem segredos, {u}. Mas nenhum tão profundo quanto o que Xal'thar guarda. Derrube Malachar primeiro.'_",
        },
    }
    d=D.get(npc,{}); 
    if not d: return f"🗣️ **{npc}:** _'Boa sorte, {u}.'_"
    if prestige>=1 and "prestige" in d: return d["prestige"]
    if len(bd)>=4 and "all_bosses" in d: return d["all_bosses"]
    if npc=="Miriel" and quests_done>=1 and "quest1" in d: return d["quest1"]
    if npc=="Miriel" and lvl>=6 and "veteran" in d: return d["veteran"]
    if npc=="Aldric" and p["gold"]>=200 and "rich" in d: return d["rich"]
    if npc=="Aldric" and len(bd)>=1 and "boss_slayer" in d: return d["boss_slayer"]
    if npc=="Capitão Heron" and "Fortaleza das Sombras" in bd and "malachar_dead" in d: return d["malachar_dead"]
    if first and "first" in d: return d["first"]
    return d.get("default","")

# ══════════════════════════════════════════════════════════════════════════════
#  LEADERBOARD
# ══════════════════════════════════════════════════════════════════════════════
def score(p):
    gh = p.get("github_profile", {})
    gh_score = gh.get("public_repos", 0) * 10 + gh.get("total_stars", 0) * 50 + gh.get("followers", 0) * 25
    return p.get("total_xp",0) + p.get("kills",0)*5 + len(p.get("bosses_defeated",{}))*100 + len(p.get("conquistas",[]))*30 + p.get("prestige_count",0)*500 + gh_score

def update_lb(lb,p):
    entry={"username":p["username"],"score":score(p),"level":p["level"],"prestige":p.get("prestige_count",0),
           "classe":p.get("classe"),"kills":p.get("kills",0),"bosses":len(p.get("bosses_defeated",{})),
           "conquistas":len(p.get("conquistas",[])),"titulo":p.get("titulo"),
           "top_lang":p.get("github_profile",{}).get("top_language") if p.get("github_profile") else None,
           "last_played":p.get("last_played","")}
    lb["players"]=[e for e in lb.get("players",[]) if e["username"]!=p["username"]]
    lb["players"].append(entry); lb["players"].sort(key=lambda x:x["score"],reverse=True); lb["players"]=lb["players"][:20]
    lb["updated"]=datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

def render_lb(lb):
    players=lb.get("players",[])
    if not players: return "_Nenhum aventureiro ainda. Seja o primeiro!_"
    medals=["🥇","🥈","🥉"]
    rows=["| # | Aventureiro | Classe | Nível | Score | Bosses | Conquistas | Lang |","|---|---|---|---|---|---|---|---|"]
    for i,e in enumerate(players[:10]):
        pos=medals[i] if i<3 else f"{i+1}º"
        c=CLASSES.get(e.get("classe",""),{})
        cls_s=f"{c.get('emoji','?')} {c.get('nome','?')}" if c else "—"
        prest=f" ✨×{e['prestige']}" if e.get("prestige",0)>0 else ""
        title=f" _({e['titulo']})_" if e.get("titulo") else ""
        lang=f"`{e['top_lang']}`" if e.get("top_lang") else "—"
        rows.append(f"| {pos} | **@{e['username']}**{prest}{title} | {cls_s} | {e['level']} | {e['score']} | {e['bosses']} | {e['conquistas']} | {lang} |")
    return "\n".join(rows)

def render_skill_tree(p):
    tree=SKILL_TREES.get(p.get("classe",""),[])
    if not tree: return "_Escolha uma classe para ver sua árvore._"
    unlocked=set(p.get("skills_unlocked",[])); pts=p.get("skill_points",0)
    branches={}
    for sk in tree: branches.setdefault(sk[2],[]).append(sk)
    out=[f"**{pts} ponto(s) disponível(is)**"]
    for br,skills in branches.items():
        parts=[]
        for sk in skills:
            if sk[0] in unlocked: icon="✅"
            elif (not sk[5] or sk[5] in unlocked) and pts>=sk[4]: icon="🔓"
            else: icon="🔒"
            parts.append(f"{icon}`{sk[0]}` **{sk[1]}** — _{sk[6]}_")
        out.append(f"{br}: " + " → ".join(parts))
    return "\n".join(out)

# ══════════════════════════════════════════════════════════════════════════════
#  README RENDERER
# ══════════════════════════════════════════════════════════════════════════════
def _render_raids_preclass(base):
    """Render active raids section for the pre-class README block."""
    raids = load_raids()
    active = [(iss, r) for iss, r in raids.items() if r.get("status") == "active"]
    if not active:
        return ""
    repo = os.environ.get("GITHUB_REPOSITORY", "xXYoungMoreXx/xXYoungMoreXx")
    rows = "".join(
        f"\n| {WORLD_BOSSES[r['boss_key']]['emoji']} {r['boss_key']} | {hp_bar(r['hp'], r['max_hp'])} | {len(r['participants'])} | [Ver Raid](https://github.com/{repo}/issues/{iss}) |"
        for iss, r in active
    )
    return f"""
---

### ⚔️ Raids Ativas
> _Escolha uma classe para participar das Raids!_

| Boss | HP | Jogadores | Link |
|---|---|---|---|{rows}
"""

def build_block(p,gs,lb):
    base="../../issues/new?labels=rpg-action&title="
    ev=get_event(gs); c=cls(p)
    titulo=f" · 🏅 *{p.get('titulo')}*" if p.get("titulo") else ""
    prestige_badge=f" · 🔮 **Prestígio {'I'*p.get('prestige_count',0)}**" if p.get("prestige_count",0) else ""

    if not p.get("classe"):
        gh=p.get("github_profile"); lang=gh.get("top_language") if gh else None
        lang_hint=""
        if lang and lang in LANG_CLASS:
            ac=LANG_CLASS[lang]; cls_d=CLASSES[ac]
            lang_hint=f"\n> 💻 **Seu GitHub: linguagem `{lang}` → afinidade com {cls_d['emoji']} {cls_d['nome']}** _(bônus ao escolher!)_"
        return f"""<!-- RPG_START -->
## ⚔️ AETHORIA: O REINO FRAGMENTADO — Escolha sua Classe
{lang_hint}
> *Há mil anos, os Reis-Dragão uniam Aethoria. O último foi traído pelo Pacto das Sombras. O reino se fragmentou.*
> *Uma profecia fala de um Escolhido marcado pela Estrela de Wyrd. Você acordou em Ironhold sem memórias.*
> *Uma tatuagem arcana pulsa em seu pulso. A jornada pertence a quem ousa começar.*

| Classe | Lore | HP | Mana | DEF | Habilidade |
|--------|------|:--:|:----:|:---:|------------|
| [{CLASSES['guerreiro']['emoji']} Guerreiro]({base}rpg%3Aclasse%3Aguerreiro) | {CLASSES['guerreiro']['lore']} | 130 | 40 | 10 | Investida Furiosa (2×) |
| [{CLASSES['mago']['emoji']} Mago]({base}rpg%3Aclasse%3Amago) | {CLASSES['mago']['lore']} | 85 | 100 | 4 | Tempestade Arcana (3×) |
| [{CLASSES['cacador']['emoji']} Caçador]({base}rpg%3Aclasse%3Acacador) | {CLASSES['cacador']['lore']} | 105 | 60 | 7 | Tiro de Precisão (2.2×) |
| [{CLASSES['ladino']['emoji']} Ladino]({base}rpg%3Aclasse%3Aladino) | {CLASSES['ladino']['lore']} | 95 | 70 | 5 | Golpe Furtivo (2× + stun) |
| [{CLASSES['paladino']['emoji']} Paladino]({base}rpg%3Aclasse%3Apaladino) | {CLASSES['paladino']['lore']} | 140 | 70 | 12 | Julgamento Divino (1.8×) |
| [{CLASSES['necromante']['emoji']} Necromante]({base}rpg%3Aclasse%3Anecromante) | {CLASSES['necromante']['lore']} | 85 | 120 | 4 | Exército de Ossos (2.5×) |
| [{CLASSES['bardo']['emoji']} Bardo]({base}rpg%3Aclasse%3Abardo) | {CLASSES['bardo']['lore']} | 95 | 85 | 6 | Canção do Caos (2×) |

> 🎮 *Clique em uma classe para começar! Qualquer visitante pode jogar.*

---

### 🌍 Evento Mundial Atual
> {ev['emoji']} **{ev['nome']}** — {ev['desc']}
{_render_raids_preclass(base)}
---

### 🏆 Quadro da Guilda
{render_lb(lb)}
> _Score = XP total + kills×5 + chefões×100 + conquistas×30 + prestígio×500 + repos×10 + estrelas×50 · Atualizado: {lb.get('updated','—')}_

<!-- RPG_END -->"""

    # Full game block
    sk=sb(p); xp_next=XP_TABLE[min(p["level"]+1,10)] if p["level"]<10 else "MAX"
    inv=", ".join(f"{i['emoji']} {i['nome']}" for i in p.get("inventory",[])) or "_vazio_"
    relics_str=", ".join(f"{r['emoji']} {r['nome']}" for r in p.get("relics",[])) or "_nenhuma_"
    comp=p.get("companion")
    comp_row=f"\n| 🧝 Companheiro | **{comp['nome']}** _{comp['classe']}_ (+{comp['atk_bonus']+sk.get('companion_atk',0)} ATK) |" if comp else ""
    dragon_row=f"\n| 🐉 Montaria | Montaria Dracônica ativa · `rpg:montar:ironhold` · `rpg:montar:ashenvale` · `rpg:montar:porto` |" if p.get("dragon_mount") else ""
    gh=p.get("github_profile")
    gh_row=f"\n| 🌐 GitHub | @{gh['login']} · {gh.get('public_repos',0)} repos · {gh.get('total_stars',0)}⭐ · {gh.get('followers',0)} followers · `{gh.get('top_language','—')}` |" if gh else ""
    quests_rows="".join(f"\n| {'✅' if q['concluida'] else '📜'} | **{q['titulo']}** | _{q['objetivo']}_ |" for q in p.get("quests",[]))
    boss_rows="".join(f"\n| {bd['emoji']} | **{bd['nome']}** | {loc} | {'☠️ Derrotado' if p.get('bosses_defeated',{}).get(loc) else '😈 Vivo'} |" for loc,bd in BOSSES.items())
    conqs_str=", ".join(next((c2[1] for c2 in CONQUISTAS if c2[0]==cid),"?") for cid in p.get("conquistas",[])) or "_nenhuma_"
    fac=p.get("factions",{"ordem":0,"circulo":0,"pacto":0})
    def frep(v):
        v=max(-5,min(5,v))
        if v>3: return "🟢🟢🟢🟢🟢 Aliado"
        if v>1: return "🟢🟢🟢⬜⬜ Amigável"
        if v>-1: return "🟡🟡⬜⬜⬜ Neutro"
        if v>-3: return "🔴🔴⬜⬜⬜ Hostil"
        return "🔴🔴🔴🔴🔴 Inimigo"
    m = p.get("active_monster")
    m_block=""
    if m:
        tag="⚠️ **[CHEFÃO]**" if m.get("is_boss") else "👹"
        phase_str=f" _(Fase {p.get('boss_phase',0)+1})_" if m.get("is_boss") else ""
        m_block=f"""
---
### {tag} {m['emoji']} {m['nome']}{phase_str}
| HP | {hp_bar(m['hp'],m['max_hp'])} |
|---|---|

> **[⚔️ Atacar]({base}rpg%3Aatacar)** · **[{c['skill_e']} {c['skill']}]({base}rpg%3Ahabilidade)** · **[🧪 Poção]({base}rpg%3Apocao)**
"""
    raids = load_raids()
    active_raids_block = ""
    active_raid_list = [(iss, r) for iss, r in raids.items() if r["status"] == "active"]
    if active_raid_list:
        repo_name = os.environ.get('GITHUB_REPOSITORY', 'xXYoungMoreXx/xXYoungMoreXx')
        raid_rows = "".join(f"\n| {WORLD_BOSSES[r['boss_key']]['emoji']} {r['boss_key']} | {hp_bar(r['hp'], r['max_hp'])} | {len(r['participants'])} | [⚔️ Juntar-se à Raid!](https://github.com/{repo_name}/issues/{iss}) |" for iss, r in active_raid_list)
        active_raids_block = f"""
---
### ⚔️ Dungeons Cooperativas (Raids Ativas)
> _Qualquer jogador pode entrar na Raid comentando `/atacar` na Issue! O dano e as recompensas são distribuídos entre todos os participantes._

| Boss | HP Global | Participantes | Ação |
|---|---|---|---|{raid_rows}
"""
        
    log_txt="\n".join(f"> {l}" for l in p.get("log",[])[:7])
    wlog="\n".join(f"> 🌍 {l}" for l in gs.get("world_log",[])[:4])

    return f"""<!-- RPG_START -->
## ⚔️ AETHORIA: O REINO FRAGMENTADO{titulo}{prestige_badge}

> *Há mil anos, os Reis-Dragão uniam Aethoria. O último foi traído pelo Pacto das Sombras. O reino se fragmentou.*
> *Uma profecia fala de um Escolhido marcado pela Estrela de Wyrd. Você acordou em Ironhold sem memórias.*
> *Qualquer visitante pode agir — a história pertence a quem ousa escrever.*

> Turno **#{gs['turn']}** · {dn(gs)} · Jogando como: **@{p['username']}**

---

### 🌍 Evento Mundial — {ev['emoji']} {ev['nome']}
> _{ev['desc']}_
> Efeitos: Monstros {int((ev.get('monster_hp_mult',1.0))*100)-100:+d}% HP · Encontros {int(ev.get('encounter_rate_bonus',0)*100):+d}% · XP ×{ev.get('xp_mult',1.0):.1f} · Preços {int((ev.get('price_mult',1.0))-1)*100:+d}%

---

### 🗺️ Mapa de Aethoria
```
{render_map(p)}
```
> 🧙 Você · 🌨️Tundra · 🏔️Pico · 🗼Oráculo · 🌲Mirewood · 🏘️Ashenvale · 🏚️Vel'Moran · 🏰Fortaleza
> 🌑Pântano · 🌾Planície · 🏙️Ironhold · ⛏️Kragdor · 🌳Floresta · 🛕Templo · 🏡Ravenford

📍 **{terrain(p)}** — _{LOCATION_LORE.get(terrain(p),'...')}_

---

### 📊 Status
| Atributo | |
|---|---|
| ❤️ HP | {hp_bar(p['hp'],p['max_hp'])} |
| 💧 Mana | {mp_bar(p['mana'],p['max_mana'])} |
| 🧙 Classe | {c['emoji']} **{c['nome']}** · Habilidade: {c['skill_e']} {c['skill']} |
| ⭐ Nível | {p['level']} · XP: {p['xp']}/{xp_next} · Total: {p.get('total_xp',0)} |
| 💰 Ouro | {p['gold']}g |
| 🧪 Poções | {p['potions']} · 🐍 Veneno: {p.get('poison_stacks',0)} cargas |
| ☠️ Kills/Mortes | {p['kills']} / {p.get('deaths',0)} |
| 🗡️ Arma / 🛡️ Armadura | {p['equipment']['weapon']} / {p['equipment']['armor']} |
| 💎 Relíquias | {relics_str} |
| 🎖️ Conquistas | {conqs_str} |{comp_row}{dragon_row}{gh_row}

---

### 🌳 Árvore de Habilidades ({p.get('skill_points',0)} ponto(s))
{render_skill_tree(p)}

---

### 🏹 Facções
| Facção | Reputação |
|---|---|
| ⚔️ Ordem do Aço | {frep(fac.get('ordem',0))} |
| 🌿 Círculo Verdante | {frep(fac.get('circulo',0))} |
| 🖤 Pacto das Sombras | {frep(fac.get('pacto',0))} |

---

### 📜 Missões
| | Missão | Objetivo |
|---|---|---|{quests_rows}

---

### 👹 Chefões
| | | Local | Status |
|---|---|---|---|{boss_rows}
{m_block}{active_raids_block}

---

### 🎮 Ações — _Última jogada: @{p['username']}_

**🧭 Mover:** [⬆️]({base}rpg%3Anorte) [⬇️]({base}rpg%3Asul) [◀️]({base}rpg%3Aoeste) [▶️]({base}rpg%3Aleste)
**⚔️ Combate:** [⚔️ Atacar]({base}rpg%3Aatacar) · [{c['skill_e']} {c['skill']}]({base}rpg%3Ahabilidade) · [🧪 Poção]({base}rpg%3Apocao)
**🍺 Explorar:** [🔍 Interagir]({base}rpg%3Ainteragir) · [😴 Descansar]({base}rpg%3Adescansar) · [🍺 Taverna]({base}rpg%3Ataverna)
**🛒 Comprar:** [🧪-8g]({base}rpg%3Acomprar%3Apocao_menor) · [💊-15g]({base}rpg%3Acomprar%3Apocao) · [💙-12g]({base}rpg%3Acomprar%3Aelixir_mana) · [🌿-10g]({base}rpg%3Acomprar%3Aantidoto)
**🔨 Crafting:** [Poção Superior]({base}rpg%3Acraftar%3Apocao_maior) · [Elixir Wyrd]({base}rpg%3Acraftar%3Aelixir_wyrd) · [Pó de Relíquias]({base}rpg%3Acraftar%3Apo_reliquias)
**🌳 Skill:** `rpg:skill:ID` — [{c['emoji']} Ver IDs no SETUP.md](../../blob/main/SETUP.md)
**⚙️ Outros:** [🔄 Reiniciar]({base}rpg%3Areiniciar) · [🔮 Prestígio (nív.10)]({base}rpg%3Aprestigio) · `rpg:desafiar:USERNAME` · `rpg:montar:DESTINO`

---

### 📖 Log de @{p['username']}
{log_txt}

{f"### 🌍 Eventos Recentes do Mundo{chr(10)}{wlog}" if wlog.strip() else ""}

---

### 🏆 Quadro da Guilda — Top Aventureiros
{render_lb(lb)}
> _Score = XP + kills×5 + chefões×100 + conquistas×30 + prestígio×500 + repos×10 + estrelas×50 · {lb.get('updated','—')}_

<!-- RPG_END -->"""

def update_readme(p,gs,lb):
    rp=Path("README.md"); content=rp.read_text("utf-8")
    updated=re.sub(r"<!-- RPG_START -->.*?<!-- RPG_END -->",build_block(p,gs,lb),content,flags=re.DOTALL)
    rp.write_text(updated,"utf-8")

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    if len(sys.argv)<2: print("Uso: engine.py <title> [username]"); sys.exit(1)
    raw=sys.argv[1].strip().lower(); u=sys.argv[2].strip() if len(sys.argv)>2 else "anon"
    # Skip bots
    if "bot" in u.lower() and "github" in u.lower(): print("⏭️ Skipped: bot user"); sys.exit(0)
    tok=os.environ.get("GITHUB_TOKEN")
    gs=load_gs(); gs["turn"]=gs.get("turn",0)+1; _cleanup_raids()
    p=load_player(u); is_new=p.pop("_new",False); p["sessions"]=p.get("sessions",0)+1
    if not p.get("factions"): p["factions"]={"ordem":0,"circulo":0,"pacto":0}
    if is_new and u!="anon":
        print(f"🌐 Novo jogador @{u} — buscando perfil GitHub...")
        profile=fetch_profile(u,tok)
        if profile:
            p["github_profile"]=profile; msgs=apply_profile_bonuses(profile,p)
            p["profile_bonuses"]=msgs  # store as list of messages
            for m in msgs: push_log(p,m)
            push_world(gs,f"🌟 **@{u}** chegou a Aethoria! _({profile.get('top_language','?')} · {profile.get('followers',0)} followers)_")
        push_log(p,f"⚔️ Bem-vindo, **@{u}**! Escolha sua classe para começar.")
    # Process action
    if raw in DIRS:
        dx,dy,name=DIRS[raw]; action_move(p,gs,dx,dy,name)
    elif raw=="rpg:atacar":     action_attack(p,gs)
    elif raw=="rpg:habilidade": action_skill(p,gs)
    elif raw=="rpg:pocao":      action_potion(p)
    elif raw=="rpg:interagir":  action_interact(p,gs)
    elif raw=="rpg:descansar":  action_rest(p)
    elif raw=="rpg:taverna":    action_tavern(p,gs)
    elif raw=="rpg:reiniciar":  action_reset(p,gs)
    elif raw=="rpg:prestige" or raw=="rpg:prestigio": action_prestige(p,gs)
    elif raw=="rpg:montar":     action_mount(p,gs)
    elif raw.startswith("rpg:classe:"):   action_class(p,gs,raw.split("rpg:classe:")[1])
    elif raw.startswith("rpg:skill:"):    action_unlock_skill(p,raw.split("rpg:skill:")[1])
    elif raw.startswith("rpg:comprar:"): action_buy(p,raw.split("rpg:comprar:")[1])
    elif raw.startswith("rpg:craftar:"): action_craft(p,raw.split("rpg:craftar:")[1])
    elif raw.startswith("rpg:montar:"):  action_mount_to(p,gs,raw.split("rpg:montar:")[1])
    elif raw.startswith("rpg:desafiar:"): action_pvp(p,gs,raw.split("rpg:desafiar:")[1])
    elif raw.startswith("rpg:criar_raid:"): action_create_raid(p, gs, raw.split("rpg:criar_raid:")[1])
    elif raw.startswith("rpg:raid_attack:"): 
        issue_number = raw.split("rpg:raid_attack:")[1]
        action_raid_attack(p, gs, issue_number)
    elif raw.startswith("rpg:mensagem:"): action_message(p, gs, raw.split("rpg:mensagem:")[1])
    else: push_log(p,f"❓ Ação `{raw}` desconhecida.")
    check_conquistas(p,gs); lv=check_lu(p)
    if lv: push_log(p,lv)
    lb=load_lb(); update_lb(lb,p); save_lb(lb)
    p["last_played"]=datetime.now(timezone.utc).isoformat()
    save_player(p); save_gs(gs); update_readme(p,gs,lb)
    # Auto-spawn raid every 30 turns if none active
    if gs["turn"] % 30 == 0 and tok:
        _try_auto_spawn_raid(gs, tok)
    print(f"✅ '{raw}' → @{u} · T#{gs['turn']} · Score:{score(p)}")

if __name__=="__main__": main()
