import customtkinter as ctk

from ui.theme import colors, spacing, typography


class GenresPage(ctk.CTkFrame):
    def __init__(self, parent, tracks=None, on_play=None):
        super().__init__(parent, fg_color=colors.BACKGROUND)
        groups = {}
        for track in tracks or []:
            genre = (getattr(track, "genre", "") or "").strip() or "Unknown genre"
            groups.setdefault(genre, []).append(track)
        ctk.CTkLabel(
            self, text="Genres", font=(typography.FONT_FAMILY, 28, "bold"),
            text_color=colors.TEXT_PRIMARY,
        ).pack(anchor="w", padx=spacing.XL, pady=(spacing.XL, spacing.SM))
        ctk.CTkLabel(
            self, text=f"{len(groups)} genres", text_color=colors.TEXT_MUTED,
        ).pack(anchor="w", padx=spacing.XL, pady=(0, spacing.LG))
        listing = ctk.CTkScrollableFrame(self, fg_color="transparent")
        listing.pack(fill="both", expand=True, padx=spacing.XL, pady=(0, spacing.XL))
        if not groups:
            ctk.CTkLabel(listing, text="Genres will appear when metadata is available in your music files.",
                         text_color=colors.TEXT_MUTED, wraplength=600).pack(anchor="w", padx=8, pady=12)
        for genre, items in sorted(groups.items(), key=lambda pair: pair[0].casefold()):
            row = ctk.CTkFrame(listing, fg_color=colors.SURFACE, corner_radius=12)
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text="♫", width=44, text_color=colors.ACCENT,
                         font=(typography.FONT_FAMILY, 22, "bold")).pack(side="left", padx=spacing.SM, pady=spacing.SM)
            ctk.CTkLabel(row, text=f"{genre}\n{len(items)} tracks", anchor="w", justify="left",
                         text_color=colors.TEXT_PRIMARY).pack(side="left", fill="x", expand=True, padx=spacing.SM, pady=spacing.MD)
            ctk.CTkButton(row, text="Play", command=lambda group=items: on_play(group) if on_play and group else None).pack(side="right", padx=spacing.MD, pady=spacing.SM)
