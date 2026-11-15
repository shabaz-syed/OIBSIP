"""Tkinter interface: input form, colour-coded result, history table and BMI trend chart."""
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from . import database
from .calculator import InvalidInputError, calculate_bmi, classify, clean_username, validate_inputs

CATEGORY_COLORS = {
    "Underweight": "#1565c0",
    "Normal": "#2e7d32",
    "Overweight": "#ef6c00",
    "Obese": "#c62828",
}


class BMIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Calculator")
        self.resizable(False, False)
        self.db_ok = True
        try:
            database.init_db()
        except database.DatabaseError as exc:
            self.db_ok = False
            messagebox.showwarning("Database problem", f"{exc}\n\nYou can still calculate BMI, but records won't be saved.")
        self._build_widgets()
        self._refresh_users()
        self.bind("<Return>", lambda _event: self.on_calculate())

    # ---------- layout ----------
    def _build_widgets(self):
        form = ttk.LabelFrame(self, text="Enter your details", padding=12)
        form.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="ew")

        ttk.Label(form, text="User name:").grid(row=0, column=0, sticky="w", pady=4)
        self.user_box = ttk.Combobox(form, width=24)
        self.user_box.grid(row=0, column=1, pady=4, padx=(8, 0))
        self.user_box.bind("<<ComboboxSelected>>", lambda _e: self._load_history())
        self.user_box.bind("<FocusOut>", lambda _e: self._load_history())

        ttk.Label(form, text="Weight (kg):").grid(row=1, column=0, sticky="w", pady=4)
        self.weight_entry = ttk.Entry(form, width=27)
        self.weight_entry.grid(row=1, column=1, pady=4, padx=(8, 0))

        ttk.Label(form, text="Height (m):").grid(row=2, column=0, sticky="w", pady=4)
        self.height_entry = ttk.Entry(form, width=27)
        self.height_entry.grid(row=2, column=1, pady=4, padx=(8, 0))

        buttons = ttk.Frame(form)
        buttons.grid(row=3, column=0, columnspan=2, pady=(8, 0))
        ttk.Button(buttons, text="Calculate", command=self.on_calculate).pack(side="left", padx=4)
        ttk.Button(buttons, text="Show Trend", command=self.on_show_trend).pack(side="left", padx=4)
        ttk.Button(buttons, text="Clear", command=self.on_clear).pack(side="left", padx=4)

        self.result_label = tk.Label(self, text="Your BMI will appear here", font=("Helvetica", 16, "bold"))
        self.result_label.grid(row=1, column=0, pady=8)

        history = ttk.LabelFrame(self, text="History", padding=8)
        history.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="ew")
        columns = ("date", "weight", "height", "bmi", "category")
        self.tree = ttk.Treeview(history, columns=columns, show="headings", height=7)
        for col, title, width in [
            ("date", "Date", 140), ("weight", "Weight (kg)", 85), ("height", "Height (m)", 80),
            ("bmi", "BMI", 60), ("category", "Category", 100),
        ]:
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, anchor="center")
        self.tree.pack(side="left")
        scroll = ttk.Scrollbar(history, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

    # ---------- actions ----------
    def on_calculate(self):
        try:
            username = clean_username(self.user_box.get())
            weight, height = validate_inputs(self.weight_entry.get(), self.height_entry.get())
        except InvalidInputError as exc:
            messagebox.showerror("Check your input", str(exc))
            return

        bmi = calculate_bmi(weight, height)
        category = classify(bmi)
        self.result_label.config(text=f"BMI: {bmi:.2f}  ({category})", fg=CATEGORY_COLORS[category])

        if self.db_ok:
            try:
                database.add_record(username, weight, height, bmi, category)
            except database.DatabaseError as exc:
                messagebox.showwarning("Not saved", f"Your result is shown, but it could not be saved.\n\n{exc}")
        self._refresh_users()
        self._load_history()

    def on_clear(self):
        self.weight_entry.delete(0, tk.END)
        self.height_entry.delete(0, tk.END)
        self.result_label.config(text="Your BMI will appear here", fg="black")

    def on_show_trend(self):
        try:
            username = clean_username(self.user_box.get())
        except InvalidInputError as exc:
            messagebox.showerror("Check your input", str(exc))
            return
        try:
            records = database.get_records(username)
        except database.DatabaseError as exc:
            messagebox.showerror("Database problem", str(exc))
            return
        if len(records) < 2:
            messagebox.showinfo("Not enough data", "Save at least two BMI records for this user to see a trend.")
            return

        dates = [datetime.fromisoformat(r[0]) for r in records]
        values = [r[3] for r in records]

        window = tk.Toplevel(self)
        window.title(f"BMI trend - {username}")
        figure = Figure(figsize=(6, 4), dpi=100)
        axes = figure.add_subplot(111)
        axes.plot(dates, values, marker="o", color="#1565c0")
        axes.axhspan(18.5, 25, alpha=0.12, color="green", label="Normal range")
        axes.set_xlabel("Date")
        axes.set_ylabel("BMI")
        axes.set_title(f"BMI over time: {username}")
        axes.legend(loc="best")
        figure.autofmt_xdate()
        canvas = FigureCanvasTkAgg(figure, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---------- helpers ----------
    def _refresh_users(self):
        if not self.db_ok:
            return
        try:
            self.user_box["values"] = database.list_users()
        except database.DatabaseError:
            pass

    def _load_history(self):
        self.tree.delete(*self.tree.get_children())
        name = " ".join(self.user_box.get().split())
        if not (self.db_ok and name):
            return
        try:
            records = database.get_records(name)
        except database.DatabaseError as exc:
            messagebox.showwarning("Database problem", str(exc))
            return
        for date, weight, height, bmi, category in reversed(records):  # newest first
            self.tree.insert("", "end", values=(date.replace("T", " "), weight, height, f"{bmi:.2f}", category))


def run():
    BMIApp().mainloop()
