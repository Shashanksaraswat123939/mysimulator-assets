"""Eleven fictional teams (no real teams, sponsors or logos). Colours are linear RGB used directly as base colours."""

TEAMS = [
    dict(id="aurelia",   name="Aurelia GP",           short="AUR", a=(0.62, 0.03, 0.03), b=(0.92, 0.92, 0.90), c=(0.05, 0.05, 0.06), helmet=(0.9, 0.9, 0.9),  nums=(1, 11)),
    dict(id="vantor",    name="Vantor Racing",        short="VAN", a=(0.02, 0.07, 0.35), b=(0.9, 0.75, 0.05),  c=(0.9, 0.9, 0.92),   helmet=(0.9, 0.75, 0.05), nums=(3, 14)),
    dict(id="nova",      name="Nova Dynamics",        short="NOV", a=(0.55, 0.57, 0.6),  b=(0.0, 0.45, 0.42),  c=(0.04, 0.04, 0.05), helmet=(0.0, 0.45, 0.42), nums=(5, 16)),
    dict(id="helios",    name="Helios Motorsport",    short="HEL", a=(0.85, 0.28, 0.02), b=(0.03, 0.03, 0.035), c=(0.9, 0.9, 0.9),   helmet=(0.85, 0.28, 0.02), nums=(7, 18)),
    dict(id="kestrel",   name="Kestrel Works",        short="KES", a=(0.0, 0.2, 0.09),   b=(0.75, 0.6, 0.15),  c=(0.9, 0.9, 0.88),   helmet=(0.75, 0.6, 0.15), nums=(9, 20)),
    dict(id="obsidian",  name="Obsidian Team",        short="OBS", a=(0.015, 0.015, 0.02), b=(0.2, 0.9, 0.1),  c=(0.7, 0.7, 0.72),   helmet=(0.2, 0.9, 0.1),  nums=(21, 22)),
    dict(id="tidewater", name="Tidewater Racing",     short="TID", a=(0.3, 0.6, 0.85),   b=(0.92, 0.92, 0.95), c=(0.02, 0.1, 0.3),   helmet=(0.3, 0.6, 0.85), nums=(23, 24)),
    dict(id="solstice",  name="Solstice GP",          short="SOL", a=(0.32, 0.08, 0.5),  b=(0.9, 0.35, 0.6),   c=(0.92, 0.92, 0.95), helmet=(0.9, 0.35, 0.6), nums=(27, 31)),
    dict(id="ironclad",  name="Ironclad Engineering", short="IRN", a=(0.1, 0.11, 0.13),  b=(0.7, 0.05, 0.05),  c=(0.75, 0.75, 0.78), helmet=(0.7, 0.05, 0.05), nums=(33, 34)),
    dict(id="meridian",  name="Meridian Racing",      short="MER", a=(0.9, 0.9, 0.92),   b=(0.02, 0.05, 0.3),  c=(0.8, 0.05, 0.05),  helmet=(0.02, 0.05, 0.3), nums=(40, 41)),
    dict(id="pinnacle",  name="Pinnacle Performance", short="PIN", a=(0.7, 0.04, 0.35),  b=(0.02, 0.02, 0.025), c=(0.9, 0.9, 0.9),  helmet=(0.7, 0.04, 0.35), nums=(44, 55)),
]

COMPOUNDS = {
    "soft": (0.85, 0.02, 0.02),
    "medium": (0.9, 0.7, 0.02),
    "hard": (0.9, 0.9, 0.9),
    "inter": (0.02, 0.6, 0.1),
    "wet": (0.02, 0.2, 0.85),
}
