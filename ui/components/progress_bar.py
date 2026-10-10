import customtkinter as ctk
from ui.theme import colors, spacing, typography

class ProgressBar(ctk.CTkFrame):
    def __init__(self, parent, on_seek=None):
        super().__init__(parent, fg_color="transparent")

        self.on_seek = on_seek
        self.current = 0
        self.total = 0
        self.is_dragging = False
        self.create_progress()

    def create_progress(self):
        self.time_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.time_frame.pack(fill="x")

        self.current_time = ctk.CTkLabel(
        self.time_frame, text="0:00", text_color=colors.TEXT_MUTED,
        font=(typography.FONT_FAMILY, typography.CAPTION_SIZE))
        self.current_time.pack(side="left")

        self.total_time = ctk.CTkLabel(
        self.time_frame, text="0:00", text_color=colors.TEXT_MUTED,
        font=(typography.FONT_FAMILY, typography.CAPTION_SIZE))
        self.total_time.pack(side="right")

        self.canvas = ctk.CTkCanvas(
        self, height=18, bg=colors.BACKGROUND,
        highlightthickness=0, borderwidth=0)
        self.canvas.pack(fill="x", pady=(spacing.XS, 0))

        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Configure>", self.on_resize)

        self.draw_progress()

    def draw_progress(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()

        if width <= 1:
            return

        height = 18
        left = 4
        right = width - 4
        center_y = height / 2
        track_height = 4

        self.canvas.create_rectangle(
            left, center_y - track_height / 2,
            right, center_y + track_height / 2,
            fill=colors.SURFACE_2, outline="")

        if self.total > 0:
            progress = self.current / self.total
            progress = max(0, min(progress, 1))
            progress_x = (left + (right - left) * progress)

            self.canvas.create_rectangle(
                left, center_y - track_height / 2,
                progress_x, center_y + track_height / 2,
                fill=colors.ACCENT, outline="")

            thumb_radius = 5

            self.canvas.create_oval(
                progress_x - thumb_radius, center_y - thumb_radius,
                progress_x + thumb_radius, center_y + thumb_radius,
                fill=colors.ACCENT, outline="")

    def update_progress(self, current, total):
        if self.is_dragging:
            return

        self.total = max(0, int(total))
        self.current = max(0, min(int(current), self.total))
        self.current_time.configure(text=self.format_time(self.current))
        self.total_time.configure(text=self.format_time(self.total))
        self.draw_progress()

    def on_press(self, event):
        if self.total <= 0:
            return

        self.is_dragging = True
        position = self.position_from_x(event.x)
        self.set_preview_position(position)

    def on_drag(self, event):
        if not self.is_dragging:
            return

        position = self.position_from_x(event.x)
        self.set_preview_position(position)

    def on_release(self, event):
        if not self.is_dragging:
            return

        position = self.position_from_x(event.x)
        self.is_dragging = False
        self.current = position
        self.current_time.configure(text=self.format_time(position))
        self.draw_progress()

        if self.on_seek:
            self.on_seek(position)

    def set_preview_position(self, position):
        self.current = position
        self.current_time.configure(text=self.format_time(position))
        self.draw_progress()

    def position_from_x(self, x):
        width = self.canvas.winfo_width()
        left = 4
        right = width - 4
        if right <= left:
            return 0
        x = max(left, min(x, right))
        progress = (x - left) / (right - left)

        return int(progress * self.total)

    def on_resize(self, event=None):
        self.draw_progress()

    def reset(self):
        self.current = 0
        self.total = 0
        self.current_time.configure(text="0:00")
        self.total_time.configure(text="0:00")
        self.draw_progress()

    def format_time(self, seconds):
        minutes = seconds // 60
        remaining_seconds = seconds % 60

        return f"{minutes}:{remaining_seconds:02d}"
