"""Capture the actual MATLAB X11 client, including the menu bar and toolbar."""
import os
import re
import subprocess
import sys
import time

from PIL import ImageGrab


def xwininfo(*args):
    return subprocess.check_output(["xwininfo", *args], text=True)


def geometry(window):
    info = xwininfo("-id", window)
    fields = ("Absolute upper-left X", "Absolute upper-left Y", "Width", "Height")
    values = [int(re.search(rf"^\s*{key}:\s*(-?\d+)", info, re.M)[1]) for key in fields]
    return values if "Map State: IsViewable" in info else None


def main():
    title = os.environ["ACYCLE_CAPTURE_TITLE"]
    for _ in range(60):
        tree = xwininfo("-root", "-tree")
        named = re.findall(r'^\s*(0x[0-9a-fA-F]+) "([^"]*)"', tree, re.M)
        matches = [geometry(window) for window, name in named if title and title in name]
        frames = [rect for rect in matches if rect and rect[2] > 100 and rect[3] > 100]
        if frames:
            break
        time.sleep(.15)
    else:
        raise RuntimeError(f"No visible window for {title!r}. X11 titles: {[name for _,name in named]}")
    x, y, width, height = max(frames, key=lambda rect: rect[2] * rect[3])
    if sys.argv[1:] == ["--click-center"]:
        subprocess.run(["xdotool","mousemove",str(x + width // 2),str(y + height // 2),"click","1"],check=True)
        return
    screen = ImageGrab.grab(xdisplay=os.environ["DISPLAY"])
    box = (max(0, x), max(0, y), min(screen.width, x + width), min(screen.height, y + height))
    print(f"X11 window {title!r} at {(x, y, width, height)}, screen {screen.size}, visible box {box}")
    screen.crop(box).save(os.environ["ACYCLE_CAPTURE_PNG"])
    if box != (x, y, x + width, y + height):
        raise RuntimeError("The window is clipped by the screen.")


if __name__ == "__main__":
    main()
