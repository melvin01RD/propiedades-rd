"""
Seed: amenidades estándar para portal inmobiliario RD
Ejecutar después de las migraciones de Alembic.
"""

AMENITIES_SEED = [
    # --- Seguridad ---
    {"name": "Seguridad 24/7",      "slug": "seguridad-24-7",    "category": "security",   "icon": "shield"},
    {"name": "Cámaras CCTV",        "slug": "camaras-cctv",      "category": "security",   "icon": "camera"},
    {"name": "Portón eléctrico",    "slug": "porton-electrico",  "category": "security",   "icon": "gate"},
    {"name": "Cerca eléctrica",     "slug": "cerca-electrica",   "category": "security",   "icon": "zap"},

    # --- Recreación ---
    {"name": "Piscina",             "slug": "piscina",           "category": "recreation", "icon": "waves"},
    {"name": "Gimnasio",            "slug": "gimnasio",          "category": "recreation", "icon": "dumbbell"},
    {"name": "Cancha de tenis",     "slug": "cancha-tenis",      "category": "recreation", "icon": "tennis"},
    {"name": "Área de juegos",      "slug": "area-juegos",       "category": "recreation", "icon": "playground"},
    {"name": "Salón de eventos",    "slug": "salon-eventos",     "category": "recreation", "icon": "building"},
    {"name": "Cancha de basketball","slug": "cancha-basketball", "category": "recreation", "icon": "circle"},

    # --- Servicios ---
    {"name": "Generador eléctrico", "slug": "generador",         "category": "services",   "icon": "power"},
    {"name": "Cisterna",            "slug": "cisterna",          "category": "services",   "icon": "droplets"},
    {"name": "Gas natural",         "slug": "gas-natural",       "category": "services",   "icon": "flame"},
    {"name": "Ascensor",            "slug": "ascensor",          "category": "services",   "icon": "arrow-up"},
    {"name": "Lobby",               "slug": "lobby",             "category": "services",   "icon": "door-open"},
    {"name": "Área de lavandería",  "slug": "lavanderia",        "category": "services",   "icon": "washing-machine"},

    # --- Exterior ---
    {"name": "Jardín",              "slug": "jardin",            "category": "exterior",   "icon": "tree"},
    {"name": "Terraza",             "slug": "terraza",           "category": "exterior",   "icon": "sun"},
    {"name": "Balcón",              "slug": "balcon",            "category": "exterior",   "icon": "layout"},
    {"name": "BBQ / Parrilla",      "slug": "bbq",               "category": "exterior",   "icon": "flame"},
    {"name": "Vista al mar",        "slug": "vista-al-mar",      "category": "exterior",   "icon": "anchor"},
    {"name": "Vista a la montaña",  "slug": "vista-montana",     "category": "exterior",   "icon": "mountain"},
]
