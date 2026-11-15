"""Tkinter interface: search bar, current conditions, 6-hour and 5-day forecast, unit toggle."""
import queue
import threading
import tkinter as tk
from io import BytesIO
from tkinter import ttk

from PIL import Image, ImageTk

from . import api
from .units import format_temp, format_wind


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather App")
        self.resizable(False, False)
        self.unit = "C"
        self.report = None
        self.icon_bytes = {}
        self.photos = {}          # (icon code, size) -> PhotoImage; keeps references alive
        self.results = queue.Queue()
        self._build_widgets()
        self.bind("<Return>", lambda _e: self.on_get_weather())
        self.after(100, self._poll_results)

    # ---------- layout ----------
    def _build_widgets(self):
        top = ttk.Frame(self, padding=12)
        top.grid(row=0, column=0, sticky="ew")
        ttk.Label(top, text="City or ZIP:").pack(side="left")
        self.city_entry = ttk.Entry(top, width=22)
        self.city_entry.pack(side="left", padx=6)
        self.city_entry.focus()
        self.get_button = ttk.Button(top, text="Get Weather", command=self.on_get_weather)
        self.get_button.pack(side="left", padx=2)
        self.locate_button = ttk.Button(top, text="Use My Location", command=self.on_use_location)
        self.locate_button.pack(side="left", padx=2)
        self.unit_button = ttk.Button(top, text="Switch to °F", command=self.on_toggle_unit)
        self.unit_button.pack(side="left", padx=2)

        self.message = tk.Label(self, text="Enter a city or ZIP code to begin.", fg="#555555", wraplength=560)
        self.message.grid(row=1, column=0, pady=(0, 6))

        self.current_frame = ttk.LabelFrame(self, text="Current weather", padding=10)
        self.current_frame.grid(row=2, column=0, padx=12, pady=6, sticky="ew")
        self.hourly_frame = ttk.LabelFrame(self, text="Next 6 hours", padding=10)
        self.hourly_frame.grid(row=3, column=0, padx=12, pady=6, sticky="ew")
        self.daily_frame = ttk.LabelFrame(self, text="Next 5 days", padding=10)
        self.daily_frame.grid(row=4, column=0, padx=12, pady=(6, 12), sticky="ew")

    # ---------- user actions ----------
    def on_get_weather(self):
        self._start_fetch(self.city_entry.get(), use_ip=False)

    def on_use_location(self):
        self._start_fetch("", use_ip=True)

    def on_toggle_unit(self):
        self.unit = "F" if self.unit == "C" else "C"
        self.unit_button.config(text="Switch to °C" if self.unit == "F" else "Switch to °F")
        if self.report:
            self._render()

    # ---------- background fetch ----------
    def _start_fetch(self, query, use_ip):
        try:
            if not use_ip:
                query = api.validate_query(query)
        except api.WeatherError as exc:
            return self._show_error(str(exc))
        self._set_busy(True)
        self._show_message("Loading..." if not use_ip else "Detecting your location...", "#555555")
        threading.Thread(target=self._worker, args=(query, use_ip), daemon=True).start()

    def _worker(self, query, use_ip):
        try:
            if use_ip:
                query = api.locate_by_ip()
            report = api.get_report(query)
            icons = {code: api.fetch_icon(code) for code in report.icon_codes()}
            self.results.put(("ok", report, icons, query))
        except api.WeatherError as exc:
            self.results.put(("error", str(exc), None, query))
        except Exception:  # never let a worker thread die silently
            self.results.put(("error", "Something unexpected went wrong. Please try again.", None, query))

    def _poll_results(self):
        try:
            while True:
                kind, payload, icons, query = self.results.get_nowait()
                self._set_busy(False)
                if kind == "ok":
                    self.report, self.icon_bytes = payload, icons
                    self.city_entry.delete(0, tk.END)
                    self.city_entry.insert(0, query)
                    self._show_message("", "#555555")
                    self._render()
                else:
                    self._show_error(payload)
        except queue.Empty:
            pass
        self.after(100, self._poll_results)

    # ---------- rendering ----------
    def _render(self):
        r, unit = self.report, self.unit
        for frame in (self.current_frame, self.hourly_frame, self.daily_frame):
            for child in frame.winfo_children():
                child.destroy()

        c = r.current
        self._icon_label(self.current_frame, c.icon, 100).grid(row=0, column=0, rowspan=3, padx=(0, 14))
        ttk.Label(self.current_frame, text=f"{c.city}, {c.country}", font=("Helvetica", 16, "bold")).grid(
            row=0, column=1, sticky="w")
        ttk.Label(self.current_frame, text=f"{format_temp(c.temp_c, unit)}   {c.description}",
                  font=("Helvetica", 14)).grid(row=1, column=1, sticky="w")
        ttk.Label(self.current_frame,
                  text=f"Feels like {format_temp(c.feels_c, unit)}  |  Humidity {c.humidity}%  |  "
                       f"Wind {format_wind(c.wind_ms, unit)}").grid(row=2, column=1, sticky="w")

        if not r.hourly:
            ttk.Label(self.hourly_frame, text="No hourly data available.").pack()
        for i, h in enumerate(r.hourly):
            cell = ttk.Frame(self.hourly_frame)
            cell.grid(row=0, column=i, padx=18)
            ttk.Label(cell, text=h.time.strftime("%I %p").lstrip("0")).pack()
            self._icon_label(cell, h.icon, 50).pack()
            ttk.Label(cell, text=format_temp(h.temp_c, unit), font=("Helvetica", 12, "bold")).pack()

        if not r.daily:
            ttk.Label(self.daily_frame, text="No daily data available.").pack()
        for i, d in enumerate(r.daily):
            cell = ttk.Frame(self.daily_frame)
            cell.grid(row=0, column=i, padx=14)
            ttk.Label(cell, text=d.date.strftime("%a %d")).pack()
            self._icon_label(cell, d.icon, 50).pack()
            ttk.Label(cell, text=f"{format_temp(d.max_c, unit)} / {format_temp(d.min_c, unit)}").pack()

    def _icon_label(self, parent, code, size):
        photo = self._photo(code, size)
        label = ttk.Label(parent, image=photo) if photo else ttk.Label(parent, text="")
        return label

    def _photo(self, code, size):
        key = (code, size)
        if key not in self.photos:
            data = self.icon_bytes.get(code)
            if not data:
                return None
            try:
                image = Image.open(BytesIO(data)).convert("RGBA").resize((size, size))
                self.photos[key] = ImageTk.PhotoImage(image)
            except Exception:
                return None
        return self.photos[key]

    # ---------- small helpers ----------
    def _show_message(self, text, color):
        self.message.config(text=text, fg=color)

    def _show_error(self, text):
        self._show_message(text, "#c62828")

    def _set_busy(self, busy):
        state = "disabled" if busy else "normal"
        self.get_button.config(state=state)
        self.locate_button.config(state=state)


def run():
    WeatherApp().mainloop()
