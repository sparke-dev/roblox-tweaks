import os
import shutil
import subprocess
import customtkinter as ctk

# --- PATH CONFIGURATION ---
FLAGS_BASE_DIR = os.path.expanduser("~/fastflags")
REPO_DIR = os.path.expanduser("~/projects/demstrap-backup")
DEST_FILE = os.path.join(REPO_DIR, "client_settings.json")

# --- GUI SETUP ---
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

class FastFlagManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FastFlag Config Manager")
        self.geometry("500x420")
        self.resizable(False, False)

        # Define Fonts (JetBrains Mono Nerd Font)
        self.title_font = ctk.CTkFont(family="JetBrainsMono Nerd Font", size=22, weight="bold")
        self.main_font = ctk.CTkFont(family="JetBrainsMono Nerd Font", size=14)
        self.small_font = ctk.CTkFont(family="JetBrainsMono Nerd Font", size=12)

        # --- UI LAYOUT ---
        self.header = ctk.CTkLabel(self, text="⚡ FastFlag Manager", font=self.title_font)
        self.header.pack(pady=(25, 15))

        # Category (Folder) Dropdown
        self.folder_label = ctk.CTkLabel(self, text="Select Category Folder:", font=self.main_font)
        self.folder_label.pack(anchor="w", padx=40)
        
        self.folder_var = ctk.StringVar(value="Select Folder...")
        self.folder_dropdown = ctk.CTkOptionMenu(self, variable=self.folder_var, command=self.update_file_dropdown, font=self.main_font)
        self.folder_dropdown.pack(fill="x", padx=40, pady=(0, 15))

        # Preset (File) Dropdown
        self.file_label = ctk.CTkLabel(self, text="Select Flag Preset:", font=self.main_font)
        self.file_label.pack(anchor="w", padx=40)

        self.file_var = ctk.StringVar(value="Select File...")
        self.file_dropdown = ctk.CTkOptionMenu(self, variable=self.file_var, font=self.main_font)
        self.file_dropdown.pack(fill="x", padx=40, pady=(0, 25))

        # Push Button
        self.push_btn = ctk.CTkButton(self, text="Apply & Push to GitHub", command=self.apply_and_push, font=self.main_font, height=40)
        self.push_btn.pack(fill="x", padx=40)

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="Ready.", font=self.small_font, text_color="gray")
        self.status_label.pack(pady=(20, 0))

        # Initialize Data
        self.load_folders()

    def load_folders(self):
        """Scans the base directory for folders."""
        if not os.path.exists(FLAGS_BASE_DIR):
            os.makedirs(FLAGS_BASE_DIR)
            
        folders = [f for f in os.listdir(FLAGS_BASE_DIR) if os.path.isdir(os.path.join(FLAGS_BASE_DIR, f))]
        
        if folders:
            self.folder_dropdown.configure(values=folders)
            self.folder_var.set(folders[0])
            self.update_file_dropdown(folders[0])
        else:
            self.folder_dropdown.configure(values=["No folders found"])
            self.file_dropdown.configure(values=["No files found"])

    def update_file_dropdown(self, selected_folder):
        """Updates the file dropdown based on the selected folder."""
        folder_path = os.path.join(FLAGS_BASE_DIR, selected_folder)
        files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

        if files:
            self.file_dropdown.configure(values=files)
            self.file_var.set(files[0])
        else:
            self.file_dropdown.configure(values=["No .json files found"])
            self.file_var.set("No files found")

    def apply_and_push(self):
        """Copies the selected preset and pushes to GitHub."""
        selected_folder = self.folder_var.get()
        selected_file = self.file_var.get()

        if "No " in selected_folder or "No " in selected_file:
            self.status_label.configure(text="Error: Invalid selection.", text_color="#ff4c4c")
            return

        source_path = os.path.join(FLAGS_BASE_DIR, selected_folder, selected_file)

        try:
            shutil.copy(source_path, DEST_FILE)
            self.status_label.configure(text=f"Loaded {selected_file}...", text_color="white")
            self.update() 

            os.chdir(REPO_DIR)
            subprocess.run(["git", "add", "client_settings.json"], check=True)
            
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            
            if status.stdout.strip():
                commit_msg = f"auto: applied {selected_file} from {selected_folder}"
                subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                subprocess.run(["git", "push", "origin", "main"], check=True)
                self.status_label.configure(text="✅ Successfully pushed to GitHub!", text_color="#4cff4c")
            else:
                self.status_label.configure(text="⚠️ Preset is already active on GitHub.", text_color="#ffcc00")

        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="#ff4c4c")

if __name__ == "__main__":
    app = FastFlagManager()
    app.mainloop()
