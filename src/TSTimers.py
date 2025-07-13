# filepath: TSTimers/src/TSTimers.py
import tkinter as tk
from tkinter import Canvas
import time
import threading
import platform
import os

try:
    import winsound  # For Windows
except ImportError:
    winsound = None

class TimerWidget:
    def __init__(self, master, name, interval_sec, theme):
        self.master = master
        self.name = name
        self.interval = interval_sec
        self.start_time = time.time()
        self.complete = False
        self.enabled = True
        self.canvas_size = 150
        self.sound_thread = None
        self.theme = theme  # Reference to theme dict

        self.countdown_seconds = 0
        self.countdown_active = False
        self.countdown_finished = False  # Flag to mark countdown finished

        self.frame = tk.Frame(master)

        self.label = tk.Label(self.frame, text=self.name, font=("Arial", 16, "bold"))
        self.label.pack(pady=(0,5))

        self.canvas = Canvas(self.frame, width=self.canvas_size, height=self.canvas_size, highlightthickness=0)
        self.canvas.pack()

        self.button = tk.Button(self.frame, text=f"Restart {self.name}", command=self.reset)
        self.button.pack(side=tk.LEFT, padx=5)

        self.toggle_var = tk.BooleanVar(value=True)
        self.toggle_button = tk.Checkbutton(self.frame, text="Enabled", variable=self.toggle_var, command=self.toggle_enabled)
        self.toggle_button.pack(side=tk.LEFT, padx=5)

        if self.name.lower() == "work":
            self.countdown_label = tk.Label(self.frame, text="", font=("Arial", 14), fg=self.theme['text'])
            self.countdown_label.pack(pady=(5,10))
        else:
            self.countdown_label = None

        self.frame.pack(padx=20, pady=20)

        self.apply_theme()  # Apply initial theme

        self.update()

    def reset(self):
        self.start_time = time.time()
        self.complete = False
        self.sound_thread = None
        self.countdown_active = False
        self.countdown_finished = False
        self.countdown_seconds = 0
        if self.countdown_label:
            self.countdown_label.config(text="")
        self.canvas.config(bg=self.theme['canvas_bg'])

    def toggle_enabled(self):
        self.enabled = self.toggle_var.get()
        self.reset()

    def play_sound_loop(self):
        while self.complete:
            if winsound:
                winsound.Beep(440, 200)  # Softer tone
            else:
                os.system('play -nq -t alsa synth 0.2 sine 440')
            time.sleep(1)

    def start_countdown(self):
        if self.countdown_label is None:
            return
        self.countdown_seconds = int(self.interval / 2)  # Half timer duration
        self.countdown_active = True
        self.countdown_finished = False
        self.update_countdown()

    def update_countdown(self):
        if self.countdown_active:
            if self.countdown_seconds > 0:
                mins, secs = divmod(self.countdown_seconds, 60)
                self.countdown_label.config(text=f"GS Reset: {mins:02d}:{secs:02d}")
                self.countdown_seconds -= 1
                self.master.after(1000, self.update_countdown)
            else:
                self.countdown_label.config(text="GS Reset: 00:00")
                self.countdown_active = False
                self.countdown_finished = True

    def update(self):
        if not self.enabled:
            self.master.after(100, self.update)
            return

        now = time.time()
        elapsed = now - self.start_time
        percent = min(elapsed / self.interval, 1)
        angle = percent * 360

        self.canvas.delete("all")

        if self.complete:
            flash_color = self.theme['accent'] if int(now * 2) % 2 == 0 else self.theme['canvas_bg']
            self.canvas.create_oval(10, 10, self.canvas_size - 10, self.canvas_size - 10, fill=flash_color, outline="")
            if self.countdown_label and not self.countdown_active and not self.countdown_finished:
                self.start_countdown()
        else:
            self.canvas.create_oval(10, 10, self.canvas_size - 10, self.canvas_size - 10, fill=self.theme['canvas_fill'], outline="")
            if percent > 0:
                self.canvas.create_arc(10, 10, self.canvas_size - 10, self.canvas_size - 10,
                                       start=90, extent=-angle, fill=self.theme['arc_fill'], outline="")

        if percent >= 1 and not self.complete:
            self.complete = True
            self.completion_time = now
            self.sound_thread = threading.Thread(target=self.play_sound_loop, daemon=True)
            self.sound_thread.start()

        self.master.after(100, self.update)

    def apply_theme(self):
        self.frame.config(bg=self.theme['bg'])
        self.label.config(bg=self.theme['bg'], fg=self.theme['text'])
        self.canvas.config(bg=self.theme['canvas_bg'])
        self.button.config(bg=self.theme['button_bg'], fg=self.theme['button_fg'], activebackground=self.theme['button_active_bg'])
        self.toggle_button.config(bg=self.theme['bg'], fg=self.theme['text'], selectcolor=self.theme['bg'])
        if self.countdown_label:
            self.countdown_label.config(bg=self.theme['bg'], fg=self.theme['text'])


