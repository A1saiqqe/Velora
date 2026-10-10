import customtkinter as ctk
from tkinter import filedialog, messagebox
from ui.theme import colors, spacing, typography

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, config, on_music_directory_change=None, on_volume_change=None):
        super().__init__(parent, fg_color=colors.BACKGROUND)
        self.config = config; self.on_music_directory_change = on_music_directory_change; self.on_volume_change = on_volume_change
        ctk.CTkLabel(self, text='Settings', font=(typography.FONT_FAMILY, 28, 'bold'), text_color=colors.TEXT_PRIMARY).pack(anchor='w', padx=spacing.XL, pady=(spacing.XL, spacing.LG))
        card = ctk.CTkFrame(self, fg_color=colors.SURFACE, corner_radius=12); card.pack(fill='x', padx=spacing.XL, pady=spacing.SM)
        ctk.CTkLabel(card, text='Music folder', font=(typography.FONT_FAMILY, 16, 'bold'), text_color=colors.TEXT_PRIMARY).pack(anchor='w', padx=16, pady=(14, 4))
        self.directory = ctk.CTkLabel(card, text=self.config.get('music_directory', ''), wraplength=620, justify='left', text_color=colors.TEXT_SECONDARY); self.directory.pack(anchor='w', padx=16, pady=4)
        ctk.CTkButton(card, text='Choose folder and scan', command=self.choose_directory).pack(anchor='w', padx=16, pady=(8, 16))
        volume_card = ctk.CTkFrame(self, fg_color=colors.SURFACE, corner_radius=12); volume_card.pack(fill='x', padx=spacing.XL, pady=spacing.SM)
        ctk.CTkLabel(volume_card, text='Startup volume', font=(typography.FONT_FAMILY, 16, 'bold'), text_color=colors.TEXT_PRIMARY).pack(anchor='w', padx=16, pady=(14, 4))
        self.volume = ctk.CTkSlider(volume_card, from_=0, to=1, number_of_steps=100, command=self.change_volume); self.volume.set(float(self.config.get('volume', .7))); self.volume.pack(fill='x', padx=16, pady=8)
        self.volume_label = ctk.CTkLabel(volume_card, text=f'{int(self.volume.get()*100)}%', text_color=colors.TEXT_MUTED); self.volume_label.pack(anchor='w', padx=16, pady=(0, 14))
        ctk.CTkLabel(self, text='Velora saves settings in a local configuration file.', text_color=colors.TEXT_MUTED).pack(anchor='w', padx=spacing.XL, pady=spacing.LG)
    def choose_directory(self):
        path = filedialog.askdirectory(parent=self, title='Choose your music folder', initialdir=self.config.get('music_directory') or None)
        if not path: return
        self.config.set('music_directory', path); self.config.save(); self.directory.configure(text=path)
        if self.on_music_directory_change:
            try: count = self.on_music_directory_change(path)
            except Exception as exc: messagebox.showerror('Scanning', f'Could not scan folder:\n{exc}', parent=self); return
            messagebox.showinfo('Scan complete', f'Tracks found and added/updated: {count}', parent=self)
    def change_volume(self, value):
        value = max(0.0, min(1.0, float(value))); self.volume_label.configure(text=f'{int(value*100)}%')
        self.config.set('volume', value); self.config.save()
        if self.on_volume_change: self.on_volume_change(value)
