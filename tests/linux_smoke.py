import importlib.util
import subprocess
import tkinter as tk
from importlib.machinery import SourceFileLoader
from pathlib import Path


source = Path(__file__).resolve().parents[1] / "snow_leopard_bounce.pyw"
loader = SourceFileLoader("snow_leopard_bounce", str(source))
spec = importlib.util.spec_from_loader(loader.name, loader)
cats = importlib.util.module_from_spec(spec)
loader.exec_module(cats)

app = cats.BounceApp(0, 0, False)
clicked = []
result = {}
target = tk.Toplevel(app.root)
target.geometry("240x180+40+40")
tk.Button(target, text="click under the cat", command=lambda: clicked.append(True)).pack(fill="both", expand=True)


def place_cat():
    result["baseline"] = bool(clicked)
    clicked.clear()
    app.target_count.set(1)
    app.sync_count()
    sprite = app.sprites[0]
    sprite["x"], sprite["y"] = 90.0, 70.0
    sprite["dx"], sprite["dy"] = 0.0, 0.0
    sprite["window"].geometry("+90+70")
    sprite["window"].lift()
    app.root.after(100, click)


def click():
    subprocess.run(["xdotool", "mousemove", "130", "110", "click", "1"], check=True)
    app.root.after(300, finish)


def finish():
    result["clicked"] = bool(clicked)
    result["music"] = app.music_on
    app.close()


app.root.after(300, lambda: subprocess.run(["xdotool", "mousemove", "130", "110", "click", "1"], check=True))
app.root.after(500, place_cat)
app.root.after(4000, app.close)
app.run()
if result != {"baseline": True, "clicked": True, "music": True}:
    raise SystemExit(f"Linux desktop check failed: {result}")
print("Linux click-through and music check passed")
