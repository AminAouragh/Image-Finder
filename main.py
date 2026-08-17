from datetime import datetime
from tkinter import font
import tkinter as tk
import threading
import pyautogui
import requests
import time

# --- INSTELLINGEN ---
WEBHOOK_URL = 'https://discord.com/api/webhooks/1504506866217255083/QxN-eIEhQ9-32qbuj4dUt8Xp-N-MtTNH9AmPDpLSk3oe22LepxkzB44cM3X2vasCX7sv'
AFBEELDINGEN = [
    'images/galaxy.png',
    'images/Stellar.png'
]

zoeken_actief = False

def stuur_notificatie(gevonden_afbeelding):
    data = {
        "content": f"Begin te kijken **{gevonden_afbeelding}** is er"
    }
    response = requests.post(WEBHOOK_URL, json=data)

    if response.status_code == 204:
        log(f"Notificatie voor {gevonden_afbeelding} succesvol verstuurd.")
    else:
        log(f"Fout bij sturen notificatie: {response.status_code}")


def zoek_loop():
    global zoeken_actief
    log(f"Programma zoekt naar {len(AFBEELDINGEN)} afbeeldingen...")

    while zoeken_actief:
        for afbeelding in AFBEELDINGEN:
            if not zoeken_actief:
                break

            try:
                locatie = pyautogui.locateOnScreen(afbeelding, confidence=0.8)

                if locatie is not None:
                    log(f"✅ {afbeelding} gevonden!")
                    stuur_notificatie(afbeelding)

                    for _ in range(60):
                        if not zoeken_actief:
                            break
                        time.sleep(1)

            except pyautogui.ImageNotFoundException:
                pass

        for _ in range(2):
            if not zoeken_actief:
                break
            time.sleep(1)


def start_zoeken():
    global zoeken_actief
    if not zoeken_actief:
        zoeken_actief = True

        _zet_status("actief")
        log("Zoeken gestart.")
        start_knop.set_enabled(False)
        stop_knop.set_enabled(True)

        threading.Thread(target=zoek_loop, daemon=True).start()


def stop_zoeken():
    global zoeken_actief
    zoeken_actief = False

    _zet_status("gestopt")
    log("Zoeken gestopt.")
    start_knop.set_enabled(True)
    stop_knop.set_enabled(False)


COLOR_BG = "#0f1115"
COLOR_CARD = "#171a21"
COLOR_CARD_BORDER = "#262a33"
COLOR_TEXT_PRIMARY = "#e8eaed"
COLOR_TEXT_SECONDARY = "#8b8f98"
COLOR_TEXT_DIM = "#5a5f6a"
COLOR_ACCENT = "#5b8cff"
COLOR_ACCENT_HOVER = "#4a75e0"
COLOR_SUCCESS = "#3ddc84"
COLOR_SUCCESS_BG = "#12291d"
COLOR_DANGER = "#ff5c5c"
COLOR_DANGER_BG = "#2b1414"
COLOR_STOP_BTN = "#232733"
COLOR_STOP_BTN_HOVER = "#2c313f"
COLOR_DISABLED_BTN = "#1b1f28"
COLOR_LOG_BG = "#0a0c0f"

STATUS_STYLES = {
    "gestopt": (COLOR_TEXT_SECONDARY, COLOR_CARD, "Gestopt"),
    "actief": (COLOR_SUCCESS, COLOR_SUCCESS_BG, "Actief"),
    "fout": (COLOR_DANGER, COLOR_DANGER_BG, "Fout"),
}

