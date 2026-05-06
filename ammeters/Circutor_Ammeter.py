from ammeters.base_ammeter import AmmeterEmulatorBase
from src.utils.Utils import generate_random_float

from src.config.constants import (
    SIMULATION,
    NUM_SAMPLES,
    TIME_STEP_MIN,
    TIME_STEP_MAX,
    VOLTAGE_MIN,
    VOLTAGE_MAX,
)


class CircutorAmmeter(AmmeterEmulatorBase):

    def __init__(self, config: dict):
        super().__init__(config["port"])
        self.command = config["command"].encode()
        self.sim = config[SIMULATION]

    @property
    def get_current_command(self) -> bytes:
        return self.command

    def measure_current(self) -> float:
        num_samples = self.sim[NUM_SAMPLES]

        time_step = generate_random_float(
            self.sim[TIME_STEP_MIN],
            self.sim[TIME_STEP_MAX]
        )

        voltages = [
            generate_random_float(
                self.sim[VOLTAGE_MIN],
                self.sim[VOLTAGE_MAX]
            )
            for _ in range(num_samples)
        ]

        print(f"CIRCUTOR Ammeter - Voltages: {voltages}, Time Step: {time_step}s")

        current = sum(v * time_step for v in voltages)

        print(f"Current: {current}A")

        return current