import customtkinter as ctk
from ui.theme import colors, spacing, typography

class ArtistsPage(ctk.CTkFrame):
    def __init__(self, parent, tracks=None, on_play=None):
        super().__init__(parent, fg_color=colors.BACKGROUND)
        groups = {}
        for track in tracks or []:
            artist = (getattr(track, 'artist', '') or '').strip() or 'Unknown artist'
            groups.setdefault(artist, []).append(track)
        ctk.CTkLabel(self, text='Artists', font=(typography.FONT_FAMILY, 28, 'bold'), text_color=colors.TEXT_PRIMARY).pack(anchor='w', padx=spacing.XL, pady=(spacing.XL, spacing.SM))
        ctk.CTkLabel(self, text=f'{len(groups)} artists', text_color=colors.TEXT_MUTED).pack(anchor='w', padx=spacing.XL, pady=(0, spacing.LG))
        listing = ctk.CTkScrollableFrame(self, fg_color='transparent')
        listing.pack(fill='both', expand=True, padx=spacing.XL, pady=(0, spacing.XL))
        if not groups:
            ctk.CTkLabel(listing, text='Artists will appear once you add music', text_color=colors.TEXT_MUTED).pack(anchor='w', padx=8, pady=12)
        for artist, items in sorted(groups.items(), key=lambda pair: pair[0].casefold()):
            row = ctk.CTkFrame(listing, fg_color=colors.SURFACE, corner_radius=12)
            row.pack(fill='x', pady=4)
            ctk.CTkLabel(row, text=f'{artist}  ·  {len(items)} tracks', anchor='w', text_color=colors.TEXT_PRIMARY).pack(side='left', fill='x', expand=True, padx=14, pady=12)
            ctk.CTkButton(row, text='Play', command=lambda group=items: on_play(group) if on_play and group else None).pack(side='right', padx=12, pady=8)
