"""In-memory store of the orders booked on this container."""

import itertools
import math
import threading
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta

from ..constants import MAX_NAME_LENGTH, MAX_ORDERS_KEPT
from ..exceptions import OrderError
from .pricing import quote


def _now_iso():
    return datetime.now(UTC).isoformat(timespec="seconds")


@dataclass
class Order:
    """A booked delivery."""

    id: str
    merchant: str
    customer: str
    zone: str
    service: str
    weight_kg: float
    price: float
    estimated_delivery: str
    status: str = "received"
    created_at: str = field(default_factory=_now_iso)

    def to_dict(self):
        """Return the order as a JSON-serialisable dict."""
        return asdict(self)


class OrderBook:
    """Thread-safe, in-memory order store.

    Each container keeps its own list, which is enough to demonstrate the
    application. A production version would persist orders in a database (for
    example DynamoDB through a gateway VPC endpoint, so the no-internet rule holds).
    """

    def __init__(self):
        self._orders = []
        self._lock = threading.Lock()
        self._seq = itertools.count(1001)

    def create(self, merchant, customer, zone, service, weight_kg):
        """Validate, price and store a new order.

        Args:
            merchant: Name of the merchant sending the parcel.
            customer: Name of the customer receiving it.
            zone: Delivery zone key.
            service: Service key.
            weight_kg: Weight in kilograms, as a number or numeric string.

        Returns:
            The new ``Order``.

        Raises:
            OrderError: If any field is missing or invalid.
        """
        merchant, customer = (merchant or "").strip(), (customer or "").strip()
        if not merchant:
            raise OrderError("Enter the merchant name.")
        if not customer:
            raise OrderError("Enter the customer name.")
        try:
            weight = float(weight_kg)
        except (TypeError, ValueError):
            raise OrderError("Enter the parcel weight as a number of kilograms.") from None
        if not math.isfinite(weight):
            raise OrderError("Enter the parcel weight as a number of kilograms.")
        price, days = quote(zone, service, weight)
        eta = (datetime.now(UTC) + timedelta(days=days)).date().isoformat()
        with self._lock:
            order = Order(
                id=f"ONW-{next(self._seq)}",
                merchant=merchant[:MAX_NAME_LENGTH],
                customer=customer[:MAX_NAME_LENGTH],
                zone=zone,
                service=service,
                weight_kg=weight,
                price=price,
                estimated_delivery=eta,
            )
            self._orders.insert(0, order)
            del self._orders[MAX_ORDERS_KEPT:]
        return order

    def recent(self, limit=10):
        """Return the newest orders first.

        Args:
            limit: Maximum number of orders to return.

        Returns:
            A list of ``Order`` objects.
        """
        with self._lock:
            return list(self._orders[:limit])


#: One order book per worker process.
book = OrderBook()
