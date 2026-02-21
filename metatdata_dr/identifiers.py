import threading
import uuid
from dataclasses import dataclass
from typing import Optional


class AtomicCounter:
    """
    Thread-safe monotonic logical clock.
    """

    def __init__(self, initial: int = 0):
        self._value = initial
        self._lock = threading.Lock()

    def increment(self) -> int:
        with self._lock:
            self._value += 1
            return self._value

    @property
    def value(self):
        return self._value


@dataclass(frozen=True)
class CompositeID:
    """
    Composite identifier: NID:LCV[:NST]
    """
    nid: str
    lcv: int
    nst: Optional[str] = None

    def __str__(self):
        if self.nst:
            return f"{self.nid}:{self.lcv}:{self.nst}"
        return f"{self.nid}:{self.lcv}"

    @property
    def key(self):
        return str(self)


def generate_nid() -> str:
    """
    Generate 128-bit UUID-based Node Identifier.
    """
    return str(uuid.uuid4())