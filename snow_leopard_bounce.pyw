import argparse
import ctypes
import math
import os
import random
import sys
import time
import tkinter as tk
from ctypes import wintypes
from ctypes.util import find_library
from pathlib import Path

if sys.platform == "win32":
    import winsound


def asset(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name


def enable_dpi_awareness() -> None:
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass


def song_next_to_app() -> Path:
    folder = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    return folder / "song.mp3"


def make_click_through_windows(window: tk.Toplevel) -> None:
    window.update_idletasks()
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.GetAncestor.argtypes = (wintypes.HWND, wintypes.UINT)
    user32.GetAncestor.restype = wintypes.HWND
    user32.GetWindowLongPtrW.argtypes = (wintypes.HWND, ctypes.c_int)
    user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
    user32.SetWindowLongPtrW.argtypes = (wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t)
    user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
    user32.SetLayeredWindowAttributes.argtypes = (wintypes.HWND, wintypes.COLORREF, wintypes.BYTE, wintypes.DWORD)
    user32.SetLayeredWindowAttributes.restype = wintypes.BOOL
    user32.SetWindowPos.argtypes = (wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT)
    user32.SetWindowPos.restype = wintypes.BOOL

    hwnd = user32.GetAncestor(window.winfo_id(), 2)
    if not hwnd:
        raise ctypes.WinError(ctypes.get_last_error())
    style = user32.GetWindowLongPtrW(hwnd, -20)
    ctypes.set_last_error(0)
    previous = user32.SetWindowLongPtrW(hwnd, -20, style | 0x00080020)
    if not previous and ctypes.get_last_error():
        raise ctypes.WinError(ctypes.get_last_error())
    if not user32.SetLayeredWindowAttributes(hwnd, 0, 255, 2):
        raise ctypes.WinError(ctypes.get_last_error())
    if not user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 0x37):
        raise ctypes.WinError(ctypes.get_last_error())


class LinuxClickThrough:
    def __init__(self, controls_window: int) -> None:
        self.controls_window = controls_window
        self.x11 = ctypes.CDLL(find_library("X11") or "libX11.so.6")
        self.xext = ctypes.CDLL(find_library("Xext") or "libXext.so.6")
        self.x11.XOpenDisplay.argtypes = (ctypes.c_char_p,)
        self.x11.XOpenDisplay.restype = ctypes.c_void_p
        self.x11.XSync.argtypes = (ctypes.c_void_p, ctypes.c_int)
        self.x11.XCloseDisplay.argtypes = (ctypes.c_void_p,)
        self.x11.XQueryTree.argtypes = (ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.POINTER(ctypes.c_ulong)), ctypes.POINTER(ctypes.c_uint))
        self.x11.XQueryTree.restype = ctypes.c_int
        self.x11.XFree.argtypes = (ctypes.c_void_p,)
        self.xext.XShapeQueryExtension.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        self.xext.XShapeQueryExtension.restype = ctypes.c_int
        self.xext.XShapeCombineRectangles.argtypes = (ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int)
        self.display = self.x11.XOpenDisplay(None)
        if not self.display:
            raise RuntimeError("An X11 or XWayland desktop is needed to show the cats.")
        event, error = ctypes.c_int(), ctypes.c_int()
        if not self.xext.XShapeQueryExtension(self.display, ctypes.byref(event), ctypes.byref(error)):
            self.close()
            raise RuntimeError("This desktop does not support click-through cat windows.")

    def apply(self, window: tk.Toplevel) -> None:
        window.update_idletasks()
        cat_window = window.winfo_id()
        windows = [cat_window]
        seen = set()
        while windows:
            x_window = windows.pop()
            if x_window in seen:
                continue
            seen.add(x_window)
            self.xext.XShapeCombineRectangles(self.display, x_window, 2, 0, 0, None, 0, 0, 0)
            root, parent = ctypes.c_ulong(), ctypes.c_ulong()
            children = ctypes.POINTER(ctypes.c_ulong)()
            count = ctypes.c_uint()
            if self.x11.XQueryTree(self.display, x_window, ctypes.byref(root), ctypes.byref(parent), ctypes.byref(children), ctypes.byref(count)):
                windows.extend(children[i] for i in range(count.value))
                if x_window == cat_window and parent.value not in (0, root.value, self.controls_window):
                    windows.append(parent.value)
                if children:
                    self.x11.XFree(children)
        self.x11.XSync(self.display, 0)

    def close(self) -> None:
        if self.display:
            self.x11.XCloseDisplay(self.display)
            self.display = None


