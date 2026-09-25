"""Replaceable Lilly dignity data; scoring logic deliberately lives elsewhere."""

from .models import PlanetName as P


SIGNS = ("Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis")

DOMICILE = {
    "Ari": P.MARS, "Tau": P.VENUS, "Gem": P.MERCURY, "Can": P.MOON,
    "Leo": P.SUN, "Vir": P.MERCURY, "Lib": P.VENUS, "Sco": P.MARS,
    "Sag": P.JUPITER, "Cap": P.SATURN, "Aqu": P.SATURN, "Pis": P.JUPITER,
}
EXALTATION = {
    "Ari": P.SUN, "Tau": P.MOON, "Can": P.JUPITER, "Vir": P.MERCURY,
    "Lib": P.SATURN, "Cap": P.MARS, "Pis": P.VENUS,
}
DETRIMENT = {
    "Ari": P.VENUS, "Tau": P.MARS, "Gem": P.JUPITER, "Can": P.SATURN,
    "Leo": P.SATURN, "Vir": P.JUPITER, "Lib": P.MARS, "Sco": P.VENUS,
    "Sag": P.MERCURY, "Cap": P.MOON, "Aqu": P.SUN, "Pis": P.MERCURY,
}
FALL = {"Ari": P.SATURN, "Can": P.MARS, "Lib": P.SUN, "Sco": P.MOON, "Cap": P.JUPITER, "Pis": P.MERCURY, "Vir": P.VENUS}

ELEMENT = {
    "Ari": "fire", "Leo": "fire", "Sag": "fire",
    "Tau": "earth", "Vir": "earth", "Cap": "earth",
    "Gem": "air", "Lib": "air", "Aqu": "air",
    "Can": "water", "Sco": "water", "Pis": "water",
}
TRIPLICITY = {
    "fire": {"day": P.SUN, "night": P.JUPITER},
    "earth": {"day": P.VENUS, "night": P.MOON},
    "air": {"day": P.SATURN, "night": P.MERCURY},
    "water": {"day": P.MARS, "night": P.MARS},
}

TERMS = {
    "Ari": ((6, P.JUPITER), (14, P.VENUS), (21, P.MERCURY), (26, P.MARS), (30, P.SATURN)),
    "Tau": ((8, P.VENUS), (15, P.MERCURY), (22, P.JUPITER), (26, P.SATURN), (30, P.MARS)),
    "Gem": ((7, P.MERCURY), (14, P.JUPITER), (21, P.VENUS), (25, P.SATURN), (30, P.MARS)),
    "Can": ((6, P.MARS), (13, P.JUPITER), (20, P.MERCURY), (27, P.VENUS), (30, P.SATURN)),
    "Leo": ((6, P.JUPITER), (13, P.VENUS), (19, P.SATURN), (25, P.MERCURY), (30, P.MARS)),
    "Vir": ((7, P.MERCURY), (13, P.VENUS), (18, P.JUPITER), (24, P.SATURN), (30, P.MARS)),
    "Lib": ((6, P.SATURN), (11, P.MERCURY), (19, P.JUPITER), (24, P.VENUS), (30, P.MARS)),
    "Sco": ((6, P.MARS), (14, P.JUPITER), (21, P.VENUS), (27, P.MERCURY), (30, P.SATURN)),
    "Sag": ((8, P.JUPITER), (14, P.VENUS), (19, P.MERCURY), (25, P.SATURN), (30, P.MARS)),
    "Cap": ((6, P.VENUS), (12, P.MERCURY), (19, P.JUPITER), (25, P.MARS), (30, P.SATURN)),
    "Aqu": ((6, P.SATURN), (12, P.MERCURY), (20, P.VENUS), (25, P.JUPITER), (30, P.MARS)),
    "Pis": ((8, P.VENUS), (14, P.JUPITER), (20, P.MERCURY), (26, P.MARS), (30, P.SATURN)),
}

FACES = {
    "Ari": (P.MARS, P.SUN, P.VENUS), "Tau": (P.MERCURY, P.MOON, P.SATURN),
    "Gem": (P.JUPITER, P.MARS, P.SUN), "Can": (P.VENUS, P.MERCURY, P.MOON),
    "Leo": (P.SATURN, P.JUPITER, P.MARS), "Vir": (P.SUN, P.VENUS, P.MERCURY),
    "Lib": (P.MOON, P.SATURN, P.JUPITER), "Sco": (P.MARS, P.SUN, P.VENUS),
    "Sag": (P.MERCURY, P.MOON, P.SATURN), "Cap": (P.JUPITER, P.MARS, P.SUN),
    "Aqu": (P.VENUS, P.MERCURY, P.MOON), "Pis": (P.SATURN, P.JUPITER, P.MARS),
}
