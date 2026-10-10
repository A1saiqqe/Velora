from pathlib import Path

import customtkinter as ctk

from ui.theme import colors, spacing, typography


class FoldersPage(ctk.CTkFrame):
    def __init__(self, parent, tracks=None, on_play=None):
        super().__init__(parent, fg_color=colors.BACKGROUND)
        groups = {}
        for track in tracks or []:
            raw_path = getattr(track, "file_path", "") or ""
            folder = str(Path(raw_path).parent) if raw_path else "Unknown folder"
            groups.setdefault(folder, []).append(track)
        ctk.CTkLabel(
            self, text="Folders", font=(typography.FONT_FAMILY, 28, "bold"),
            text_color=colors.TEXT_PRIMARY,
        ).pack(anchor="w", padx=spacing.XL, pady=(spacing.XL, spacing.SM))
        ctk.CTkLabel(
            self, text=f"{len(groups)} music folders", text_color=colors.TEXT_MUTED,
        ).pack(anchor="w", padx=spacing.XL, pady=(0, spacing.LG))
        listing = ctk.CTkScrollableFrame(self, fg_color="transparent")
        listing.pack(fill="both", expand=True, padx=spacing.XL, pady=(0, spacing.XL))
        if not groups:
            ctk.CTkLabel(listing, text="Music folders will appear after you scan your library.",
                         text_color=colors.TEXT_MUTED).pack(anchor="w", padx=8, pady=12)
        for folder, items in sorted(groups.items(), key=lambda pair: pair[0].casefold()):
            row = ctk.CTkFrame(listing, fg_color=colors.SURFACE, corner_radius=12)
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text="▰", width=44, text_color=colors.ACCENT,
                         font=(typography.FONT_FAMILY, 20, "bold")).pack(side="left", padx=spacing.SM, pady=spacing.SM)
            details = ctk.CTkFrame(row, fg_color="transparent")
            details.pack(side="left", fill="x", expand=True, padx=spacing.SM, pady=spacing.SM)
            ctk.CTkLabel(details, text=Path(folder).name or folder, anchor="w",
                         text_color=colors.TEXT_PRIMARY, font=(typography.FONT_FAMILY, typography.BODY_SIZE, "bold")).pack(fill="x")
            ctk.CTkLabel(details, text=f"{folder}  ·  {len(items)} tracks", anchor="w",
                         text_color=colors.TEXT_MUTED, font=(typography.FONT_FAMILY, typography.SMALL_SIZE)).pack(fill="x")
            ctk.CTkButton(row, text="Play", command=lambda group=items: on_play(group) if on_play and group else None).pack(side="right", padx=spacing.MD, pady=spacing.SM)
