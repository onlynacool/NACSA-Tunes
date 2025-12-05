import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pygame
import os
import json
import io
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
from PIL import Image, ImageTk, ImageDraw

class NACSATunes:
    def __init__(self, root):
        self.root = root
        self.root.title("NACSA Tunes")
        self.root.geometry("1300x750")
        self.root.configure(bg="#000000")

        pygame.mixer.init()

        # --- NEW: Attributes for app logo ---
        self.app_icon = None
        self.app_logo_photo = None
        self.load_app_logo() # Load the logo image

        # --- MODIFIED: Set the main window icon ---
        if self.app_icon:
            self.root.iconphoto(False, self.app_icon)

        self.current_folder = ""
        self.songs = []
        self.current_song_index = -1
        self.is_playing = False
        self.is_paused = False
        self.repeat_mode = "none"
        self.custom_playlists = {}
        self.current_playlist_name = "All Songs"
        self.song_length = 0
        self.current_position = 0
        self.seek_offset = 0

        self.album_art_label = None
        self.album_art_photo = None
        self.default_art_path = "default_album_art.png"
        self.create_default_album_art()

        self.setup_ui()
        self.load_playlists()
        self.update_ui()

    # --- NEW: Method to load the application logo ---
    def load_app_logo(self):
        """Loads the app_logo.png file and creates PhotoImage objects for the icon and header."""
        try:
            # Load the main icon for the window title bar
            icon_image = Image.open("app_logo.png")
            self.app_icon = ImageTk.PhotoImage(icon_image)

            # Load and resize the logo for the header
            logo_image = icon_image.resize((50, 50), Image.Resampling.LANCZOS)
            self.app_logo_photo = ImageTk.PhotoImage(logo_image)
        except FileNotFoundError:
            print("Warning: app_logo.png not found. The application will run without the logo.")
        except Exception as e:
            print(f"Error loading app_logo.png: {e}")

    def create_default_album_art(self):
        if not os.path.exists(self.default_art_path):
            try:
                img = Image.new('RGB', (300, 300), color='#1a1a1a')
                d = ImageDraw.Draw(img)
                d.text((120, 140), "No Art", fill='#00FFFF')
                img.save(self.default_art_path)
            except Exception as e:
                print(f"Could not create default album art: {e}")

    def setup_ui(self):
        try:
            self.title_font = ("Bauhaus 93", 36, "bold")
            self.text_font = ("Cascadia Code", 12)
            self.bold_text_font = ("Cascadia Code", 14, "bold")
            self.header_font = ("Cascadia Code", 16, "bold")
            self.button_font = ("Cascadia Code", 14, "bold")
            self.subtitle_font = ("Cascadia Code", 8, "italic")
            self.root.option_add("*font", self.text_font)
        except tk.TclError:
            self.title_font, self.text_font, self.bold_text_font, self.header_font, self.button_font, self.subtitle_font = ("Arial", 36, "bold"), ("Arial", 12), ("Arial", 14, "bold"), ("Arial", 16, "bold"), ("Arial", 14, "bold"), ("Arial", 8, "italic")
            self.root.option_add("*font", self.text_font)

        header_frame = tk.Frame(self.root, bg="#000000")
        header_frame.pack(fill=tk.X, pady=(10, 5), padx=20)
        
        # --- MODIFIED: Header section to include the logo ---
        # If the logo was loaded successfully, display it
        if self.app_logo_photo:
            logo_label = tk.Label(header_frame, image=self.app_logo_photo, bg="#000000")
            logo_label.pack(side=tk.LEFT, anchor='w')
            # Keep a reference to the image to prevent garbage collection
            logo_label.image = self.app_logo_photo

        title_container = tk.Frame(header_frame, bg="#000000")
        title_container.pack(side=tk.LEFT, padx=10) # Add some padding between logo and title
        app_title = tk.Label(title_container, text="NACSA Tunes", bg="#000000", fg="#00FFFF", font=self.title_font)
        app_title.pack(anchor="w")
        powered_by_label = tk.Label(title_container, text="powered by Nakul", bg="#000000", fg="grey", font=self.subtitle_font)
        powered_by_label.pack(anchor="w")

        main_frame = tk.Frame(self.root, bg="#000000")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        left_panel = tk.Frame(main_frame, bg="#000000", width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        tk.Button(left_panel, text="Select Music Folder", command=self.select_folder, bg="#1a1a1a", fg="#00FFFF", font=self.text_font).pack(pady=(10, 5), fill=tk.X)
        tk.Label(left_panel, text="PLAYLISTS", bg="#000000", fg="#00FFFF", font=self.bold_text_font).pack(pady=(20, 5), fill=tk.X)
        self.playlist_listbox = tk.Listbox(left_panel, bg="#1a1a1a", fg="white", selectbackground="#00FFFF", selectforeground="black", borderwidth=0, highlightthickness=0)
        self.playlist_listbox.pack(fill=tk.BOTH, expand=True)
        self.playlist_listbox.bind("<<ListboxSelect>>", self.on_playlist_select)
        add_playlist_frame = tk.Frame(left_panel, bg="#000000")
        add_playlist_frame.pack(pady=5, fill=tk.X)
        self.new_playlist_entry = tk.Entry(add_playlist_frame, bg="#1a1a1a", fg="white", insertbackground="white")
        self.new_playlist_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(add_playlist_frame, text="Create", command=self.create_playlist, bg="#00FFFF", fg="black").pack(side=tk.RIGHT, padx=(5,0))

        right_panel = tk.Frame(main_frame, bg="#000000")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        top_right_frame = tk.Frame(right_panel, bg="#000000")
        top_right_frame.pack(fill=tk.BOTH, expand=True)

        list_container_frame = tk.Frame(top_right_frame, bg="#000000")
        list_container_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        song_list_header_frame = tk.Frame(list_container_frame, bg="#000000")
        song_list_header_frame.pack(fill=tk.X, pady=(10, 5))
        tk.Label(song_list_header_frame, text="SONG LIBRARY", bg="#000000", fg="#00FFFF", font=self.header_font).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(song_list_header_frame, text="Sort by:", bg="#000000", fg="white").pack(side=tk.LEFT, padx=(10, 5))
        self.sort_option_menu = ttk.Combobox(song_list_header_frame, values=["Name", "Title", "Artist", "Album"], state="readonly", width=8)
        self.sort_option_menu.set("Name")
        self.sort_option_menu.pack(side=tk.LEFT)
        self.sort_option_menu.bind("<<ComboboxSelected>>", self.sort_songs)
        
        song_list_frame = tk.Frame(list_container_frame, bg="#000000")
        song_list_frame.pack(fill=tk.BOTH, expand=True)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Vertical.TScrollbar", troughcolor="#000000", background="#1a1a1a", bordercolor="#1a1a1a", arrowcolor="#00FFFF")
        self.song_listbox = tk.Listbox(song_list_frame, bg="#1a1a1a", fg="white", selectbackground="#00FFFF", selectforeground="black", borderwidth=0, highlightthickness=0)
        self.song_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.song_listbox.bind("<Double-Button-1>", self.play_selected_song)
        scrollbar = ttk.Scrollbar(song_list_frame, orient="vertical", command=self.song_listbox.yview, style="Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.song_listbox.config(yscrollcommand=scrollbar.set)

        art_frame = tk.Frame(top_right_frame, bg="#000000")
        art_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0), pady=(10, 0))
        self.album_art_label = tk.Label(art_frame, bg="#000000")
        self.album_art_label.pack()
        self.update_album_art(None)

        controls_container = tk.Frame(right_panel, bg="#000000")
        controls_container.pack(fill=tk.X, pady=(10, 0))
        metadata_frame = tk.Frame(controls_container, bg="#000000")
        metadata_frame.pack(fill=tk.X, pady=5)
        self.current_song_label = tk.Label(metadata_frame, text="No song selected", bg="#000000", fg="#00FFFF", font=self.bold_text_font, wraplength=800, anchor="w")
        self.current_song_label.pack(fill=tk.X, pady=(0, 5))
        self.metadata_label = tk.Label(metadata_frame, text="Artist: N/A | Album: N/A", bg="#000000", fg="white", anchor="w", wraplength=800)
        self.metadata_label.pack(fill=tk.X)
        style.configure("TProgressbar", background="#00FFFF", troughcolor="#1a1a1a", borderwidth=0, relief="flat")
        self.progress_bar = ttk.Progressbar(controls_container, orient="horizontal", mode="determinate", style="TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        self.progress_bar.config(maximum=100)
        self.progress_bar.bind("<Button-1>", self.seek_song)
        time_frame = tk.Frame(controls_container, bg="#000000")
        time_frame.pack(fill=tk.X)
        self.current_time_label = tk.Label(time_frame, text="0:00", bg="#000000", fg="white")
        self.current_time_label.pack(side=tk.LEFT)
        self.total_time_label = tk.Label(time_frame, text="0:00", bg="#000000", fg="white")
        self.total_time_label.pack(side=tk.RIGHT)
        central_controls_frame = tk.Frame(controls_container, bg="#000000")
        central_controls_frame.pack(pady=15)
        tk.Button(central_controls_frame, text="Add to Playlist", command=self.add_to_playlist, bg="#1a1a1a", fg="#00FFFF", font=self.button_font).pack(side=tk.LEFT, padx=15)
        tk.Button(central_controls_frame, text="⏮️", command=self.play_previous, bg="#1a1a1a", fg="#00FFFF", font=("Arial", 16), width=3).pack(side=tk.LEFT, padx=10)
        self.play_pause_btn = tk.Button(central_controls_frame, text="▶️", command=self.toggle_play_pause, bg="#00FFFF", fg="black", font=("Arial", 16), width=3)
        self.play_pause_btn.pack(side=tk.LEFT, padx=10)
        tk.Button(central_controls_frame, text="⏭️", command=self.play_next, bg="#1a1a1a", fg="#00FFFF", font=("Arial", 16), width=3).pack(side=tk.LEFT, padx=10)
        self.repeat_btn = tk.Button(central_controls_frame, text="🔁", command=self.toggle_repeat, bg="#1a1a1a", fg="#00FFFF", font=("Arial", 16), width=3)
        self.repeat_btn.pack(side=tk.LEFT, padx=10)
        tk.Button(central_controls_frame, text="🔀", command=self.shuffle_songs, bg="#1a1a1a", fg="#00FFFF", font=("Arial", 16), width=3).pack(side=tk.LEFT, padx=10)
        volume_frame = tk.Frame(central_controls_frame, bg="#000000")
        volume_frame.pack(side=tk.LEFT, padx=15)
        tk.Label(volume_frame, text="Volume", bg="#000000", fg="white").pack(side=tk.LEFT, padx=5)
        style.configure("TScale", background="#000000", troughcolor="#1a1a1a", sliderrelief="flat")
        self.volume_slider = ttk.Scale(volume_frame, from_=0, to=1, orient="horizontal", command=self.set_volume, style="TScale")
        self.volume_slider.set(0.5)
        pygame.mixer.music.set_volume(0.5)
        self.volume_slider.pack(side=tk.LEFT, padx=5)

    def update_ui(self):
        if self.is_playing and not pygame.mixer.music.get_busy():
            self.handle_song_end()
        elif self.is_playing:
            raw_pos = pygame.mixer.music.get_pos() / 1000
            self.current_position = self.seek_offset + raw_pos
            self.current_position = min(self.current_position, self.song_length) if self.song_length > 0 else 0
            if self.song_length > 0:
                progress_percentage = (self.current_position / self.song_length) * 100
                self.progress_bar.config(value=progress_percentage)
            minutes, seconds = divmod(int(self.current_position), 60)
            self.current_time_label.config(text=f"{minutes}:{seconds:02d}")
        self.root.after(200, self.update_ui)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.current_folder = folder_path
            self.load_songs_from_folder()

    def load_songs_from_folder(self):
        self.songs.clear()
        if self.current_folder:
            supported_formats = (".mp3",)
            for filename in os.listdir(self.current_folder):
                if filename.endswith(supported_formats):
                    path = os.path.join(self.current_folder, filename)
                    try:
                        audio = ID3(path)
                        title = audio.get('TIT2', [filename])[0]
                        artist = audio.get('TPE1', ['Unknown Artist'])[0]
                        album = audio.get('TALB', ['Unknown Album'])[0]
                    except Exception:
                        title, artist, album = filename, "Unknown Artist", "Unknown Album"
                    self.songs.append({'filename': filename, 'path': path, 'title': title, 'artist': artist, 'album': album})
        if not self.songs and self.current_folder:
            messagebox.showinfo("NACSA Tunes", "No supported MP3 files found for sorting.")
        self.sort_songs()
        self.current_playlist_name = "All Songs"
        self.populate_playlists()

    def update_listbox(self):
        self.song_listbox.delete(0, tk.END)
        for song in self.songs:
            self.song_listbox.insert(tk.END, song['title'] if song['title'] != song['filename'] else song['filename'])

    def sort_songs(self, event=None):
        sort_by = self.sort_option_menu.get()
        sort_key = {'Name': 'filename', 'Title': 'title', 'Artist': 'artist', 'Album': 'album'}.get(sort_by, 'filename')
        self.songs.sort(key=lambda x: str(x[sort_key]).lower())
        self.update_listbox()
        pygame.mixer.music.stop()
        self.is_playing, self.is_paused = False, False
        self.play_pause_btn.config(text="▶️")
        self.current_song_label.config(text="No song selected")
        self.metadata_label.config(text="Artist: N/A | Album: N/A")
        self.progress_bar.config(value=0)
        self.current_time_label.config(text="0:00")
        self.total_time_label.config(text="0:00")
        self.update_album_art(None)

    def play_song(self, song_index, start_pos=0):
        if not self.songs or not (0 <= song_index < len(self.songs)):
            return
        self.current_song_index = song_index
        song_data = self.songs[self.current_song_index]
        try:
            pygame.mixer.music.load(song_data['path'])
            self.seek_offset = start_pos
            pygame.mixer.music.play(start=start_pos)
            self.is_playing, self.is_paused = True, False
            self.play_pause_btn.config(text="⏸️")
            self.update_song_info(song_data)
        except pygame.error as e:
            messagebox.showerror("Playback Error", f"Could not play {song_data['filename']}: {e}")

    def update_song_info(self, song_data):
        self.current_song_label.config(text=song_data['title'])
        self.metadata_label.config(text=f"ARTIST: {song_data['artist']} | ALBUM: {song_data['album']}")
        self.get_song_length(song_data['path'])
        self.update_album_art(song_data['path'])

    def get_song_length(self, full_path):
        try:
            self.song_length = MP3(full_path).info.length
            minutes, seconds = divmod(int(self.song_length), 60)
            self.total_time_label.config(text=f"{minutes}:{seconds:02d}")
        except Exception:
            self.song_length = 0
            self.total_time_label.config(text="0:00")

    def update_album_art(self, full_path):
        try:
            image_data = None
            if full_path:
                audio = ID3(full_path)
                image_data = next((tag.data for key, tag in audio.items() if key.startswith("APIC")), None)
            if image_data:
                img = Image.open(io.BytesIO(image_data))
            else:
                img = Image.open(self.default_art_path)
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            self.album_art_photo = ImageTk.PhotoImage(img)
            self.album_art_label.config(image=self.album_art_photo)
            self.album_art_label.image = self.album_art_photo
        except Exception:
            img = Image.open(self.default_art_path)
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            self.album_art_photo = ImageTk.PhotoImage(img)
            self.album_art_label.config(image=self.album_art_photo)
            self.album_art_label.image = self.album_art_photo

    def seek_song(self, event):
        if self.song_length > 0 and (self.is_playing or self.is_paused):
            bar_width = self.progress_bar.winfo_width()
            if bar_width > 0:
                was_paused = self.is_paused
                new_time = (event.x / bar_width) * self.song_length
                self.play_song(self.current_song_index, start_pos=new_time)
                if was_paused:
                    pygame.mixer.music.pause()
                    self.is_playing, self.is_paused = False, True
                    self.play_pause_btn.config(text="▶️")

    def toggle_play_pause(self):
        if not pygame.mixer.music.get_busy() and not self.is_paused:
            if self.songs: self.play_song(0)
            return
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_paused, self.is_playing = True, False
            self.play_pause_btn.config(text="▶️")
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused, self.is_playing = False, True
            self.play_pause_btn.config(text="⏸️")

    def play_selected_song(self, event=None):
        selected_index = self.song_listbox.curselection()
        if selected_index: self.play_song(selected_index[0])

    def play_next(self):
        if not self.songs: return
        next_index = self.current_song_index + 1 if self.current_song_index != -1 else 0
        if next_index >= len(self.songs): next_index = 0
        self.play_song(next_index)

    def play_previous(self):
        if not self.songs: return
        prev_index = self.current_song_index - 1
        if prev_index < 0: prev_index = len(self.songs) - 1
        self.play_song(prev_index)
        
    def handle_song_end(self):
        if self.repeat_mode == "one":
            self.play_song(self.current_song_index)
        elif self.repeat_mode == "all":
            self.play_next()
        else:
            if self.current_song_index < len(self.songs) - 1:
                self.play_next()
            else:
                self.is_playing = False
                self.play_pause_btn.config(text="▶️")
                self.current_song_label.config(text="Playlist Finished")
                self.progress_bar.config(value=0)
                self.current_time_label.config(text="0:00")

    def toggle_repeat(self):
        if self.repeat_mode == "none":
            self.repeat_mode, text = "all", "Repeat All: The current playlist will loop."
            self.repeat_btn.config(text="🔁:")
        elif self.repeat_mode == "all":
            self.repeat_mode, text = "one", "Repeat One: The current song will repeat."
            self.repeat_btn.config(text="🔂1")
        else:
            self.repeat_mode, text = "none", "Repeat is off."
            self.repeat_btn.config(text="🔁")
        messagebox.showinfo("Repeat Mode", text)

    def shuffle_songs(self):
        import random
        if self.songs:
            random.shuffle(self.songs)
            self.update_listbox()
            messagebox.showinfo("Shuffle", "Current queue has been shuffled.")

    def set_volume(self, value):
        pygame.mixer.music.set_volume(float(value))

    def load_playlists(self):
        try:
            with open("playlists.json", "r") as f: self.custom_playlists = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): self.custom_playlists = {}
        self.populate_playlists()

    def save_playlists(self):
        with open("playlists.json", "w") as f: json.dump(self.custom_playlists, f, indent=4)

    def populate_playlists(self):
        self.playlist_listbox.delete(0, tk.END)
        self.playlist_listbox.insert(tk.END, "All Songs")
        for playlist_name in self.custom_playlists.keys(): self.playlist_listbox.insert(tk.END, playlist_name)

    def create_playlist(self):
        playlist_name = self.new_playlist_entry.get().strip()
        if playlist_name and playlist_name not in self.custom_playlists and playlist_name != "All Songs":
            self.custom_playlists[playlist_name] = []
            self.new_playlist_entry.delete(0, tk.END)
            self.save_playlists()
            self.populate_playlists()
            messagebox.showinfo("Playlist", f"Playlist '{playlist_name}' created.")
        else: messagebox.showerror("Error", "Invalid or existing playlist name.")

    def on_playlist_select(self, event):
        selected_index = self.playlist_listbox.curselection()
        if not selected_index: return
        selected_playlist_name = self.playlist_listbox.get(selected_index[0])
        self.current_playlist_name = selected_playlist_name
        self.load_songs_from_folder() 
        if selected_playlist_name != "All Songs":
            playlist_filenames = self.custom_playlists.get(selected_playlist_name, [])
            self.songs = [s for s in self.songs if s['filename'] in playlist_filenames]
        self.sort_songs()

    def add_to_playlist(self):
        song_index_tuple = self.song_listbox.curselection()
        if not song_index_tuple:
            messagebox.showerror("Error", "Please select a song to add.")
            return
        
        song_data = self.songs[song_index_tuple[0]]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Manage Playlists")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.configure(bg="#1a1a1a")

        # --- MODIFIED: Set the playlist dialog window icon ---
        if self.app_icon:
            dialog.iconphoto(False, self.app_icon)
        
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        dialog_x = root_x + (root_width - 400) // 2
        dialog_y = root_y + (root_height - 350) // 2
        dialog.geometry(f"+{dialog_x}+{dialog_y}")
        
        tk.Label(dialog, text=f"Add '{song_data['title'][:30]}...' to:", bg="#1a1a1a", fg="white", font=self.text_font).pack(pady=(10, 5))
        
        playlist_frame = tk.Frame(dialog, bg="#1a1a1a")
        playlist_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        dialog_playlist_box = tk.Listbox(playlist_frame, bg="#333333", fg="white", selectbackground="#00FFFF", selectforeground="black")
        dialog_playlist_box.pack(fill=tk.BOTH, expand=True)
        
        custom_playlists = list(self.custom_playlists.keys())
        if not custom_playlists:
            dialog_playlist_box.insert(tk.END, "No custom playlists found.")
            dialog_playlist_box.config(state="disabled")
        else:
            for p_name in custom_playlists:
                dialog_playlist_box.insert(tk.END, p_name)

        def confirm_add():
            selected_playlist_tuple = dialog_playlist_box.curselection()
            if not selected_playlist_tuple:
                messagebox.showerror("Error", "Please select a playlist to add the song to.", parent=dialog)
                return
            
            playlist_name = dialog_playlist_box.get(selected_playlist_tuple[0])
            song_filename = song_data['filename']

            if song_filename not in self.custom_playlists[playlist_name]:
                self.custom_playlists[playlist_name].append(song_filename)
                self.save_playlists()
                messagebox.showinfo("Success", f"Added to '{playlist_name}'.", parent=dialog)
            else:
                messagebox.showinfo("Info", f"Song is already in '{playlist_name}'.", parent=dialog)
            dialog.destroy()

        def refresh_dialog_list():
            dialog_playlist_box.delete(0, tk.END)
            updated_custom_playlists = list(self.custom_playlists.keys())
            if not updated_custom_playlists:
                dialog_playlist_box.insert(tk.END, "No custom playlists found.")
                dialog_playlist_box.config(state="disabled")
            else:
                for p_name in updated_custom_playlists:
                    dialog_playlist_box.insert(tk.END, p_name)
        
        button_frame = tk.Frame(dialog, bg="#1a1a1a")
        button_frame.pack(pady=10, fill=tk.X, padx=10)
        
        add_btn = tk.Button(button_frame, text="Add Song", command=confirm_add, bg="#00FFFF", fg="black")
        add_btn.pack(side=tk.LEFT, expand=True, padx=5)

        delete_btn = tk.Button(button_frame, text="Delete Playlist", command=lambda: self._confirm_delete_playlist(dialog, dialog_playlist_box, refresh_dialog_list), bg="#500000", fg="white")
        delete_btn.pack(side=tk.LEFT, expand=True, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=dialog.destroy, bg="#333333", fg="white")
        cancel_btn.pack(side=tk.RIGHT, expand=True, padx=5)

    def _confirm_delete_playlist(self, parent_dialog, listbox, refresh_callback):
        selected_playlist_tuple = listbox.curselection()
        if not selected_playlist_tuple:
            messagebox.showerror("Error", "Please select a playlist to delete.", parent=parent_dialog)
            return

        playlist_name = listbox.get(selected_playlist_tuple[0])

        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete the playlist '{playlist_name}'?\nThis cannot be undone.", parent=parent_dialog):
            if playlist_name in self.custom_playlists:
                del self.custom_playlists[playlist_name]
                self.save_playlists()
                self.populate_playlists()
                refresh_callback()
                messagebox.showinfo("Success", f"Playlist '{playlist_name}' has been deleted.", parent=parent_dialog)


if __name__ == "__main__":
    root = tk.Tk()
    app = NACSATunes(root)
    root.mainloop()
