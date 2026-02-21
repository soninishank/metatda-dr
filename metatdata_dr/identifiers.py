import threading
import uuid
from dataclasses import dataclass
from typing import Optional


class AtomicCounter:
    """
    Thread-safe monotonic logical clock.

    The ``increment()`` method is fully atomic. The ``value`` property
    provides a best-effort snapshot read and is NOT guaranteed to be
    consistent under concurrent modification; use it only for
    informational/logging purposes.
    """

    def __init__(self, initial: int = 0):
        self._value = initial
        self._lock = threading.Lock()

    def increment(self) -> int:
        with self._lock:
            self._value += 1
            return self._value

    @property
    def value(self) -> int:
        """Best-effort snapshot read (not lock-protected)."""
        return self._value


@dataclass(frozen=True)
class CompositeID:
    """
    Composite identifier with format: NID:LCV[:NST]

    Attributes:
        nid: Node Identifier — 128-bit UUID string assigned at node creation.
        lcv: Logical Clock Value — monotonically increasing integer per node.
        nst: Namespace Tag — optional string for multi-tenant or sharded nodes.
    """
    nid: str
    lcv: int
    nst: Optional[str] = None

    def __str__(self) -> str:
        if self.nst:
            return f"{self.nid}:{self.lcv}:{self.nst}"
        return f"{self.nid}:{self.lcv}"

    @property
    def key(self) -> str:
        """String representation used as dict key in the metadata index."""
        return str(self)


def generate_nid() -> str:
    """
    Generate a 128-bit UUID-based Node Identifier.

    Returns:
        A UUID4 string (e.g. '550e8400-e29b-41d4-a716-446655440000').
    """
    return str(uuid.uuid4())