from ammeters.base_ammeter import AmmeterEmulatorBase
from src.utils.Utils import generate_random_float

from src.config.constants import (
    VOLTAGE_MIN,
    VOLTAGE_MAX,
    RESISTANCE_MIN,
    RESISTANCE_MAX,
    PORT,
    SIMULATION,
)


class GreenleeAmmeter(AmmeterEmulatorBase):

    def __init__(self, config: dict):
        super().__init__(config[PORT])
        self.command = config["command"].encode()
        self.sim = config[SIMULATION]

    @property
    def get_current_command(self) -> bytes:
        return self.command

    def measure_current(self) -> float:

        voltage = generate_random_float(
            self.sim[VOLTAGE_MIN],
            self.sim[VOLTAGE_MAX]
        )

        resistance = generate_random_float(
            self.sim[RESISTANCE_MIN],
            self.sim[RESISTANCE_MAX]
        )

        current = voltage / resistance

        print(
            f"Greenlee Ammeter - Voltage: {voltage}V, "
            f"Resistance: {resistance}Ω, "
            f"Current: {current}A"
        )

        return current