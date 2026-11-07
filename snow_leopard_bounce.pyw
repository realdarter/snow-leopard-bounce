"""Snow Leopard Bounce: 50 bouncing cat windows owned by one main window."""

import argparse
import ctypes
import math
import random
import sys
import time
import tkinter as tk
import winsound
from pathlib import Path


def asset(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name


def enable_dpi_awareness() -> None:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass


class MusicPlayer:
    """Play the included tune or a user supplied, licensed song.mp3."""

    def __init__(self) -> None:
        self.send = ctypes.windll.winmm.mciSendStringW
        self.send.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p]
        self.send.restype = ctypes.c_uint
        self.opened = False
        self.wav_playing = False
        self.track_name = "Original cat tune"

    @staticmethod
    def external_song() -> Path:
        folder = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
        return folder / "song.mp3"

    def play(self) -> bool:
        self.close()
        song = self.external_song()
        if song.is_file():
            if not self.send(f'open "{song}" type mpegvideo alias snowcatmusic', None, 0, None):
                self.opened = True
                if not self.send("play snowcatmusic repeat", None, 0, None):
                    self.track_name = "Your local song"
                    return True
                self.close()
        try:
            winsound.PlaySound(
                str(asset("cat-tune.wav")),
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP,
            )
            self.wav_playing = True
            self.track_name = "Original cat tune"
            return True
        except RuntimeError:
            return False

    def close(self) -> None:
        if self.opened:
            self.send("close snowcatmusic", None, 0, None)
            self.opened = False
        if self.wav_playing:
            winsound.PlaySound(None, 0)
            self.wav_playing = False


class BounceApp:
    def __init__(self, count: int, duration: float, no_music: bool) -> None:
        self.root = tk.Tk()
        self.root.title("Snow Leopard Bounce")
        self.root.configure(bg="#101521")
        self.root.resizable(False, False)
        self.root.geometry("470x470")
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind("<Escape>", lambda _event: self.close())
        self.root.bind("<Unmap>", self.on_unmap)
        self.root.bind("<Map>", self.on_map)
        self.root.iconbitmap(str(asset("cat.ico")))

        self.no_music = no_music
        self.running = True
        self.music_on = False
        self.music = MusicPlayer()
        self.timer_id = None
        self.last_frame = time.monotonic()
        self.sprites = []
        self.started = False
        self.rng = random.SystemRandom()
        self.average_speed = tk.IntVar(value=125)
        self.target_count = tk.IntVar(value=count)
        self.small_image = tk.PhotoImage(file=str(asset("cat-small.png")))
        self.large_image = tk.PhotoImage(file=str(asset("cat-large.png")))

        tk.Label(
            self.root,
            text="SNOW LEOPARD BOUNCE",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg="#101521",
        ).pack(pady=(15, 2))
        tk.Label(
            self.root,
            text="BOUNCE  •  BOOST  •  GLIDE",
            font=("Segoe UI", 9, "bold"),
            fg="#85e7da",
            bg="#101521",
        ).pack(pady=(0, 7))
        tk.Label(self.root, image=self.large_image, bg="#101521").pack()
        self.status = tk.Label(
            self.root,
            text="Original cat tune",
            font=("Segoe UI", 10),
            fg="#d5d2e6",
            bg="#101521",
        )
        self.status.pack(pady=(9, 4))

        self.speed_label = tk.Label(
            self.root,
            text="Average speed: 125 px/s",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#101521",
        )
        self.speed_label.pack(pady=(3, 0))
        tk.Scale(
            self.root,
            from_=60,
            to=220,
            resolution=5,
            variable=self.average_speed,
            command=self.update_speed_label,
            orient="horizontal",
            length=300,
            showvalue=False,
            bd=0,
            highlightthickness=0,
            sliderrelief="flat",
            troughcolor="#30394d",
            activebackground="#85e7da",
            bg="#101521",
            fg="white",
        ).pack(pady=(0, 7))

        self.count_label = tk.Label(
            self.root,
            text=f"Cats on screen: {count}",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#101521",
        )
        self.count_label.pack(pady=(2, 0))
        tk.Scale(
            self.root,
            from_=0,
            to=100,
            resolution=1,
            variable=self.target_count,
            command=self.update_count,
            orient="horizontal",
            length=300,
            showvalue=False,
            bd=0,
            highlightthickness=0,
            sliderrelief="flat",
            troughcolor="#30394d",
            activebackground="#85e7da",
            bg="#101521",
            fg="white",
        ).pack(pady=(0, 8))

        buttons = tk.Frame(self.root, bg="#101521")
        buttons.pack()
        self.music_button = tk.Button(
            buttons,
            text="Mute music",
            command=self.toggle_music,
            width=13,
            font=("Segoe UI", 10, "bold"),
            bg="#27394a",
            fg="white",
            activebackground="#3b566b",
            activeforeground="white",
            relief="flat",
            bd=0,
            pady=7,
            cursor="hand2",
        )
        self.music_button.pack(side="left", padx=7)
        tk.Button(
            buttons,
            text="Close all",
            command=self.close,
            width=13,
            font=("Segoe UI", 10, "bold"),
            bg="#a9415b",
            fg="white",
            activebackground="#cd617b",
            activeforeground="white",
            relief="flat",
            bd=0,
            pady=7,
            cursor="hand2",
        ).pack(side="left", padx=7)

        if self.no_music:
            self.music_button.configure(state="disabled", text="Music off")
        self.root.after(150, self.start)
        if duration > 0:
            self.root.after(round(duration * 1000), self.close)

    def start(self) -> None:
        if not self.running:
            return
        self.started = True
        self.sync_count()
        self.root.lift()
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
        window.configure(bg="#101521")
        window.attributes("-topmost", True)
        window.geometry(f"{size}x{size}+{round(x)}+{round(y)}")
        tk.Label(window, image=self.small_image, borderwidth=0, highlightthickness=0).pack()
        window.bind("<Button-1>", lambda _event: self.root.lift())
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
        self.root.lift()

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
            # The speed rises after impact, peaks at 0.22 s, then eases back
            # to the selected average speed without ever stopping.
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
        # Keep the close control visible above the moving windows.
        self.root.lift()
        self.timer_id = self.root.after(33, self.move)

    def update_speed_label(self, _value: str) -> None:
        self.speed_label.configure(text=f"Average speed: {self.average_speed.get()} px/s")

    def update_count(self, _value: str) -> None:
        self.count_label.configure(text=f"Cats on screen: {self.target_count.get()}")
        if self.started:
            self.sync_count()

    def on_unmap(self, event: tk.Event) -> None:
        if event.widget == self.root and self.root.state() == "iconic":
            for sprite in self.sprites:
                sprite["window"].withdraw()

    def on_map(self, event: tk.Event) -> None:
        if event.widget == self.root:
            for sprite in self.sprites:
                sprite["window"].deiconify()
            self.root.lift()

    def play_music(self) -> None:
        if self.music.play():
            self.music_on = True
            self.status.configure(text=self.music.track_name)
            self.music_button.configure(text="Mute music")
        else:
            self.music_button.configure(text="Music unavailable", state="disabled")

    def toggle_music(self) -> None:
        if self.music_on:
            self.music.close()
            self.music_on = False
            self.music_button.configure(text="Play music")
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
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--duration", type=float, default=0, help="Auto close after this many seconds")
    parser.add_argument("--no-music", action="store_true")
    args = parser.parse_args()
    enable_dpi_awareness()
    BounceApp(max(0, min(100, args.count)), args.duration, args.no_music).run()
