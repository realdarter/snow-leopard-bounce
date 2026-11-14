import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path


source = Path(__file__).resolve().parents[1] / "snow_leopard_bounce.pyw"
loader = SourceFileLoader("snow_leopard_bounce", str(source))
spec = importlib.util.spec_from_loader(loader.name, loader)
cats = importlib.util.module_from_spec(spec)
loader.exec_module(cats)

app = cats.BounceApp(2, 0, True)
result = {}


def minimize():
    result["before"] = [(sprite["x"], sprite["y"]) for sprite in app.sprites]
    app.root.iconify()
    app.root.after(700, check)


def check():
    result["main_minimized"] = app.root.state() == "iconic"
    result["cats_visible"] = all(sprite["window"].winfo_viewable() for sprite in app.sprites)
    result["cats_moved"] = result["before"] != [(sprite["x"], sprite["y"]) for sprite in app.sprites]
    app.close()


app.root.after(600, minimize)
app.root.after(4000, app.close)
app.run()
if not all(result.get(key) for key in ("main_minimized", "cats_visible", "cats_moved")):
    raise SystemExit(f"Linux minimize check failed: {result}")
print("Linux minimize check passed")
