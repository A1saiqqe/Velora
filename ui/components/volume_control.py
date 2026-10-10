import customtkinter as ctk
from ui.theme import colors, spacing, typography
from ui.components.icon import load_icon


class VolumeControl(ctk.CTkFrame):
    def __init__(self, parent, on_volume_change=None):
        super().__init__(parent, fg_color="transparent")

        self.on_volume_change = on_volume_change
        self.volume = 1.0
        self.previous_volume = 1.0
        self.is_muted = False

        self.create_control()

    def create_control(self):
        self.volume_button = ctk.CTkButton(
            self, image=load_icon("volume", 18), text="",
            width=40, height=40, fg_color="transparent",
            hover_color=colors.SURFACE_HOVER,
            corner_radius=12, command=self.toggle_mute)
        self.volume_button.pack(side="left", padx=(0, spacing.SM))

        self.volume_label = ctk.CTkLabel(
            self, text="100%", text_color=colors.TEXT_SECONDARY,
            font=(typography.FONT_FAMILY, typography.CAPTION_SIZE), width=40)
        self.volume_label.pack(side="left", padx=(0, spacing.SM))

        self.volume_slider = ctk.CTkSlider(
            self, from_=0, to=1, width=120, height=16,
            fg_color=colors.SURFACE_2, progress_color=colors.ACCENT, button_color=colors.ACCENT,
            button_hover_color=colors.ACCENT_HOVER, command=self.on_slider_change)
        self.volume_slider.pack(side="left")
        self.volume_slider.set(self.volume)

    def on_slider_change(self, value):
        self.volume = max(0.0, min(1.0, float(value)))

        if self.volume > 0:
            self.previous_volume = self.volume
            self.is_muted = False

            self.volume_button.configure(image=load_icon("volume", 18))
        else:
            self.is_muted = True
            self.volume_button.configure(image=load_icon("mute", 18))

        self.update_label()

        if self.on_volume_change:
            self.on_volume_change(self.volume)

    def toggle_mute(self):
        if self.is_muted:
            self.volume = self.previous_volume

            if self.volume <= 0:
                self.volume = 1.0

            self.is_muted = False
            self.volume_button.configure(image=load_icon("volume", 18))

        else:
            if self.volume > 0:
                self.previous_volume = self.volume

            self.volume = 0.0
            self.is_muted = True

            self.volume_button.configure(image=load_icon("mute", 18))

        self.volume_slider.set(self.volume)
        self.update_label()

        if self.on_volume_change:
            self.on_volume_change(self.volume)

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, float(volume)))
        if self.volume > 0:
            self.previous_volume = self.volume
            self.is_muted = False

            self.volume_button.configure(image=load_icon("volume", 18))
        else:
            self.is_muted = True
            self.volume_button.configure(image=load_icon("mute", 18))

        self.volume_slider.set(self.volume)
        self.update_label()

    def update_label(self):
        percentage = int(self.volume * 100)
        self.volume_label.configure(text=f"{percentage}%")