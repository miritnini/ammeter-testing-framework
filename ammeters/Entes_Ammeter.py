from ammeters.base_ammeter import AmmeterEmulatorBase
from src.utils.Utils import generate_random_float

from src.config.constants import (
    MAGNETIC_FIELD_MIN,
    MAGNETIC_FIELD_MAX,
    CALIBRATION_MIN,
    CALIBRATION_MAX,
)


class EntesAmmeter(AmmeterEmulatorBase):

    def __init__(self, config: dict):
        super().__init__(config["port"])
        self.command = config["command"].encode()
        self.sim = config["simulation"]

    @property
    def get_current_command(self) -> bytes:
        return self.command

    def measure_current(self) -> float:

        magnetic_field = generate_random_float(
            self.sim[MAGNETIC_FIELD_MIN],
            self.sim[MAGNETIC_FIELD_MAX]
        )

        calibration_factor = generate_random_float(
            self.sim[CALIBRATION_MIN],
            self.sim[CALIBRATION_MAX]
        )

        current = magnetic_field * calibration_factor

        print(
            f"ENTES Ammeter - Magnetic Field: {magnetic_field}T, "
            f"Calibration Factor: {calibration_factor}, "
            f"Current: {current}A"
        )

        return current