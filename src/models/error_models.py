from dataclasses import dataclass

@dataclass
class ErrorSimulatorConfig:
    enabled: bool = False
    noise_rate: float = 0.05
    spike_rate: float = 0.01
    drop_rate: float = 0.01

@dataclass
class ErrorEvent:
    value: float
    error_type: str

@dataclass
class ErrorEntry:
    error_type: str
    message: str
    context: str
    severity: str