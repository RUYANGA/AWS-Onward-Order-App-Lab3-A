"""Price and delivery estimate for a parcel."""

from ..constants import MAX_WEIGHT_KG, PER_KG, SERVICES, ZONES
from ..exceptions import OrderError


def quote(zone, service, weight_kg):
    """Return the price and delivery time for a parcel.

    Args:
        zone: Key of ``ZONES`` (``local``, ``regional`` or ``national``).
        service: Key of ``SERVICES`` (``standard`` or ``express``).
        weight_kg: Parcel weight in kilograms, more than 0 and at most ``MAX_WEIGHT_KG``.

    Returns:
        A ``(price, delivery_days)`` tuple.

    Raises:
        OrderError: If the zone, service or weight is not valid.
    """
    if zone not in ZONES:
        raise OrderError(f"Choose a delivery zone: {', '.join(ZONES)}.")
    if service not in SERVICES:
        raise OrderError(f"Choose a service: {', '.join(SERVICES)}.")
    if not 0 < weight_kg <= MAX_WEIGHT_KG:
        raise OrderError(f"Weight must be more than 0 and at most {MAX_WEIGHT_KG:g} kg.")
    z, s = ZONES[zone], SERVICES[service]
    price = round((z["base"] + PER_KG * weight_kg) * s["multiplier"], 2)
    days = max(1, z["days"] - s["days_saved"])
    return price, days
