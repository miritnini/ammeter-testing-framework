import random
from src.models.error_models import ErrorSimulatorConfig

class ErrorSimulator:

    def __init__(self, config: ErrorSimulatorConfig):
        self.enabled = config.enabled
        self.noise_rate = config.noise_rate
        self.spike_rate = config.spike_rate
        self.drop_rate = config.drop_rate

    def inject(self, value: float) -> float:
        if not self.enabled:
            return value

        if random.random() < self.drop_rate:
            raise ValueError("Simulated missing reading")

        if random.random() < self.spike_rate:
            return value * random.uniform(3, 10)

        if random.random() < self.noise_rate:
            return value + random.uniform(-5, 5)

        return value