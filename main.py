from datetime import datetime
from tkinter import font
import tkinter as tk
import threading
import pyautogui
import requests
import time

WEBHOOK_URL = 'https://discord.com/api/webhooks/1504506866217255083/QxN-eIEhQ9-32qbuj4dUt8Xp-N-MtTNH9AmPDpLSk3oe22LepxkzB44cM3X2vasCX7sv'
AFBEELDINGEN = [
    'images/galaxy.png',
    'images/image.png'
]

zoeken_actief = False


def stuur_notificatie(gevonden_afbeelding):
    data = {
        "content": f"Begin te kijken **{gevonden_afbeelding}** is er"
    }
    response = requests.post(WEBHOOK_URL, json=data)

    if response.status_code == 204:
        print(f"Notificatie voor {gevonden_afbeelding} succesvol verstuurd.")
    else:
        print(f"Fout bij sturen notificatie: {response.status_code}")


def zoek_loop():
    global zoeken_actief

    print(
        f"Programma is gestart en zoekt naar {len(AFBEELDINGEN)} afbeeldingen...")

    while zoeken_actief:
        for afbeelding in AFBEELDINGEN:
            if not zoeken_actief:
                break

            try:
                locatie = pyautogui.locateOnScreen(afbeelding, confidence=0.8)

                if locatie is not None:
                    status_label.config(
                        text=f"Gevonden: {afbeelding}!", fg="green")
                    print(f"{afbeelding} gevonden!")
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

        if zoeken_actief:
            status_label.config(text="Status: Aan het zoeken...", fg="blue")


def start_zoeken():
    global zoeken_actief
    if not zoeken_actief:
        zoeken_actief = True
        status_label.config(text="Status: Aan het zoeken...", fg="blue")

        threading.Thread(target=zoek_loop, daemon=True).start()


def stop_zoeken():
    """Wordt uitgevoerd als je op Stop klikt."""
    global zoeken_actief
    zoeken_actief = False
    status_label.config(text="Status: Gestopt", fg="red")
    print("Zoeken is gestopt.")


# --- GUI OPBOUWEN ---
"""
Webhook Zoeker - Moderne dark-theme GUI
=========================================
Dit is alleen de interface. De start_zoeken() en stop_zoeken() functies
zijn placeholders - vul ze zelf verder in met de logica die je nodig hebt.
"""


# ---------------------------------------------------------------------------
# Kleurenpalet (dark theme)
# ---------------------------------------------------------------------------
COLOR_BG = "#0f1115"          # achtergrond hoofdvenster
COLOR_CARD = "#171a21"        # achtergrond "kaart" elementen
COLOR_CARD_BORDER = "#262a33"
COLOR_TEXT_PRIMARY = "#e8eaed"
COLOR_TEXT_SECONDARY = "#8b8f98"
COLOR_ACCENT = "#5b8cff"      # blauw accent
COLOR_ACCENT_HOVER = "#4a75e0"
COLOR_SUCCESS = "#3ddc84"
COLOR_SUCCESS_BG = "#173324"
COLOR_DANGER = "#ff5c5c"
COLOR_DANGER_BG = "#331717"
COLOR_STOP_BTN = "#232733"
COLOR_STOP_BTN_HOVER = "#2c313f"
COLOR_LOG_BG = "#0a0c0f"

# Status kleuren gekoppeld aan tekst
STATUS_STYLES = {
    "gestopt": (COLOR_TEXT_SECONDARY, COLOR_CARD),
    "actief": (COLOR_SUCCESS, COLOR_SUCCESS_BG),
    "fout": (COLOR_DANGER, COLOR_DANGER_BG),
}

is_actief = False


# ---------------------------------------------------------------------------
# Helper: rounded-look button via Canvas (Tkinter Buttons zijn lastig te
# stylen; dit geeft een strakkere, moderne look dan een standaard Button)
# ---------------------------------------------------------------------------
class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, bg, hover_bg, fg="#ffffff",
                 width=220, height=42, font_size=11, font_weight="bold"):
        super().__init__(parent, width=width, height=height,
                         bg=COLOR_BG, highlightthickness=0)
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        self.fg = fg
        self.width = width
        self.height = height
        self.radius = 10
        self.text = text
        self.font_obj = font.Font(
            family="Segoe UI", size=font_size, weight=font_weight)

        self._draw(self.bg)

        self.bind("<Enter>", lambda e: self._draw(self.hover_bg))
        self.bind("<Leave>", lambda e: self._draw(self.bg))
        self.bind("<Button-1>", lambda e: self.command())

    def _round_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
            x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _draw(self, color):
        self.delete("all")
        self._round_rect(1, 1, self.width - 1, self.height - 1,
                         self.radius, fill=color, outline="")
        self.create_text(self.width / 2, self.height / 2, text=self.text,
                         fill=self.fg, font=self.font_obj)

    def set_enabled(self, enabled: bool):
        if enabled:
            self.bind("<Button-1>", lambda e: self.command())
            self.bind("<Enter>", lambda e: self._draw(self.hover_bg))
            self.bind("<Leave>", lambda e: self._draw(self.bg))
            self._draw(self.bg)
        else:
            self.unbind("<Button-1>")
            self.unbind("<Enter>")
            self.unbind("<Leave>")
            self._draw(COLOR_STOP_BTN)