class TacoshackTimersApp:
    def __init__(self, root):
        self.root = root
        root.title("Tacoshack Timers")

        self.light_theme = {
            'bg': 'white',
            'text': 'black',
            'canvas_bg': 'white',
            'canvas_fill': '#222',
            'arc_fill': 'white',
            'button_bg': 'SystemButtonFace',
            'button_fg': 'black',
            'button_active_bg': '#ddd',
            'accent': '#10a37f',  # For flash color in light mode
        }

        self.dark_theme = {
            'bg': '#0a0a0a',             # ChatGPT very dark background
            'text': '#d3d3d3',           # Light gray text
            'canvas_bg': '#0a0a0a',      # Same as bg
            'canvas_fill': '#262626',    # Dark gray fill for circle bg
            'arc_fill': '#10a37f',       # Teal-ish arc fill
            'button_bg': '#262626',      # Darker gray for buttons
            'button_fg': '#d3d3d3',      # Light text on buttons
            'button_active_bg': '#3a3a3a', # Slightly lighter on press
            'accent': '#10a37f',         # Accent teal for flashing circle
        }

        self.theme = self.light_theme

        # Set root bg initially
        self.root.config(bg=self.theme['bg'])

        self.top_frame = tk.Frame(root, bg=self.theme['bg'])  # Store as instance variable
        self.top_frame.pack(fill=tk.X, pady=10)

        self.title_label = tk.Label(self.top_frame, text="Tacoshack Timers", font=("Arial", 24, "bold"),
                                    bg=self.theme['bg'], fg=self.theme['text'])
        self.title_label.pack(side=tk.LEFT, padx=20)

        self.spacer = tk.Frame(self.top_frame, bg=self.theme['bg'])  # Store as instance variable
        self.spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.toggle_theme_button = tk.Button(self.top_frame, text="Toggle Dark Theme", command=self.toggle_theme,
                                            bg=self.theme['button_bg'], fg=self.theme['button_fg'], activebackground=self.theme['button_active_bg'])
        self.toggle_theme_button.pack(side=tk.RIGHT, padx=20)

        self.container = tk.Frame(root, bg=self.theme['bg'])
        self.container.pack(padx=20, pady=20)

        timer_configs = [
            ("Tips", 5 * 60),
            ("Work", 10 * 60),
            ("Overtime", 30 * 60)
        ]

        self.timers = {}
        for name, seconds in timer_configs:
            widget = TimerWidget(self.container, name, seconds, self.theme)
            widget.frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            self.timers[name.lower()] = widget

    def toggle_theme(self):
        self.theme = self.dark_theme if self.theme == self.light_theme else self.light_theme

        self.root.config(bg=self.theme['bg'])
        self.top_frame.config(bg=self.theme['bg'])      # Update top_frame
        self.spacer.config(bg=self.theme['bg'])         # Update spacer
        self.container.config(bg=self.theme['bg'])

        self.title_label.config(bg=self.theme['bg'], fg=self.theme['text'])
        self.toggle_theme_button.config(bg=self.theme['button_bg'], fg=self.theme['button_fg'], activebackground=self.theme['button_active_bg'])

        for timer in self.timers.values():
            timer.theme = self.theme
            timer.apply_theme()


def main():
    root = tk.Tk()
    app = TacoshackTimersApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()