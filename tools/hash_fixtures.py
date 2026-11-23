"""Print SHA-256 entries for a deliberate reference-data revision."""
import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
files=sorted(f for dirname in ("catalog","fixtures","suites/archived") for f in (root/dirname).rglob("*")
             if f.is_file() and f.name!="checksums.json" and "__pycache__" not in f.parts)
print(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
