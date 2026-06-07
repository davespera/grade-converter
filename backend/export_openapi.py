import json
import os
import sys

# Set before importing main: instantiating the app builds the DB engine, which
# requires a parseable DATABASE_URL even though no connection is ever opened.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")

from backend.main import app

out_path = sys.argv[1] if len(sys.argv) > 1 else "frontend/.openapi.json"
with open(out_path, "w") as f:
    json.dump(app.openapi(), f)
