"""Delivery zones, services and pricing rules for Onward Logistics."""

ZONES = {
    "local": {"label": "Same city", "base": 4.00, "days": 1},
    "regional": {"label": "Same region", "base": 7.50, "days": 2},
    "national": {"label": "Anywhere in the country", "base": 12.00, "days": 4},
}
SERVICES = {
    "standard": {"label": "Standard", "multiplier": 1.0, "days_saved": 0},
    "express": {"label": "Express", "multiplier": 1.6, "days_saved": 1},
}
PER_KG = 1.20
MAX_WEIGHT_KG = 50.0
MAX_NAME_LENGTH = 80
#: Orders kept per container; older ones are dropped.
MAX_ORDERS_KEPT = 200
