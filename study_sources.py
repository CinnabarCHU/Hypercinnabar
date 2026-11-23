"""Cross-check the field identities and reference chronologies of the historical studies."""
import csv
from collections import defaultdict

import numpy as np

from records import ROOT, catalog, record_array, source_bytes


def archive_table(asset):
    raw = source_bytes(catalog("assets")[asset]).decode().split("*/", 1)[1].strip()
    return list(csv.reader(raw.splitlines(), delimiter="\t"))


def verify_classic_sources(tasks):
    for task in tasks.values():
        if "reference_record" in task:
            clock = np.loadtxt(ROOT / task["reference_file"], delimiter=",", skiprows=1)
            archived = record_array(task["reference_record"])
            if not np.array_equal(archived, clock[:, 1:]):
                raise ValueError(f"Published age-depth rows disagree with {task['reference_record']}")

    t3, t5, t7 = (archive_table(key) for key in ("846table3", "846table", "846table7"))
    if not ("δ13C" in t5[0][3] and "δ18O" in t5[0][4] and
            "δ18O" in t7[0][1] and "δ13C" in t7[0][2] and
            "δ18O" in t3[0][8] and "δ13C" in t3[0][9]):
        raise ValueError("Site 846 archive field names have changed")
    # Table 3 reports revised depth to 0.001 m, Table 5 to 0.01 m.
    adjusted = defaultdict(list)
    for row in t3[1:]:
        if all(row[i] for i in (2, 4, 8, 9)):
            adjusted[tuple(float(row[i]) for i in (2, 8, 9))].append(float(row[4]))
    interpolated = {tuple(map(float, row[:3])) for row in t7[1:] if all(row[:3])}
    paired = [row for row in t5[1:] if row[3] and row[4] and 63.43 <= float(row[2]) <= 96]
    matches_depth = matches_age = reversed_age = 0
    for row in paired:
        depth, age, composite, oxygen, carbon = map(float, row[:5])
        matches_depth += any(abs(d-composite) <= .005001 for d in adjusted[depth, oxygen, carbon])
        matches_age += (age, oxygen, carbon) in interpolated
        reversed_age += (age, carbon, oxygen) in interpolated
    if len(paired) != 319 or matches_depth < 100 or matches_age != 25 or reversed_age != 0:
        raise ValueError("Independent Site 846 tables do not support the registered isotope order")
    print(f"Site 846 isotope check: {matches_depth} adjusted Table 3 pairs and {matches_age} exact "
          f"Table 7 pairs agree with printed Table 5; {reversed_age} Table 7 pairs agree after reversal.")
