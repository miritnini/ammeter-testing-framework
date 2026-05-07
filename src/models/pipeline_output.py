from dataclasses import dataclass
from typing import List, Dict

from src.models.ammeter_result import AmmeterResult


@dataclass
class PipelineOutput:
    run_id: str
    timestamp: str

    results: List[AmmeterResult]

    most_reliable: str
    ranking: Dict[str, float]