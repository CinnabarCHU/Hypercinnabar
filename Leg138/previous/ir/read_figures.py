"""Read selected ink in the original figure plates. Requires Pillow and the companion folder."""

import argparse
import csv
import gzip
import json
from pathlib import Path
from statistics import median

from PIL import Image

ROOT = Path(__file__).resolve().parent
# One point within each manually selected cross section of the solid ink stroke in Fig. 45.
PICKS = [(220,181),(250,201),(270,217),(300,241),(330,264),(360,288),(390,311),
         (420,327),(450,341),(480,356),(510,373),(530,386),(550,418),(565,443),
         (580,454),(600,468),(620,482),(640,491),(660,498)]


def read_fig45(plates):
    yield ["printed_page","y_px","x_left_px","x_right_px","composite_depth_graph_m","equivalent_log_depth_graph_m"]
    with Image.open(plates / "F45-1.png").convert("L") as image:
        pixel = image.load()
        for y, seed in PICKS:
            if pixel[seed, y] >= 145:
                raise ValueError(f"No dark stroke at {seed},{y}")
            left = right = seed
            while left > 0 and pixel[left-1, y] < 145:
                left -= 1
            while right+1 < image.width and pixel[right+1, y] < 145:
                right += 1
            v = (y - 78) / (727.5 - 78)
            x0 = 72.0 + (75.5-72.0)*v
            x350 = 503.5 + (508.0-503.5)*v
            depth = 350*((left+right)/2 - x0)/(x350-x0)
            yield ["317", str(y), str(left), str(right), f"{depth:.1f}", f"{350*v:.1f}"]


def read_fig07(plates):
    yield ["page","track","mcd_from_axis","y_px","median_x_px","min_x_px","max_x_px","estimate_from_print","unit"]
    with (ROOT / "metadata/location.csv").open(encoding="utf-8", newline="") as stream:
        origins = {int(row["printed_page"]): json.loads(row["pixel_rect"])[:2]
                   for row in csv.DictReader(stream) if row["item_id"] == "F07"}
    geometry = json.loads((ROOT/"data/figures/page-registration.json").read_text())["geometry"][3:]
    for panel, g in enumerate(geometry):
        page = 276 + panel
        crop_x, crop_y = origins[page]
        with Image.open(plates/f"F07-{panel+1}.png").convert("L") as image:
            pixel = image.load()
            for j, (track, unit) in enumerate([("GRAPE","g/cm3"), ("susceptibility","10^-5 SI")]):
                axis0, axis1 = g["ticks"][j]
                low, high = (1.5,1.9) if j == 0 else ((10,50) if page == 278 else (1,5))
                for y in range(int(g["y0"])+8, int(g["y1"])-6, 2):
                    # The top of the last susceptibility panel contains an annotation.
                    if page == 278 and j == 1 and y < 284:
                        continue
                    v = (y-g["y0"])/(g["y1"]-g["y0"])
                    drift = g["drift"]*v
                    a = g["rails"][j]+drift+7
                    b = g["rails"][j+1]+drift-4
                    dark = [x for x in range(int(a)+1, int(b)+1)
                            if x < b and pixel[x-crop_x,y-crop_y] < 156]
                    if not dark or dark[-1]-dark[0] > 45:
                        continue
                    x = median(dark)
                    depth = v*150 + panel*150
                    value = low+(x-axis0-drift)*(high-low)/(axis1-axis0)
                    yield [str(page),track,f"{depth:.4f}",str(y),f"{x:.1f}",str(dark[0]),
                           str(dark[-1]),f"{value:.5f}",unit]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plates", type=Path, help="plates directory from the companion ZIP")
    parser.add_argument("--export", type=Path, help="optional directory for uncompressed CSV output")
    args = parser.parse_args()
    for name, source, reader in (("fig07_ink","fig07_ink.csv.gz",read_fig07),
                                 ("fig45_ink","fig45_ink.csv",read_fig45)):
        rows = list(reader(args.plates))
        opener = gzip.open if source.endswith(".gz") else open
        with opener(ROOT/"data/figures"/source, "rt", encoding="utf-8", newline="") as stream:
            if rows != list(csv.reader(stream)):
                raise ValueError(f"Image readings disagree: {name}")
        if args.export:
            args.export.mkdir(parents=True, exist_ok=True)
            with (args.export/(name+".csv")).open("w", encoding="utf-8", newline="") as out:
                csv.writer(out, lineterminator="\n").writerows(rows)
        print(name, len(rows)-1, "image readings verified")


if __name__ == "__main__":
    main()
