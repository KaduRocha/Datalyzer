# run.py
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR / "src"))

from src.core.engine import DataEngine




config = {
    "host": "localhost",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "123456"
}

engine = DataEngine(config)

profile = engine.run_schema_profile()

import json
print(json.dumps(profile, indent=2, default=str))