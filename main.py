import threading
import time
import json
import os
from src.utils.config import load_config
from ammeters.Greenlee_Ammeter import GreenleeAmmeter
from ammeters.Entes_Ammeter import EntesAmmeter
from ammeters.Circutor_Ammeter import CircutorAmmeter

from src.testing.test_framework import AmmeterTestFramework
from src.testing.orchestrator import Orchestrator

from src.config.constants import GREENLEE, ENTES, CIRCUTOR


# =========================================================
# LOAD CONFIG
# =========================================================
config = load_config("config/config.yaml")


# =========================================================
# START AMMETER EMULATORS
# =========================================================
def start_device(device_class, device_config):
    device = device_class(device_config)
    device.start_server()


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":

    print("Starting Ammeter Emulators...")

    mapping = {
        GREENLEE: GreenleeAmmeter,
        ENTES: EntesAmmeter,
        CIRCUTOR: CircutorAmmeter,
    }

    for name, cls in mapping.items():
        conf = config["ammeters"][name].copy()
        conf["simulation"] = config["simulation"]

        threading.Thread(
            target=start_device,
            args=(cls, conf),
            daemon=True
        ).start()

    time.sleep(2)
    print("Running pipeline...")
    framework = AmmeterTestFramework()
    orchestrator = Orchestrator(framework)
    output = orchestrator.run_and_export("results/results.json")
    print("Run completed:", output["run_id"])

    while True:
        time.sleep(1)