def round_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    points = [
        x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class RoundedCard(tk.Canvas):
    def __init__(self, parent, fill=COLOR_CARD, border=COLOR_CARD_BORDER,
                 radius=14, parent_bg=COLOR_BG, height=None):
        super().__init__(parent, bg=parent_bg, highlightthickness=0, bd=0,
                         **({"height": height} if height else {}))
        self.fill = fill
        self.border = border
        self.radius = radius
        self.body = tk.Frame(self, bg=fill)
        self._window = self.create_window(0, 0, window=self.body, anchor="nw")
        self.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        w = self.winfo_width()
        h = self.winfo_height()
        self.delete("shape")
        shape = round_rect(self, 1, 1, w - 1, h - 1, self.radius,
                           fill=self.fill, outline=self.border, width=1)
        self.itemconfig(shape, tags="shape")
        self.tag_lower(shape)
        self.coords(self._window, 1, 1)
        self.itemconfig(self._window, width=w - 2, height=h - 2)

    def set_fill(self, fill):
        self.fill = fill
        self.body.config(bg=fill)
        for child in self.body.winfo_children():
            try:
                child.config(bg=fill)
            except tk.TclError:
                pass
        self._redraw()


class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, bg, hover_bg,
                 fg="#ffffff", parent_bg=COLOR_BG,
                 width=300, height=44, font_size=11, font_weight="bold"):
        super().__init__(parent, width=width, height=height,
                         bg=parent_bg, highlightthickness=0, bd=0)
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        self.fg = fg
        self.w = width
        self.h = height
        self.radius = 12
        self.text = text
        self.enabled = True
        self.font_obj = font.Font(family="Segoe UI", size=font_size,
                                  weight=font_weight)
        self._bind_events()
        self._draw(self.bg, self.fg)
        self.config(cursor="hand2")

    def _bind_events(self):
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_enter(self, _=None):
        if self.enabled:
            self._draw(self.hover_bg, self.fg)

    def _on_leave(self, _=None):
        if self.enabled:
            self._draw(self.bg, self.fg)

    def _on_press(self, _=None):
        if self.enabled:
            self._draw(self.hover_bg, self.fg, inset=2)

    def _on_release(self, _=None):
        if self.enabled:
            self._draw(self.hover_bg, self.fg)
            self.command()

    def _draw(self, color, fg, inset=0):
        self.delete("all")
        round_rect(self, 1 + inset, 1 + inset, self.w - 1 - inset,
                   self.h - 1 - inset, self.radius, fill=color, outline="")
        self.create_text(self.w / 2, self.h / 2, text=self.text,
                         fill=fg, font=self.font_obj)

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if enabled:
            self.config(cursor="hand2")
            self._draw(self.bg, self.fg)
        else:
            self.config(cursor="arrow")
            self._draw(COLOR_DISABLED_BTN, COLOR_TEXT_DIM)

_pulse_job = {"id": None, "on": False}


def _zet_status(status_key: str):
    fg, bg, tekst = STATUS_STYLES[status_key]
    status_card.set_fill(bg)
    status_dot.config(bg=bg)
    status_dot.itemconfig(dot, fill=fg)
    status_tekst_label.config(text=f"Status: {tekst}", fg=fg, bg=bg)
    if status_key == "actief":
        _start_pulse(fg, bg)
    else:
        _stop_pulse(fg)


def _start_pulse(fg, bg):
    _stop_pulse(fg)

    def tick():
        _pulse_job["on"] = not _pulse_job["on"]
        status_dot.itemconfig(dot, fill=fg if _pulse_job["on"] else bg)
        status_dot.itemconfig(ring, outline=fg if _pulse_job["on"] else bg)
        _pulse_job["id"] = root.after(600, tick)
    tick()


def _stop_pulse(fg):
    if _pulse_job["id"] is not None:
        root.after_cancel(_pulse_job["id"])
        _pulse_job["id"] = None
    status_dot.itemconfig(dot, fill=fg)
    status_dot.itemconfig(ring, outline="")


def log(bericht: str):
    tijd = datetime.now().strftime("%H:%M:%S")
    log_box.config(state="normal")
    log_box.insert("end", f"[{tijd}] ", "tijd")
    log_box.insert("end", f"{bericht}\n", "tekst")
    log_box.see("end")
    log_box.config(state="disabled")

