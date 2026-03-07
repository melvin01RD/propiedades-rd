"""
Seed: 32 demarcaciones administrativas de República Dominicana
+ sectores principales de Distrito Nacional, Santo Domingo y Santiago.

Uso:
    python -m src.persistence.seeds.seed_provinces
"""

PROVINCES_SEED = [
    {"id": 1,  "name": "Distrito Nacional",       "code": "DN"},
    {"id": 2,  "name": "Azua",                    "code": "AZ"},
    {"id": 3,  "name": "Bahoruco",                "code": "BH"},
    {"id": 4,  "name": "Barahona",                "code": "BR"},
    {"id": 5,  "name": "Dajabón",                 "code": "DJ"},
    {"id": 6,  "name": "Duarte",                  "code": "DU"},
    {"id": 7,  "name": "Elías Piña",              "code": "EP"},
    {"id": 8,  "name": "El Seibo",                "code": "ES"},
    {"id": 9,  "name": "Espaillat",               "code": "EX"},
    {"id": 10, "name": "Hato Mayor",              "code": "HM"},
    {"id": 11, "name": "Hermanas Mirabal",        "code": "HI"},
    {"id": 12, "name": "Independencia",           "code": "IN"},
    {"id": 13, "name": "La Altagracia",           "code": "AL"},
    {"id": 14, "name": "La Romana",               "code": "LR"},
    {"id": 15, "name": "La Vega",                 "code": "VE"},
    {"id": 16, "name": "María Trinidad Sánchez",  "code": "MT"},
    {"id": 17, "name": "Monseñor Nouel",          "code": "MN"},
    {"id": 18, "name": "Monte Cristi",            "code": "MC"},
    {"id": 19, "name": "Monte Plata",             "code": "MP"},
    {"id": 20, "name": "Pedernales",              "code": "PE"},
    {"id": 21, "name": "Peravia",                 "code": "PV"},
    {"id": 22, "name": "Puerto Plata",            "code": "PP"},
    {"id": 23, "name": "Samaná",                  "code": "SM"},
    {"id": 24, "name": "San Cristóbal",           "code": "SC"},
    {"id": 25, "name": "San José de Ocoa",        "code": "SO"},
    {"id": 26, "name": "San Juan",                "code": "SJ"},
    {"id": 27, "name": "San Pedro de Macorís",    "code": "SP"},
    {"id": 28, "name": "Sánchez Ramírez",         "code": "SR"},
    {"id": 29, "name": "Santiago",                "code": "STG"},
    {"id": 30, "name": "Santiago Rodríguez",      "code": "SRD"},
    {"id": 31, "name": "Santo Domingo",           "code": "SD"},
    {"id": 32, "name": "Valverde",                "code": "VD"},
]

# Sectores por province_id
# DN = 1, Santo Domingo = 31, Santiago = 29, La Romana = 14,
# Puerto Plata = 22, La Altagracia = 13
SECTORS_SEED = [

    # ── Distrito Nacional (province_id=1) ──────────────────────────────
    {"name": "Piantini",               "province_id": 1},
    {"name": "Naco",                   "province_id": 1},
    {"name": "Evaristo Morales",       "province_id": 1},
    {"name": "Bella Vista",            "province_id": 1},
    {"name": "Serrallés",              "province_id": 1},
    {"name": "La Esperilla",           "province_id": 1},
    {"name": "El Millón",              "province_id": 1},
    {"name": "Gazcue",                 "province_id": 1},
    {"name": "Ciudad Colonial",        "province_id": 1},
    {"name": "Los Prados",             "province_id": 1},
    {"name": "Mirador Norte",          "province_id": 1},
    {"name": "Mirador Sur",            "province_id": 1},
    {"name": "Renacimiento",           "province_id": 1},
    {"name": "Paraíso",                "province_id": 1},
    {"name": "Julieta",                "province_id": 1},
    {"name": "Los Cacicazgos",         "province_id": 1},
    {"name": "La Julia",               "province_id": 1},
    {"name": "Cristo Rey",             "province_id": 1},
    {"name": "Gascue",                 "province_id": 1},
    {"name": "El Vergel",              "province_id": 1},

    # ── Santo Domingo (province_id=31) ─────────────────────────────────
    {"name": "Arroyo Hondo",           "province_id": 31},
    {"name": "Arroyo Hondo Viejo",     "province_id": 31},
    {"name": "Los Ríos",               "province_id": 31},
    {"name": "La Ureña",               "province_id": 31},
    {"name": "Alma Rosa",              "province_id": 31},
    {"name": "Los Alcarrizos",         "province_id": 31},
    {"name": "Boca Chica",             "province_id": 31},
    {"name": "San Isidro",             "province_id": 31},
    {"name": "Manoguayabo",            "province_id": 31},
    {"name": "Jardines del Norte",     "province_id": 31},
    {"name": "Sabana Perdida",         "province_id": 31},
    {"name": "Guaricano",              "province_id": 31},
    {"name": "Herrera",                "province_id": 31},
    {"name": "Palma Real",             "province_id": 31},
    {"name": "Fernández",              "province_id": 31},
    {"name": "Serena Village",         "province_id": 31},
    {"name": "Cuesta Hermosa",         "province_id": 31},
    {"name": "Mega Centro",            "province_id": 31},
    {"name": "La Isabelita",           "province_id": 31},
    {"name": "Ensanche Ozama",         "province_id": 31},

    # ── Santiago (province_id=29) ───────────────────────────────────────
    {"name": "Pekín",                  "province_id": 29},
    {"name": "Las Colinas",            "province_id": 29},
    {"name": "Los Jardines",           "province_id": 29},
    {"name": "Bella Vista",            "province_id": 29},
    {"name": "El Embrujo",             "province_id": 29},
    {"name": "La Trinitaria",          "province_id": 29},
    {"name": "Reparto Conuco",         "province_id": 29},
    {"name": "Ensanche Bermúdez",      "province_id": 29},
    {"name": "Gurabo",                 "province_id": 29},
    {"name": "Nibaje",                 "province_id": 29},
    {"name": "Loma Linda",             "province_id": 29},
    {"name": "Los Salados",            "province_id": 29},
    {"name": "Pueblo Nuevo",           "province_id": 29},
    {"name": "Villa Olímpica",         "province_id": 29},
    {"name": "Centro de la Ciudad",    "province_id": 29},

    # ── La Romana (province_id=14) ──────────────────────────────────────
    {"name": "Casa de Campo",          "province_id": 14},
    {"name": "Bayahibe",               "province_id": 14},
    {"name": "Centro de La Romana",    "province_id": 14},

    # ── Puerto Plata (province_id=22) ───────────────────────────────────
    {"name": "Sosúa",                  "province_id": 22},
    {"name": "Cabarete",               "province_id": 22},
    {"name": "Costambar",              "province_id": 22},
    {"name": "Cofresí",                "province_id": 22},
    {"name": "Centro Puerto Plata",    "province_id": 22},

    # ── La Altagracia (province_id=13) ──────────────────────────────────
    {"name": "Punta Cana",             "province_id": 13},
    {"name": "Bávaro",                 "province_id": 13},
    {"name": "Cap Cana",               "province_id": 13},
    {"name": "Uvero Alto",             "province_id": 13},
    {"name": "Macao",                  "province_id": 13},
    {"name": "Higüey Centro",          "province_id": 13},
]
