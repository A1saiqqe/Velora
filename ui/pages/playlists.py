import tkinter as tk
from tkinter import simpledialog, messagebox
import customtkinter as ctk
from ui.theme import colors, spacing, typography

class PlaylistsPage(ctk.CTkFrame):
    def __init__(self, parent, repository, tracks=None, on_play=None):
        super().__init__(parent, fg_color=colors.BACKGROUND)
        self.repository, self.tracks, self.on_play = repository, list(tracks or []), on_play
        header = ctk.CTkFrame(self, fg_color='transparent'); header.pack(fill='x', padx=spacing.XL, pady=spacing.XL)
        ctk.CTkLabel(header, text='Playlists', font=(typography.FONT_FAMILY, 28, 'bold'), text_color=colors.TEXT_PRIMARY).pack(side='left')
        ctk.CTkButton(header, text='＋ Create playlist', command=self.create_playlist).pack(side='right')
        self.listing = ctk.CTkScrollableFrame(self, fg_color='transparent'); self.listing.pack(fill='both', expand=True, padx=spacing.XL, pady=(0, spacing.XL))
        self.refresh()
    def refresh(self):
        for child in self.listing.winfo_children(): child.destroy()
        playlists = self.repository.get_playlists()
        if not playlists:
            ctk.CTkLabel(self.listing, text='No playlists yet. Create your first one using the button above.', text_color=colors.TEXT_MUTED).pack(anchor='w', padx=8, pady=12); return
        for item in playlists:
            row = ctk.CTkFrame(self.listing, fg_color=colors.SURFACE, corner_radius=12); row.pack(fill='x', pady=4)
            ctk.CTkLabel(row, text=f"{item['name']}  ·  {item['track_count']} tracks", anchor='w', text_color=colors.TEXT_PRIMARY).pack(side='left', fill='x', expand=True, padx=14, pady=12)
            ctk.CTkButton(row, text='Add entire library', command=lambda pid=item['id']: self.add_library(pid)).pack(side='right', padx=5, pady=8)
            ctk.CTkButton(row, text='▶', width=42, command=lambda pid=item['id']: self.play_playlist(pid)).pack(side='right', padx=5, pady=8)
            ctk.CTkButton(row, text='Delete', fg_color='transparent', command=lambda pid=item['id'], name=item['name']: self.delete_playlist(pid, name)).pack(side='right', padx=5, pady=8)
    def create_playlist(self):
        name = simpledialog.askstring('New playlist', 'Playlist name:', parent=self)
        if not name or not name.strip(): return
        try: self.repository.create_playlist(name.strip())
        except ValueError as exc: messagebox.showerror('Playlists', str(exc), parent=self); return
        self.refresh()
    def add_library(self, playlist_id):
        self.repository.add_tracks_to_playlist(playlist_id, self.tracks); self.refresh()
    def play_playlist(self, playlist_id):
        tracks = self.repository.get_playlist_tracks(playlist_id)
        if tracks and self.on_play: self.on_play(tracks)
        elif not tracks: messagebox.showinfo('Playlist', 'This playlist has no tracks yet.', parent=self)
    def delete_playlist(self, playlist_id, name):
        if messagebox.askyesno('Delete playlist', f'Delete “{name}”?', parent=self):
            self.repository.delete_playlist(playlist_id); self.refresh()
