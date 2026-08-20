from pathlib import Path

import ee
from dotenv import dotenv_values

ROOT_DIR = Path(__file__).parent.parent
config = dotenv_values(ROOT_DIR / ".env")
PROJECT_ID = config["GEE_PROJECT_ID"]


def initialize_ee() -> None:
    try:
        ee.Initialize(project=PROJECT_ID)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=PROJECT_ID)


if __name__ == "__main__":
    initialize_ee()
    print("Earth Engine OK:", ee.Number(1).getInfo())