root = tk.Tk()
root.title("Webhook Zoeker")
root.geometry("400x520")
root.configure(bg=COLOR_BG)
root.resizable(False, False)

FONT_TITLE = font.Font(family="Segoe UI Semibold", size=16, weight="bold")
FONT_SUB = font.Font(family="Segoe UI", size=9)
FONT_STATUS = font.Font(family="Segoe UI", size=10, weight="bold")
FONT_LOG_HEADER = font.Font(family="Segoe UI", size=8, weight="bold")

accent_bar = tk.Frame(root, bg=COLOR_ACCENT, height=3)
accent_bar.pack(fill="x")

header = tk.Frame(root, bg=COLOR_BG)
header.pack(fill="x", padx=26, pady=(22, 0))

tk.Label(header, text="Webhook Zoeker", font=FONT_TITLE,
         fg=COLOR_TEXT_PRIMARY, bg=COLOR_BG).pack(anchor="w")
tk.Label(header, text="Scan en beheer inkomende webhooks", font=FONT_SUB,
         fg=COLOR_TEXT_SECONDARY, bg=COLOR_BG).pack(anchor="w", pady=(3, 0))

status_card = RoundedCard(root, fill=COLOR_CARD, parent_bg=COLOR_BG, height=52)
status_card.pack(fill="x", padx=26, pady=(18, 14))
status_card.pack_propagate(False)

status_inner = tk.Frame(status_card.body, bg=COLOR_CARD)
status_inner.place(relx=0.0, rely=0.5, x=16, anchor="w")

status_dot = tk.Canvas(status_inner, width=14, height=14, bg=COLOR_CARD,
                       highlightthickness=0, bd=0)
ring = status_dot.create_oval(0, 0, 13, 13, outline="", width=1)
dot = status_dot.create_oval(4, 4, 10, 10, fill=COLOR_TEXT_SECONDARY,
                             outline="")
status_dot.pack(side="left")

status_tekst_label = tk.Label(status_inner, text="Status: Gestopt",
                              font=FONT_STATUS, fg=COLOR_TEXT_SECONDARY,
                              bg=COLOR_CARD)
status_tekst_label.pack(side="left", padx=(10, 0))

knoppen_frame = tk.Frame(root, bg=COLOR_BG)
knoppen_frame.pack(fill="x", padx=26)

start_knop = ModernButton(knoppen_frame, text="Start Zoeken",
                          command=start_zoeken, bg=COLOR_ACCENT,
                          hover_bg=COLOR_ACCENT_HOVER)
start_knop.pack(pady=(0, 8))

stop_knop = ModernButton(knoppen_frame, text="Stop Zoeken",
                         command=stop_zoeken, bg=COLOR_STOP_BTN,
                         hover_bg=COLOR_STOP_BTN_HOVER,
                         fg=COLOR_TEXT_PRIMARY)
stop_knop.pack()
stop_knop.set_enabled(False)

tk.Label(root, text="ACTIVITEIT", font=FONT_LOG_HEADER,
         fg=COLOR_TEXT_DIM, bg=COLOR_BG).pack(anchor="w", padx=27,
                                              pady=(18, 6))

log_card = RoundedCard(root, fill=COLOR_LOG_BG, parent_bg=COLOR_BG)
log_card.pack(fill="both", expand=True, padx=26, pady=(0, 24))

log_box = tk.Text(log_card.body, bg=COLOR_LOG_BG, fg=COLOR_TEXT_SECONDARY,
                  font=("Consolas", 9), relief="flat", padx=14, pady=12,
                  wrap="word", state="disabled", borderwidth=0,
                  highlightthickness=0, insertbackground=COLOR_TEXT_PRIMARY,
                  spacing1=1, spacing3=3)
log_box.pack(fill="both", expand=True, padx=2, pady=2)
log_box.tag_config("tijd", foreground=COLOR_TEXT_DIM)
log_box.tag_config("tekst", foreground=COLOR_TEXT_PRIMARY)

log("Klaar. Wachten op start.")

root.mainloop()
