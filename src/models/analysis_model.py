from dataclasses import dataclass

@dataclass
class AmmeterAnalysisResult:
    ammeter: str
    mean: float
    std: float
    min: float
    max: float
    count: int
    errors: int
    cv: float
    error_rate: float
    accuracy_score: float