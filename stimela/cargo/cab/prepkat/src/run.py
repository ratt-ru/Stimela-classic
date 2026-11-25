import os
from pathlib import Path

import yaml
from prepkat.feed_flip import _feed_flip


if __name__ == "__main__":
    with open(os.environ["CONFIG"], "r") as config_file:
        cab = yaml.safe_load(config_file)

    parameters = {
        parameter["name"]: parameter["value"] for parameter in cab["parameters"]
    }
    _feed_flip(
        Path(parameters["ms_path"]),
        parameters.get("columns") or ["DATA", "WEIGHT_SPECTRUM", "FLAG"],
    )