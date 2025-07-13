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
    def __init__(self, master, name, interval_sec):
        self.master = master
        self.name = name
        self.interval = interval_sec
        self.start_time = time.time()
        self.complete = False
        self.enabled = True
        self.canvas_size = 150
        self.sound_thread = None

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

        # Pack countdown label AFTER the buttons, only for "Work"
        if self.name.lower() == "work":
            self.countdown_label = tk.Label(self.frame, text="", font=("Arial", 14), fg="black")
            self.countdown_label.pack(pady=(5,10))
        else:
            self.countdown_label = None

        self.frame.pack(padx=20, pady=20)

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
        self.canvas.config(bg=self.master.cget("bg"))

    def toggle_enabled(self):
        self.enabled = self.toggle_var.get()
        self.reset()

    def play_sound_loop(self):
        while self.complete:
            if winsound:
                winsound.Beep(440, 200)  # Softer tone
            else:
                # macOS/Linux alternative with softer tone
                os.system('play -nq -t alsa synth 0.2 sine 440')
            time.sleep(1)

    def start_countdown(self):
        if self.countdown_label is None:
            return
        self.countdown_seconds = int(self.interval / 2)  # Half the timer duration
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
            flash_color = "#ff0000" if int(now * 2) % 2 == 0 else "#222"
            self.canvas.create_oval(10, 10, self.canvas_size - 10, self.canvas_size - 10, fill=flash_color, outline="")
            # Only start countdown if not active and countdown not finished
            if self.countdown_label and not self.countdown_active and not self.countdown_finished:
                self.start_countdown()
        else:
            self.canvas.create_oval(10, 10, self.canvas_size - 10, self.canvas_size - 10, fill="white", outline="")
            if percent > 0:
                self.canvas.create_arc(10, 10, self.canvas_size - 10, self.canvas_size - 10,
                                       start=90, extent=-angle, fill="#222", outline="")

        if percent >= 1 and not self.complete:
            self.complete = True
            self.completion_time = now
            self.sound_thread = threading.Thread(target=self.play_sound_loop, daemon=True)
            self.sound_thread.start()

        self.master.after(100, self.update)

def main():
    root = tk.Tk()
    root.title("Tacoshack Timers")

    title_label = tk.Label(root, text="Tacoshack Timers", font=("Arial", 24, "bold"))
    title_label.pack(pady=10, anchor='center')

    # Create a container frame to hold all timers centered horizontally
    container = tk.Frame(root)
    container.pack(padx=20, pady=20)

    timer_configs = [
        ("Tips", 5 * 60),
        ("Work", 10 * 60),
        ("Overtime", 30 * 60)
    ]

    timers = {}
    for name, seconds in timer_configs:
        widget = TimerWidget(container, name, seconds)
        widget.frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        timers[name.lower()] = widget

    def on_key_press(event):
        key_input = event.char.strip().lower()
        if key_input == '/':
            buffer.clear()
        elif key_input and len(buffer) < 20:
            buffer.append(key_input)
            command = ''.join(buffer)
            if command in timers:
                timers[command].reset()
                buffer.clear()

    buffer = []
    root.bind("<Key>", on_key_press)

    root.mainloop()

if __name__ == '__main__':
    main()
