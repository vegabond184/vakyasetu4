import os
import customtkinter as ctk
from PIL import Image

# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------
PHOTOS_DIR = "photos"                     # folder to load images from
VALID_EXT = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
THUMB_SIZE = (220, 220)
CARD_COLS = 4


class PHOTOS:
    def __init__(self, root):
        self.root = root
        self.root.title("Photos")
        self.root.attributes("-fullscreen", True)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.root.configure(fg_color="#121212")

        # global escape: quits app only when in grid view (viewer uses
        # escape to back out to the grid instead, see _bind_viewer_keys)
        self.root.bind("<Down>", self._on_escape)

        self.photo_paths = self._load_photo_paths()
        self.current_index = None          # index into photo_paths while viewing
        self.viewer_frame = None           # overlay frame, created on demand
        self.viewer_image_label = None
        self._pending_delete_confirm = False

        self.selected_index = 0            # keyboard-selected card in grid view
        self.card_widgets = {}             # index -> card frame, for highlighting

        self._build_ui()
        self._populate_grid()

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------
    def _load_photo_paths(self):
        if not os.path.isdir(PHOTOS_DIR):
            os.makedirs(PHOTOS_DIR, exist_ok=True)
        files = [
            os.path.join(PHOTOS_DIR, f)
            for f in sorted(os.listdir(PHOTOS_DIR))
            if f.lower().endswith(VALID_EXT)
        ]
        return files

    # ------------------------------------------------------------------
    # UI CONSTRUCTION - GRID VIEW
    # ------------------------------------------------------------------
    def _build_ui(self):
        # Top bar: title
        self.top_bar = ctk.CTkFrame(self.root, fg_color="transparent", height=60)
        self.top_bar.pack(fill="x", padx=40, pady=(30, 10))

        self.app_title = ctk.CTkLabel(
            self.top_bar, text="Photo Gallery", font=("Helvetica", 22, "bold"),
            text_color="white"
        )
        self.app_title.pack(side="left")

        self.hint_label = ctk.CTkLabel(
            self.top_bar,
            text="Arrows select · Enter/Space opens · ←/→ browse photo · Del deletes · Esc back",
            font=("Helvetica", 13), text_color="#8a8a8e"
        )
        self.hint_label.pack(side="right")

        # Main scrollable frame for photo cards
        self.main_frame = ctk.CTkScrollableFrame(
            self.root, corner_radius=20, fg_color="#1c1c1e"
        )
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=20)

        for c in range(CARD_COLS):
            self.main_frame.grid_columnconfigure(c, weight=1)

        # Placeholder shown when there are no photos
        self.empty_label = ctk.CTkLabel(
            self.main_frame,
            text=f"No photos found.\nAdd images to the '{PHOTOS_DIR}' folder and restart.",
            font=("Helvetica", 18), text_color="#9ca3af"
        )

    def _populate_grid(self):
        # clear existing cards
        for child in self.main_frame.winfo_children():
            if child is not self.empty_label:
                child.destroy()
        self.card_widgets = {}

        if not self.photo_paths:
            self.empty_label.grid(row=0, column=0, columnspan=CARD_COLS, pady=80)
            self._refresh_grid_navigation()
            return
        self.empty_label.grid_forget()

        for i, path in enumerate(self.photo_paths):
            row, col = divmod(i, CARD_COLS)
            self._create_card(path, i, row, col)

        self._refresh_grid_navigation()

    def _create_card(self, path, index, row, col):
        card = ctk.CTkFrame(
            self.main_frame, corner_radius=14, fg_color="#2a2a2c",
            border_width=3, border_color="#2a2a2c"
        )
        card.grid(row=row, column=col, padx=14, pady=14, sticky="nsew")
        self.card_widgets[index] = card

        try:
            img = Image.open(path)
            img.thumbnail(THUMB_SIZE)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        except Exception:
            ctk_img = None

        thumb_label = ctk.CTkLabel(
            card, image=ctk_img, text="" if ctk_img else "⚠️ unreadable",
            width=THUMB_SIZE[0], height=THUMB_SIZE[1]
        )
        thumb_label.pack(padx=10, pady=(10, 6))

        name_label = ctk.CTkLabel(
            card, text=os.path.basename(path), font=("Helvetica", 12),
            text_color="#9ca3af"
        )
        name_label.pack(pady=(0, 10))

        # clicking anywhere on the card selects it and opens the full viewer
        for widget in (card, thumb_label, name_label):
            widget.bind("<Button-1>", lambda e, i=index: self._activate_card(i))
            widget.configure(cursor="hand2")

    def _activate_card(self, index):
        self._select(index)
        self._open_viewer(index)

    # ------------------------------------------------------------------
    # GRID KEYBOARD NAVIGATION
    # ------------------------------------------------------------------
    def _select(self, index):
        if not self.photo_paths:
            return
        self.selected_index = max(0, min(index, len(self.photo_paths) - 1))
        self._update_selection_highlight()
        self._scroll_to_selected()

    def _update_selection_highlight(self):
        for i, card in self.card_widgets.items():
            card.configure(border_color="#3b82f6" if i == self.selected_index else "#2a2a2c")

    def _scroll_to_selected(self):
        """Scroll the CTkScrollableFrame's canvas just enough to bring the
        currently-selected card fully into view."""
        card = self.card_widgets.get(self.selected_index)
        canvas = getattr(self.main_frame, "_parent_canvas", None)
        if card is None or canvas is None:
            return

        self.main_frame.update_idletasks()
        bbox = canvas.bbox("all")
        if not bbox:
            return
        total_height = bbox[3] - bbox[1]
        if total_height <= 0:
            return

        card_top = card.winfo_y()
        card_bottom = card_top + card.winfo_height()
        canvas_height = canvas.winfo_height()
        visible_top = canvas.canvasy(0)
        visible_bottom = visible_top + canvas_height

        if card_top < visible_top:
            canvas.yview_moveto(max(0, card_top / total_height))
        elif card_bottom > visible_bottom:
            canvas.yview_moveto(max(0, (card_bottom - canvas_height) / total_height))

    def _refresh_grid_navigation(self):
        """Keep selection valid and (un)bind grid arrow keys depending on
        whether the grid or the fullscreen viewer currently has focus."""
        if not self.photo_paths:
            self._unbind_grid_keys()
            return
        self.selected_index = max(0, min(self.selected_index, len(self.photo_paths) - 1))
        self._update_selection_highlight()
        self._scroll_to_selected()
        if self.current_index is None:      # viewer is closed -> grid is active
            self._bind_grid_keys()
        else:
            self._unbind_grid_keys()

    def _bind_grid_keys(self):
        # self.root.bind("<Left>", self._on_grid_left)
        self.root.bind("<Delete>", self._on_grid_right)
        # self.root.bind("<Up>", self._on_grid_up)
        # self.root.bind("<Down>", self._on_grid_down)
        self.root.bind("<Return>", self._on_grid_activate)
        # self.root.bind("<space>", self._on_grid_activate)

    def _unbind_grid_keys(self):
        for seq in ("<Left>","<Return>"):
            self.root.unbind(seq)

    def _on_grid_left(self, event=None):
        self._select((self.selected_index - 1) % len(self.photo_paths))

    def _on_grid_right(self, event=None):
        self._select((self.selected_index + 1) % len(self.photo_paths))

    def _on_grid_up(self, event=None):
        new_index = self.selected_index - CARD_COLS
        if new_index >= 0:
            self._select(new_index)

    def _on_grid_down(self, event=None):
        new_index = self.selected_index + CARD_COLS
        if new_index < len(self.photo_paths):
            self._select(new_index)

    def _on_grid_activate(self, event=None):
        self._activate_card(self.selected_index)

    # ------------------------------------------------------------------
    # FULLSCREEN VIEWER
    # ------------------------------------------------------------------
    def _open_viewer(self, index):
        self._unbind_grid_keys()
        self.current_index = index
        self._pending_delete_confirm = False

        if self.viewer_frame is None:
            self.viewer_frame = ctk.CTkFrame(self.root, fg_color="#000000")
            self.viewer_image_label = ctk.CTkLabel(self.viewer_frame, text="")
            self.viewer_image_label.pack(expand=True)

            self.viewer_status = ctk.CTkLabel(
                self.viewer_frame, text="", font=("Helvetica", 14),
                text_color="#9ca3af"
            )
            self.viewer_status.pack(side="bottom", pady=20)

        self.viewer_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.viewer_frame.lift()
        self._bind_viewer_keys()
        self._show_current_photo()

    def _close_viewer(self):
        if self.viewer_frame is not None:
            self.viewer_frame.place_forget()
        self.current_index = None
        self._unbind_viewer_keys()
        self._refresh_grid_navigation()

    def _show_current_photo(self):
        if not self.photo_paths:
            self._close_viewer()
            self._populate_grid()
            return

        # clamp index in case photos were deleted
        self.current_index = max(0, min(self.current_index, len(self.photo_paths) - 1))
        path = self.photo_paths[self.current_index]

        try:
            img = Image.open(path)
            screen_w = self.root.winfo_screenwidth() - 160
            screen_h = self.root.winfo_screenheight() - 220
            img.thumbnail((screen_w, screen_h))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.viewer_image_label.configure(image=ctk_img, text="")
        except Exception:
            self.viewer_image_label.configure(image=None, text="⚠️ Could not load image")

        self._pending_delete_confirm = False
        self.viewer_status.configure(
            text=f"{os.path.basename(path)}  ·  {self.current_index + 1}/{len(self.photo_paths)}"
        )

    # ------------------------------------------------------------------
    # KEY HANDLING
    # ------------------------------------------------------------------
    def _bind_viewer_keys(self):
        # self.root.bind("<Left>", self._on_prev)
        self.root.bind("<Delete>", self._on_next)
        # self.root.bind("<Delete>", self._on_delete)
        # self.root.bind("<BackSpace>", self._on_delete)

    def _unbind_viewer_keys(self):
        self.root.unbind("<Left>")
        self.root.unbind("<Right>")
        self.root.unbind("<Delete>")
        self.root.unbind("<BackSpace>")

    def _on_prev(self, event=None):
        if self.current_index is None:
            return
        self.current_index = (self.current_index - 1) % len(self.photo_paths)
        self._show_current_photo()

    def _on_next(self, event=None):
        if self.current_index is None:
            return
        self.current_index = (self.current_index + 1) % len(self.photo_paths)
        self._show_current_photo()

    def _on_delete(self, event=None):
        """First Delete press asks for confirmation, second press within the
        same photo confirms and deletes the file from disk."""
        if self.current_index is None:
            return

        if not self._pending_delete_confirm:
            self._pending_delete_confirm = True
            self.viewer_status.configure(
                text="Press Delete again to permanently remove this photo (Esc to cancel)",
                text_color="#ff6b6b"
            )
            return

        path = self.photo_paths[self.current_index]
        try:
            os.remove(path)
        except OSError:
            pass

        del self.photo_paths[self.current_index]
        self.viewer_status.configure(text_color="#9ca3af")

        if self.photo_paths:
            self._show_current_photo()
        else:
            self._close_viewer()

        self._populate_grid()

    def _on_escape(self, event=None):
        if self.current_index is not None:
            if self._pending_delete_confirm:
                self._pending_delete_confirm = False
                self._show_current_photo()
            else:
                self._close_viewer()
        else:
            self.root.destroy()


def main():
    app = ctk.CTk()
    PHOTOS(app)
    app.mainloop()


# if __name__ == "__main__":
#     main()