class WindowsMusicPlayer:
    def __init__(self) -> None:
        self.send = ctypes.windll.winmm.mciSendStringW
        self.send.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p]
        self.send.restype = ctypes.c_uint
        self.opened = False
        self.wav_playing = False

    def play(self) -> bool:
        self.close()
        song = song_next_to_app()
        if song.is_file() and self.play_mp3(song):
            return True
        bundled_song = asset("Blue-Skies.mp3")
        if bundled_song.is_file() and self.play_mp3(bundled_song):
            return True
        try:
            winsound.PlaySound(
                str(asset("cat-tune.wav")),
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP,
            )
            self.wav_playing = True
            return True
        except RuntimeError:
            return False

    def play_mp3(self, song: Path) -> bool:
        if self.send(f'open "{song}" type mpegvideo alias snowcatmusic', None, 0, None):
            return False
        self.opened = True
        if self.send("play snowcatmusic repeat", None, 0, None):
            self.close()
            return False
        return True

    def close(self) -> None:
        if self.opened:
            self.send("close snowcatmusic", None, 0, None)
            self.opened = False
        if self.wav_playing:
            winsound.PlaySound(None, 0)
            self.wav_playing = False


class LinuxMusicPlayer:
    def __init__(self) -> None:
        os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
        import pygame
        self.pygame = pygame

    def play(self) -> bool:
        self.close()
        try:
            self.pygame.mixer.init()
        except self.pygame.error:
            return False
        for song in (song_next_to_app(), asset("Blue-Skies.mp3"), asset("cat-tune.wav")):
            if song.is_file():
                try:
                    self.pygame.mixer.music.load(str(song))
                    self.pygame.mixer.music.play(-1)
                    return True
                except self.pygame.error:
                    pass
        self.close()
        return False

    def close(self) -> None:
        if self.pygame.mixer.get_init():
            self.pygame.mixer.music.stop()
            self.pygame.mixer.music.unload()
            self.pygame.mixer.quit()


