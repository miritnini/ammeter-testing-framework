# src/models/ammeter_result.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from src.models.sensor_model import SensorResult
from src.models.statistics_model import Statistics


@dataclass
class AmmeterResult:
    ammeter: str
    sensor: SensorResult
    expected_freq: float
    actual_freq: float
    statistics: Statistics
    test_passed: bool
    failures: List[str]
    raw_result: Optional[Dict[str, Any]]


@dataclass
class NormalizedAmmeterResult:
    ammeter: str
    samples: List[float] = field(default_factory=list)
    count: int = 0
    errors: int = 0
    expected_freq: float = 0.0
    actual_freq: float = 0.0
    mean: float = 0.0
    median: float = 0.0
    std: float = 0.0
    min: float = 0.0
    max: float = 0.0
    test_passed: bool = False
    failures: List[str] = field(default_factory=list)
    raw_result: Optional[Any] = None
    statistics: Optional[Statistics] = None