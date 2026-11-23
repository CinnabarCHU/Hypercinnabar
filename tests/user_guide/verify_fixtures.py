"""Check the guide and data against the acceptance manifest; standard library only."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[2]
manifest = json.loads((Path(__file__).with_name('manifest.json')).read_text())
for name, expected in manifest['files'].items():
    data = (root / 'upstream' / 'acycle' / name).read_bytes()
    assert len(data) == expected['bytes'], name
    assert hashlib.sha256(data).hexdigest() == expected['sha256'], name
print(f"Verified {len(manifest['files'])} pinned guide/data files.")