class BounceApp:
    def __init__(self, count: int, duration: float, no_music: bool) -> None:
        self.root = tk.Tk()
        self.root.title("Snow Leopard Bounce")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)
        x = max(0, (self.root.winfo_screenwidth() - 390) // 2)
        y = max(0, (self.root.winfo_screenheight() - 390) // 2)
        self.root.geometry(f"390x390+{x}+{y}")
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind("<Escape>", lambda _event: self.close())

        self.no_music = no_music
        self.running = True
        self.music_on = False
        self.music = WindowsMusicPlayer() if sys.platform == "win32" else LinuxMusicPlayer()
        self.click_through = None if sys.platform == "win32" else LinuxClickThrough(self.root.winfo_id())
        self.timer_id = None
        self.last_frame = time.monotonic()
        self.sprites = []
        self.started = False
        self.rng = random.SystemRandom()
        self.average_speed = tk.IntVar(value=125)
        self.target_count = tk.IntVar(value=count)
        self.small_image = tk.PhotoImage(file=str(asset("cat-small.png")))
        self.large_image = tk.PhotoImage(file=str(asset("cat-large.png")))
        if sys.platform == "win32":
            self.root.iconbitmap(str(asset("cat.ico")))
        else:
            self.root.iconphoto(True, self.small_image)

        tk.Label(self.root, text="i am pawing your computer", font=("Segoe UI", 16, "bold")).pack(pady=(12, 5))
        tk.Label(self.root, image=self.large_image).pack()
        self.count_label = tk.Label(
            self.root,
            text=f"cats: {count}",
            font=("Segoe UI", 10),
        )
        self.count_label.pack(pady=(7, 0))
        tk.Scale(
            self.root,
            from_=0,
            to=100,
            resolution=1,
            variable=self.target_count,
            command=self.update_count,
            orient="horizontal",
            length=270,
            showvalue=False,
        ).pack()

        self.speed_label = tk.Label(
            self.root,
            text="speed: 125",
            font=("Segoe UI", 10),
        )
        self.speed_label.pack()
        tk.Scale(
            self.root,
            from_=60,
            to=220,
            resolution=5,
            variable=self.average_speed,
            command=self.update_speed_label,
            orient="horizontal",
            length=270,
            showvalue=False,
        ).pack()

        buttons = tk.Frame(self.root)
        buttons.pack(pady=(5, 0))
        self.music_button = tk.Button(
            buttons,
            text="mute",
            command=self.toggle_music,
            width=11,
        )
        self.music_button.pack(side="left", padx=4)
        tk.Button(
            buttons,
            text="stop cats",
            command=self.close,
            width=11,
        ).pack(side="left", padx=4)

        if self.no_music:
            self.music_button.configure(state="disabled", text="no music")
        self.root.after(150, self.start)
        if duration > 0:
            self.root.after(round(duration * 1000), self.close)

    def start(self) -> None:
        if not self.running:
            return
        self.started = True
        self.sync_count()
        if not self.no_music:
            self.play_music()
        self.last_frame = time.monotonic()
        self.move()

    def create_sprite(self) -> None:
        size = self.small_image.width()
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        x = float(self.rng.randrange(max(1, width - size + 1)))
        y = float(self.rng.randrange(max(1, height - size + 1)))
        angle = self.rng.uniform(0, 2 * math.pi)
        window = tk.Toplevel(self.root)
        window.overrideredirect(True)
        window.attributes("-topmost", True)
        window.geometry(f"{size}x{size}+{round(x)}+{round(y)}")
        tk.Label(window, image=self.small_image, borderwidth=0, highlightthickness=0).pack()
        if self.click_through:
            self.click_through.apply(window)
        else:
            make_click_through_windows(window)
        self.sprites.append({
            "window": window,
            "x": x,
            "y": y,
            "dx": math.cos(angle),
            "dy": math.sin(angle),
            "speed_factor": self.rng.uniform(0.85, 1.15),
            "last_bounce": -100.0,
        })

    def sync_count(self) -> None:
        target = self.target_count.get()
        while len(self.sprites) < target:
            self.create_sprite()
        while len(self.sprites) > target:
            self.sprites.pop()["window"].destroy()
        self.raise_controls()

    def move(self) -> None:
        if not self.running:
            return
        now = time.monotonic()
        elapsed = min(now - self.last_frame, 0.05)
        self.last_frame = now
        size = self.small_image.width()
        max_x = max(0, self.root.winfo_screenwidth() - size)
        max_y = max(0, self.root.winfo_screenheight() - size)
        for sprite in self.sprites:
            age = now - sprite["last_bounce"]
            pulse = 0.0 if age > 2.0 else (age / 0.22) * math.exp(1 - age / 0.22)
            speed = self.average_speed.get() * sprite["speed_factor"] * (1 + 0.95 * pulse)
            x = sprite["x"] + sprite["dx"] * speed * elapsed
            y = sprite["y"] + sprite["dy"] * speed * elapsed
            bounced = False
            if x < 0 or x > max_x:
                x = min(max(x, 0), max_x)
                sprite["dx"] = -sprite["dx"]
                bounced = True
            if y < 0 or y > max_y:
                y = min(max(y, 0), max_y)
                sprite["dy"] = -sprite["dy"]
                bounced = True
            if bounced:
                sprite["last_bounce"] = now
            sprite["x"], sprite["y"] = x, y
            sprite["window"].geometry(f"+{round(x)}+{round(y)}")
        self.timer_id = self.root.after(33, self.move)

    def raise_controls(self) -> None:
        if self.root.state() == "normal":
            self.root.lift()

    def update_speed_label(self, _value: str) -> None:
        self.speed_label.configure(text=f"speed: {self.average_speed.get()}")

    def update_count(self, _value: str) -> None:
        self.count_label.configure(text=f"cats: {self.target_count.get()}")
        if self.started:
            self.sync_count()

    def play_music(self) -> None:
        if self.music.play():
            self.music_on = True
            self.music_button.configure(text="mute")
        else:
            self.music_button.configure(text="no music", state="disabled")

    def toggle_music(self) -> None:
        if self.music_on:
            self.music.close()
            self.music_on = False
            self.music_button.configure(text="unmute")
        else:
            self.play_music()

    def close(self) -> None:
        if not self.running:
            return
        self.running = False
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
        if self.music_on:
            self.music.close()
        for sprite in self.sprites:
            sprite["window"].destroy()
        self.sprites.clear()
        if self.click_through:
            self.click_through.close()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--duration", type=float, default=0, help="Auto close after this many seconds")
    parser.add_argument("--no-music", action="store_true")
    args = parser.parse_args()
    if sys.platform not in ("win32", "linux"):
        parser.error("Snow Leopard Bounce runs on Windows or Linux.")
    enable_dpi_awareness()
    BounceApp(max(0, min(100, args.count)), args.duration, args.no_music).run()
