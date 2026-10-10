import customtkinter as ctk
from ui.theme import colors, spacing, typography

class AlbumsPage(ctk.CTkFrame):
    def __init__(self, parent, tracks=None, on_play=None):
        super().__init__(parent, fg_color=colors.BACKGROUND)
        tracks = list(tracks or [])
        groups = {}
        for track in tracks:
            album = (getattr(track, 'album', '') or '').strip() or 'Unknown album'
            artist = (getattr(track, 'artist', '') or '').strip() or 'Unknown artist'
            groups.setdefault((album, artist), []).append(track)
        ctk.CTkLabel(self, text='Albums', font=(typography.FONT_FAMILY, 28, 'bold'), text_color=colors.TEXT_PRIMARY).pack(anchor='w', padx=spacing.XL, pady=(spacing.XL, spacing.SM))
        ctk.CTkLabel(self, text=f'{len(groups)} albums', text_color=colors.TEXT_MUTED).pack(anchor='w', padx=spacing.XL, pady=(0, spacing.LG))
        listing = ctk.CTkScrollableFrame(self, fg_color='transparent')
        listing.pack(fill='both', expand=True, padx=spacing.XL, pady=(0, spacing.XL))
        if not groups:
            ctk.CTkLabel(listing, text='Albums will appear once you add music', text_color=colors.TEXT_MUTED).pack(anchor='w', padx=8, pady=12)
        for (album, artist), items in sorted(groups.items(), key=lambda pair: pair[0][0].casefold()):
            card = ctk.CTkFrame(listing, fg_color=colors.SURFACE, corner_radius=12)
            card.pack(fill='x', pady=4)
            label = f'{album}\n{artist} · {len(items)} tracks'
            ctk.CTkLabel(card, text=label, justify='left', anchor='w', text_color=colors.TEXT_PRIMARY).pack(side='left', fill='x', expand=True, padx=14, pady=12)
            ctk.CTkButton(card, text='Play', command=lambda group=items: on_play(group) if on_play and group else None).pack(side='right', padx=12, pady=8)