# ---------------------------------------------------------------------------
# Placeholder-functies — vul hier je eigen logica in
# ---------------------------------------------------------------------------
def start_zoeken():
    """TODO: eigen logica hier — bv. thread starten die het scherm scant
    of een lokale server opzet om webhooks te ontvangen."""
    global is_actief
    is_actief = True
    _zet_status("actief")
    log("Zoeken gestart.")
    start_knop.set_enabled(False)
    stop_knop.set_enabled(True)


def stop_zoeken():
    """TODO: eigen logica hier — bv. thread/server netjes afsluiten."""
    global is_actief
    is_actief = False
    _zet_status("gestopt")
    log("Zoeken gestopt.")
    start_knop.set_enabled(True)
    stop_knop.set_enabled(False)


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------
def _zet_status(status_key: str):
    fg, bg = STATUS_STYLES[status_key]
    tekst = {"gestopt": "Gestopt", "actief": "Actief",
             "fout": "Fout"}[status_key]
    status_dot.itemconfig(dot, fill=fg)
    status_tekst_label.config(text=f"Status: {tekst}", fg=fg)
    status_pill.config(bg=bg)
    status_tekst_label.config(bg=bg)
    status_dot.config(bg=bg)


def log(bericht: str):
    tijd = datetime.now().strftime("%H:%M:%S")
    log_box.config(state="normal")
    log_box.insert("end", f"[{tijd}] {bericht}\n")
    log_box.see("end")
    log_box.config(state="disabled")


# ---------------------------------------------------------------------------
# Hoofdvenster
# ---------------------------------------------------------------------------
root = tk.Tk()
root.title("Webhook Zoeker")
root.geometry("380x460")
root.configure(bg=COLOR_BG)
root.resizable(False, False)

FONT_TITLE = font.Font(family="Segoe UI", size=15, weight="bold")
FONT_SUB = font.Font(family="Segoe UI", size=9)
FONT_STATUS = font.Font(family="Segoe UI", size=10, weight="bold")
FONT_LOG_HEADER = font.Font(family="Segoe UI", size=9, weight="bold")

# --- Header -----------------------------------------------------------
header = tk.Frame(root, bg=COLOR_BG)
header.pack(fill="x", padx=24, pady=(24, 4))

titel_label = tk.Label(header, text="Webhook Zoeker", font=FONT_TITLE,
                       fg=COLOR_TEXT_PRIMARY, bg=COLOR_BG)
titel_label.pack(anchor="w")

subtitel_label = tk.Label(header, text="Scan en beheer inkomende webhooks",
                          font=FONT_SUB, fg=COLOR_TEXT_SECONDARY, bg=COLOR_BG)
subtitel_label.pack(anchor="w", pady=(2, 0))

# --- Status pill --------------------------------------------------------
status_pill = tk.Frame(root, bg=COLOR_CARD, highlightthickness=1,
                       highlightbackground=COLOR_CARD_BORDER)
status_pill.pack(fill="x", padx=24, pady=16)

status_inner = tk.Frame(status_pill, bg=COLOR_CARD)
status_inner.pack(fill="x", padx=16, pady=12)

status_dot = tk.Canvas(status_inner, width=10, height=10, bg=COLOR_CARD,
                       highlightthickness=0)
dot = status_dot.create_oval(
    0, 0, 10, 10, fill=COLOR_TEXT_SECONDARY, outline="")
status_dot.pack(side="left")

status_tekst_label = tk.Label(status_inner, text="Status: Gestopt",
                              font=FONT_STATUS, fg=COLOR_TEXT_SECONDARY, bg=COLOR_CARD)
status_tekst_label.pack(side="left", padx=(10, 0))

# --- Knoppen --------------------------------------------------------------
knoppen_frame = tk.Frame(root, bg=COLOR_BG)
knoppen_frame.pack(pady=(0, 8))

start_knop = ModernButton(knoppen_frame, text="Start Zoeken", command=start_zoeken,
                          bg=COLOR_ACCENT, hover_bg=COLOR_ACCENT_HOVER)
start_knop.pack(pady=6)

stop_knop = ModernButton(knoppen_frame, text="Stop Zoeken", command=stop_zoeken,
                         bg=COLOR_STOP_BTN, hover_bg=COLOR_STOP_BTN_HOVER,
                         fg=COLOR_TEXT_SECONDARY)
stop_knop.pack(pady=6)
stop_knop.set_enabled(False)  # bij opstarten is er nog niks te stoppen

# --- Log sectie -------------------------------------------------------
log_header = tk.Label(root, text="ACTIVITEIT", font=FONT_LOG_HEADER,
                      fg=COLOR_TEXT_SECONDARY, bg=COLOR_BG)
log_header.pack(anchor="w", padx=24, pady=(12, 6))

log_frame = tk.Frame(root, bg=COLOR_CARD, highlightthickness=1,
                     highlightbackground=COLOR_CARD_BORDER)
log_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

log_box = tk.Text(log_frame, bg=COLOR_LOG_BG, fg=COLOR_TEXT_SECONDARY,
                  font=("Consolas", 9), relief="flat", padx=12, pady=10,
                  wrap="word", state="disabled", borderwidth=0)
log_box.pack(fill="both", expand=True, padx=1, pady=1)

log("Klaar. Wachten op start.")

root.mainloop()
