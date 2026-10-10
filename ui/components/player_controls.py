import customtkinter as ctk
from ui.theme import colors, spacing
from ui.components.icon import load_icon

class PlayerControls(ctk.CTkFrame):
    def __init__(self, parent, on_play_pause=None, on_next=None, on_previous=None, on_shuffle=None, on_repeat=None):
        super().__init__(parent, fg_color="transparent")
        self.is_playing = False
        self.shuffle_enabled = False
        self.repeat_mode = "off"
        self.on_play_pause = on_play_pause
        self.on_next = on_next
        self.on_previous = on_previous
        self.on_shuffle = on_shuffle
        self.on_repeat = on_repeat
        self.create_controls()

    def create_controls(self):
        self.controls = ctk.CTkFrame(self, fg_color="transparent")
        self.controls.pack()

        self.shuffle_button = ctk.CTkButton(
            self.controls, image=load_icon("shuffle", 18),
            text="", width=40, height=40,
            fg_color="transparent",
            hover_color=colors.SURFACE_HOVER,
            corner_radius=12, command=self.toggle_shuffle)
        self.shuffle_button.pack(side="left", padx=spacing.SM)

        self.previous_button = ctk.CTkButton(
            self.controls, image=load_icon("previous", 18),
            text="", width=40, height=40,
            fg_color="transparent",
            hover_color=colors.SURFACE_HOVER,
            corner_radius=12, command=self.previous_track)
        self.previous_button.pack(side="left", padx=spacing.SM)

        self.play_icon = load_icon("play", 24)
        self.pause_icon = load_icon("pause", 24)

        self.play_button = ctk.CTkButton(
            self.controls, image=self.play_icon,
            text="", width=64, height=64,
            fg_color=colors.ACCENT,
            hover_color=colors.ACCENT_HOVER,
            corner_radius=32, command=self.toggle_playback)
        self.play_button.pack(side="left", padx=spacing.MD)

        self.next_button = ctk.CTkButton(
            self.controls, image=load_icon("next", 18),
            text="", width=40, height=40,
            fg_color="transparent",
            hover_color=colors.SURFACE_HOVER,
            corner_radius=12,command=self.next_track)
        self.next_button.pack(side="left", padx=spacing.SM)

        self.repeat_button = ctk.CTkButton(
            self.controls, image=load_icon("repeat", 18),
            text="", width=40, height=40,fg_color="transparent",
            hover_color=colors.SURFACE_HOVER,
            corner_radius=12,command=self.toggle_repeat)
        self.repeat_button.pack(side="left", padx=spacing.SM)

    def toggle_playback(self):
        if self.on_play_pause:
            self.on_play_pause()

    def toggle_shuffle(self):
        if self.on_shuffle:
            enabled = self.on_shuffle()
            if enabled is not None:
                self.set_shuffle(enabled)

    def toggle_repeat(self):
        if self.on_repeat:
            mode = self.on_repeat()
            if mode is not None:
                self.set_repeat_mode(mode)

    def set_playing(self, playing):
        self.is_playing = playing
        if self.is_playing:
            self.play_button.configure(image=self.pause_icon)
        else:
            self.play_button.configure(image=self.play_icon)

    def set_shuffle(self, enabled):
        self.shuffle_enabled = bool(enabled)
        if self.shuffle_enabled:
            self.shuffle_button.configure(fg_color=colors.ACCENT_SOFT, hover_color=colors.ACCENT_HOVER)
        else:
            self.shuffle_button.configure(fg_color="transparent", hover_color=colors.SURFACE_HOVER)

    def set_repeat_mode(self, mode):
        self.repeat_mode = mode

        if mode == "off":
            self.repeat_button.configure(fg_color="transparent", hover_color=colors.SURFACE_HOVER)
        else:
            self.repeat_button.configure(fg_color=colors.ACCENT_SOFT, hover_color=colors.ACCENT_HOVER)

    def next_track(self):
        if self.on_next:
            self.on_next()

    def previous_track(self):
        if self.on_previous:
            self.on_previous()