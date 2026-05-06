import random


class ErrorSimulator:

    def __init__(self, config: dict):
        self.noise_rate = config.get("noise_rate", 0.05)
        self.spike_rate = config.get("spike_rate", 0.01)
        self.drop_rate = config.get("drop_rate", 0.01)

    # ---------------------------
    # MAIN ENTRY
    # ---------------------------
    def inject(self, value: float) -> float:

        #  missing reading
        if random.random() < self.drop_rate:
            raise ValueError("Simulated missing reading")

        #  spike
        if random.random() < self.spike_rate:
            return value * random.uniform(3, 10)

        #  noise
        if random.random() < self.noise_rate:
            return value + random.uniform(-5, 5)

        return value