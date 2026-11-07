"""Create square cat images, a Windows icon, and an original looping tune."""

from pathlib import Path

from PIL import Image


HERE = Path(__file__).resolve().parent
photo = Image.open(HERE / "cat-source.jpg").convert("RGB")
side = min(photo.size)
# Keep the ears and most of the raised paw in a square crop.
left = (photo.width - side) // 2
top = min(max(0, round(photo.height * 0.075)), photo.height - side)
square = photo.crop((left, top, left + side, top + side))
square.resize((256, 256), Image.Resampling.LANCZOS).save(HERE / "cat.png")
square.resize((104, 104), Image.Resampling.LANCZOS).save(HERE / "cat-small.png")
square.resize((168, 168), Image.Resampling.LANCZOS).save(HERE / "cat-large.png")
square.save(HERE / "cat.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("Created square images and icon.")
