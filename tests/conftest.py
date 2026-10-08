import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def root():
    return ROOT


@pytest.fixture(scope="session")
def results():
    names = {"explore": "01_explore", "discovery": "02_discovery", "conformance": "03_conformance",
             "performance": "04_performance", "recommendations": "05_recommendations",
             "bpi2019": "06_bpi2019"}
    return {k: json.loads((ROOT / "results" / f"{v}.json").read_text(encoding="utf-8")) for k, v in names.items()}
