readme:
  title: "🎵 NACSA Tunes — Offline Python Music Player"

  intro: |
    NACSA Tunes is a modern offline MP3 music player built in Python.
    It supports playlist management, album art extraction, ID3 metadata,
    shuffle & repeat modes, volume control, and a clean Tkinter-based UI.

  features: |
    ## ⭐ Features
    - 🎧 Play MP3 files
    - 📂 Select any folder as your music library
    - 🏷️ Read ID3 metadata (Title / Artist / Album)
    - 🖼️ Display embedded album art (APIC)
    - 🎚️ Volume slider + Seek bar
    - 🔁 Repeat (One / All / Off)
    - 🔀 Shuffle mode
    - 📜 Create & delete custom playlists
    - 🌙 Dark themed UI
    - 🖼️ Optional app icon (app_logo.png)

  prerequisites: |
    ## 🚀 Prerequisites

    ### 1. Check Python Version
    ```bash
    python --version
    ```

    ### 2. Required Python Libraries
    - pygame  
    - mutagen  
    - pillow  
    - tkinter *(default in Python installs)*  

    ### 3. OS Support
    | OS      | Support |
    |---------|---------|
    | Windows | ✔️ Full |
    | Linux   | ✔️ Needs Tkinter |
    | macOS   | ✔️ pygame may need SDL |

  installation: |
    ## 📦 Installation

    ### Clone Repository
    ```bash
    git clone https://github.com/your-username/nacsa-tunes.git
    cd nacsa-tunes
    ```

    ### Install Dependencies
    ```bash
    pip install pygame mutagen pillow
    ```

    ### Install Tkinter if missing

    **Ubuntu / Debian**
    ```bash
    sudo apt install python3-tk
    ```

    **Fedora**
    ```bash
    sudo dnf install python3-tkinter
    ```

    **Arch Linux**
    ```bash
    sudo pacman -S tk
    ```

    **macOS**
    ```bash
    brew install python-tk
    ```

  running: |
    ## ▶️ Run the App
    ```bash
    python nacsa_tunes.py
    ```

  structure: |
    ## 📁 Project Structure
    ```
    nacsa-tunes/
    ├── nacsa_tunes.py
    ├── playlists.json           (auto-generated)
    ├── app_logo.png             (optional)
    ├── default_album_art.png    (auto-generated)
    └── README.md
    ```

  logo: |
    ## 🖼️ Optional App Logo
    Add a file named:
    ```
    app_logo.png
    ```
    in the root folder.
    If missing, the app loads without a logo.

  playlist_info: |
    ## 💾 Playlist Storage
    Playlists are saved inside:
    ```
    playlists.json
    ```

    Example:
    ```json
    {
      "My Favorites": ["song1.mp3", "song2.mp3"]
    }
    ```

  tech: |
    ## 🛠️ Technologies Used
    - Python
    - Tkinter
    - Pygame
    - Mutagen
    - Pillow (PIL)

  contributing: |
    ## 🤝 Contributing
    Pull requests are welcome. You may enhance:
    - UI / Theme improvements  
    - More audio formats  
    - Export / Import playlists  
    - Windows .exe packaging (PyInstaller)

  license: |
    ## 📜 License
    MIT License — free to use & modify.

  closing: |
    ---
    Enjoy your music! 🎵
