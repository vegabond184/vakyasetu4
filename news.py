import customtkinter as ctk
import requests
import threading

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
API_KEY = "d68381765b2148cdbf983e93b3d611c9"   # <-- put your newsapi.org key here
COUNTRY = "us"                       # e.g. "us", "in", "gb"
CATEGORY = "general"                 # business, entertainment, general,
                                      # health, science, sports, technology
PAGE_SIZE = 20

TITLE_FONT = ("Helvetica", 34, "bold")
BODY_FONT = ("Helvetica", 18)
META_FONT = ("Helvetica", 14)

BG_COLOR = "#121212"
CARD_COLOR = "#1c1c1e"
ACCENT_COLOR = "#3b82f6"
MUTED_TEXT = "#9ca3af"


class NEWS:
    def __init__(self, root):
        self.root = root
        self.root.title("News")
        self.root.attributes("-fullscreen", True)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.root.configure(fg_color=BG_COLOR)

        self.articles = []
        self.index = 0

        self._build_ui()
        self._bind_keys()
        self._load_news_async()

    # ------------------------------------------------------------------
    # UI CONSTRUCTION
    # ------------------------------------------------------------------
    def _build_ui(self):
        # Top bar: title + progress indicator
        self.top_bar = ctk.CTkFrame(self.root, fg_color="transparent", height=60)
        self.top_bar.pack(fill="x", padx=40, pady=(30, 10))

        self.app_title = ctk.CTkLabel(
            self.top_bar, text="Today's News", font=("Helvetica", 22, "bold"),
            text_color="white"
        )
        self.app_title.pack(side="left")

        self.progress_label = ctk.CTkLabel(
            self.top_bar, text="", font=META_FONT, text_color=MUTED_TEXT
        )
        self.progress_label.pack(side="right")

        # Main card
        self.main_frame = ctk.CTkFrame(
            self.root, corner_radius=20, fg_color=CARD_COLOR
        )
        self.main_frame.pack(expand=True, fill="both", padx=40, pady=(10, 20))

        # Source / date meta row
        self.meta_label = ctk.CTkLabel(
            self.main_frame, text="", font=META_FONT, text_color=ACCENT_COLOR
        )
        self.meta_label.pack(pady=(170, 6))

        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame, text="Loading news...", font=TITLE_FONT,
            text_color="white", wraplength=1000, justify="center"
        )
        self.title_label.pack(padx=60, pady=(0, 16))

        # Description
        self.desc_label = ctk.CTkLabel(
            self.main_frame, text="", font=BODY_FONT, text_color="#d1d5db",
            wraplength=1000, justify="center"
        )
        self.desc_label.pack(padx=60, pady=(0, 20))

        # Bottom hint bar
        self.hint_label = ctk.CTkLabel(
            self.root,
            text="Delete = Next    •    Enter = Previous    •    Esc = Quit",
            font=META_FONT, text_color=MUTED_TEXT
        )
        self.hint_label.pack(pady=(0, 20))

    def _bind_keys(self):
        self.root.bind("<Delete>", self.next_news)
        self.root.bind("<Return>", self.prev_news)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    # ------------------------------------------------------------------
    # DATA FETCH
    # ------------------------------------------------------------------
    def _load_news_async(self):
        """Fetch headlines in a background thread so the UI never freezes."""
        threading.Thread(target=self._fetch_news, daemon=True).start()

    def _fetch_news(self):
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": COUNTRY,
            "category": CATEGORY,
            "pageSize": PAGE_SIZE,
            "apiKey": API_KEY,
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") != "ok":
                raise ValueError(data.get("message", "Unknown API error"))

            # Keep only articles that have at least a title
            self.articles = [
                a for a in data.get("articles", [])
                if a.get("title") and a.get("title") != "[Removed]"
            ]

            if not self.articles:
                raise ValueError("No articles returned.")

            self.index = 0
            self.root.after(0, self._render_current)

        except Exception as e:
            self.root.after(0, lambda: self._show_error(str(e)))

    def _show_error(self, message):
        self.title_label.configure(text="Couldn't load news")
        self.desc_label.configure(text=message)
        self.meta_label.configure(text="")
        self.progress_label.configure(text="")

    # ------------------------------------------------------------------
    # RENDERING
    # ------------------------------------------------------------------
    def _render_current(self):
        if not self.articles:
            return

        article = self.articles[self.index]

        self.title_label.configure(text=article.get("title", "Untitled"))
        self.desc_label.configure(
            text=article.get("description") or "No description available."
        )

        source = article.get("source", {}).get("name", "Unknown source")
        published = (article.get("publishedAt") or "")[:10]
        self.meta_label.configure(text=f"{source}   •   {published}")

        self.progress_label.configure(
            text=f"{self.index + 1} / {len(self.articles)}"
        )

    # ------------------------------------------------------------------
    # NAVIGATION
    # ------------------------------------------------------------------
    def next_news(self, event=None):
        if not self.articles:
            return
        self.index = (self.index + 1) % len(self.articles)
        self._render_current()

    def prev_news(self, event=None):
        if not self.articles:
            return
        self.index = (self.index - 1) % len(self.articles)
        self._render_current()


def main():
    app = ctk.CTk()
    NEWS(app)
    app.mainloop()


# if __name__ == "__main__":
#     main()