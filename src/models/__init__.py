from dataclasses import dataclass, field
from typing import List


@dataclass
class SensorResult:
    samples: List[float] = field(default_factory=list)
    errors: int = 0
    count: int = 0