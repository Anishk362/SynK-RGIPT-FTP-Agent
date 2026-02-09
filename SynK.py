import ftplib
import os
import time
import json
import sys
import platform
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import multiprocessing

# -------------------------------------------------------------------------
# CONSTANTS & CONFIGURATION
# -------------------------------------------------------------------------

# DETERMINING THE "REAL" LOCATION
if getattr(sys, 'frozen', False):
    EXE_PATH = sys.executable
    if platform.system() == "Darwin":
        # On Mac, sys.executable points inside the .app bundle (Contents/MacOS/SynK)
        # We want the folder containing the .app
        APP_BUNDLE_PATH = os.path.abspath(os.path.join(os.path.dirname(EXE_PATH), "../../.."))
        
        # MAC FIX: Use 'Application Support' for config because 'Applications' is Read-Only
        APP_NAME = "SynK"
        CONFIG_DIR = os.path.join(os.path.expanduser("~"), "Library", "Application Support", APP_NAME)
        if not os.path.exists(CONFIG_DIR):
            try: os.makedirs(CONFIG_DIR)
            except: pass
        CONFIG_FILE = os.path.join(CONFIG_DIR, "SynK_config.json")
        LOG_FILE = os.path.join(CONFIG_DIR, "SynK.log")
        
        # For Mac, we don't change directory to the App Bundle as we can't write there anyway
        APP_DIR = APP_BUNDLE_PATH 
    else:
        # On Windows, it's the folder containing the .exe
        APP_DIR = os.path.dirname(sys.executable)
        # Windows: We write next to the EXE (Since it's in a user folder like Desktop/SynK)
        try: os.chdir(APP_DIR)
        except: pass
        CONFIG_FILE = os.path.join(APP_DIR, "SynK_config.json")
        LOG_FILE = os.path.join(APP_DIR, "SynK.log")
else:
    EXE_PATH = os.path.abspath(__file__)
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    try: os.chdir(APP_DIR)
    except: pass
    CONFIG_FILE = os.path.join(APP_DIR, "SynK_config.json")
    LOG_FILE = os.path.join(APP_DIR, "SynK.log")

POLL_INTERVAL = 3600  # 1 Hour
DEFAULT_HOST = "192.168.3.9" 

# -------------------------------------------------------------------------
# SYNC ENGINE
# -------------------------------------------------------------------------

def log_error(message):
    """Writes error messages to a local log file with timestamp."""
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        # SENIOR DEV FIX: Added encoding='utf-8' to prevent crashes on non-ASCII systems
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except: pass

def is_directory(ftp, item):
    original = ftp.pwd()
    try:
        ftp.cwd(item)
        ftp.cwd(original)
        return True
    except: 
        return False

def sync_recursive(ftp, local_path):
    if not os.path.exists(local_path):
        try: os.makedirs(local_path)
        except: return 

    try: items = ftp.nlst()
    except: return

    for item in items:
        if item in ['.', '..']: continue
        local_item_path = os.path.join(local_path, item)

        if is_directory(ftp, item):
            ftp.cwd(item)
            sync_recursive(ftp, local_item_path)
            ftp.cwd('..')
        else:
            download = False
            if not os.path.exists(local_item_path): 
                download = True
            else:
                try:
                    # Compare sizes to check for updates
                    if ftp.size(item) != os.path.getsize(local_item_path): 
                        download = True
                except: pass

            if download:
                try:
                    with open(local_item_path, 'wb') as f:
                        ftp.retrbinary(f"RETR {item}", f.write)
                except: pass

def run_sync_cycle(sync_list):
    for task in sync_list:
        ftp = None
        try:
            ftp = ftplib.FTP(task['host'], timeout=30)
            ftp.login(task['user'], task['pass'])
            
            # EDGE CASE HANDLER: If Prof renames/deletes folder, this throws error
            # We catch it specifically so the app continues to sync other subjects
            if task['remote_dir']: 
                try:
                    ftp.cwd(task['remote_dir'])
                except Exception as e:
                    log_error(f"SYNC FAIL: Remote folder '{task['remote_dir']}' not found. Professor may have renamed it.")
                    ftp.quit()
                    continue

            sync_recursive(ftp, task['local_dir'])
            ftp.quit()
        except Exception as main_e: 
            log_error(f"CONNECTION FAIL: Could not connect to {task.get('host', 'unknown')}. {main_e}")
            pass

# -------------------------------------------------------------------------
# GUI SECTION
# -------------------------------------------------------------------------

class SetupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SynK Manager - RGIPT") 
        self.root.geometry("500x650")
        self.tasks = [] 

        if os.path.exists(CONFIG_FILE):
            try:
                # SENIOR DEV FIX: Added encoding='utf-8' for robust JSON reading
                with open(CONFIG_FILE, 'r', encoding="utf-8") as f:
                    self.tasks = json.load(f)
            except: 
                self.tasks = [] # Safe fallback if JSON is corrupt

        tk.Label(root, text='Add New "SynK" Task', font=("Segoe UI", 12, "bold")).pack(pady=10)

        tk.Label(root, text="FTP Host IP:").pack(anchor="w", padx=20)
        self.entry_host = tk.Entry(root, width=50)
        self.entry_host.insert(0, DEFAULT_HOST)
        self.entry_host.pack(padx=20)

        tk.Label(root, text="Username:").pack(anchor="w", padx=20)
        self.entry_user = tk.Entry(root, width=50)
        self.entry_user.pack(padx=20)

        tk.Label(root, text="Password:").pack(anchor="w", padx=20)
        self.entry_pass = tk.Entry(root, width=50, show="*")
        self.entry_pass.pack(padx=20)

        tk.Label(root, text="Remote Folder Name (Exact Spelling):").pack(anchor="w", padx=20)
        tk.Label(root, text="(e.g. 'MA 221 @25-26')", font=("Segoe UI", 8, "italic"), fg="gray").pack(anchor="w", padx=20)
        self.entry_remote = tk.Entry(root, width=50)
        self.entry_remote.pack(padx=20)

        tk.Label(root, text="Save to Local Folder:").pack(anchor="w", padx=20, pady=(10,0))
        self.lbl_local_path = tk.Label(root, text="No folder selected", fg="blue")
        self.lbl_local_path.pack(padx=20)
        
        tk.Button(root, text="Choose Folder", command=self.browse_folder).pack(pady=5)
        
        tk.Button(root, text="+ VERIFY & ADD TASK", command=self.add_task, bg="#e1e1e1", font=("Segoe UI", 9, "bold")).pack(pady=15)

        tk.Label(root, text="Configured Tasks:", font=("Segoe UI", 10, "bold")).pack(pady=5)
        
        # --- SCROLLABLE FRAME (Replaces Listbox to support Buttons) ---
        self.list_container = tk.Frame(root, relief="sunken", bd=1)
        self.list_container.pack(padx=20, pady=5, fill="both", expand=True)

        self.canvas = tk.Canvas(self.list_container, bg="white", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.list_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_frame_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_frame_window, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.refresh_task_list()
        # -------------------------------------------------------

        tk.Button(root, text="SAVE & START SynK", command=self.save_and_start, bg="#007bff", fg="white", font=("Segoe UI", 11, "bold"), height=2).pack(pady=20, fill="x", padx=20)

        self.current_local_path = ""

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.current_local_path = folder
            self.lbl_local_path.config(text=folder)

    # --- UI UPDATE: Function to Draw Rows with Delete Buttons ---
    def refresh_task_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for i, task in enumerate(self.tasks):
            row = tk.Frame(self.scrollable_frame, bg="white", pady=2)
            row.pack(fill="x", expand=True, pady=1)

            display_text = f"{task['user']} -> .../{os.path.basename(task['local_dir'])}"
            tk.Label(row, text=display_text, bg="white", anchor="w", font=("Segoe UI", 9)).pack(side="left", padx=5, fill="x", expand=True)

            # Red Trash Button
            btn = tk.Button(row, text="✖", bg="#dc3545", fg="white", font=("Segoe UI", 8, "bold"), width=3,
                            activebackground="#bd2130", activeforeground="white",
                            command=lambda idx=i: self.delete_task(idx))
            btn.pack(side="right", padx=5)
            
            tk.Frame(self.scrollable_frame, height=1, bg="#e0e0e0").pack(fill="x")

    def delete_task(self, index):
        self.tasks.pop(index)
        self.refresh_task_list()

    def add_task(self):
        host = self.entry_host.get().strip()
        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get().strip()
        remote = self.entry_remote.get().strip()
        local = self.current_local_path

        if not (host and user and pwd and local):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        try:
            self.root.config(cursor="wait")
            self.root.update()
            ftp = ftplib.FTP(host, timeout=5)
            ftp.login(user, pwd)
            if remote: ftp.cwd(remote)
            ftp.quit()
        except Exception as e:
            self.root.config(cursor="")
            messagebox.showerror("Verification Failed", f"Could not verify task.\nError: {e}")
            return
        finally:
            self.root.config(cursor="")

        task = {"host": host, "user": user, "pass": pwd, "remote_dir": remote, "local_dir": local}
        self.tasks.append(task)
        self.refresh_task_list()
        
        self.entry_remote.delete(0, tk.END)
        self.lbl_local_path.config(text="No folder selected")
        self.current_local_path = ""
        messagebox.showinfo("Success", "Task Verified & Added!")

    def save_and_start(self):
        try:
            # SENIOR DEV FIX: encoding='utf-8'
            with open(CONFIG_FILE, 'w', encoding="utf-8") as f:
                json.dump(self.tasks, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")
            return
        
        # 1. Setup Startup
        add_to_startup() 
        
        # 2. LAUNCH BACKGROUND AGENT
        if platform.system() == "Windows":
            try:
                startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
                vbs_path = os.path.join(startup_folder, "SynK_Agent.vbs")
                if os.path.exists(vbs_path):
                    # Execute the VBS which handles the silent launch
                    subprocess.Popen(['wscript.exe', vbs_path], shell=False, close_fds=True)
            except: pass

        elif platform.system() == "Darwin":
             try:
                plist = os.path.expanduser("~/Library/LaunchAgents/com.synk.agent.plist")
                os.system(f"launchctl unload {plist} 2>/dev/null")
                os.system(f"launchctl load {plist}")
             except: pass

        messagebox.showinfo("Success", "SynK is now running in the background.\nYou can close this window.")
        self.root.destroy()
        sys.exit(0)

# -------------------------------------------------------------------------
# STARTUP LOGIC
# -------------------------------------------------------------------------
def add_to_startup():
    if not getattr(sys, 'frozen', False): return
    try:
        if platform.system() == "Windows":
            startup = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
            vbs = os.path.join(startup, "SynK_Agent.vbs")
            with open(vbs, "w", encoding="utf-8") as f:
                f.write('Set WshShell = CreateObject("WScript.Shell")\n')
                # IMPORTANT: We use --silent flag
                f.write(f'WshShell.Run chr(34) & "{EXE_PATH}" & chr(34) & " --silent", 0\n')
                f.write('Set WshShell = Nothing')

        elif platform.system() == "Darwin":
            plist = os.path.expanduser("~/Library/LaunchAgents/com.synk.agent.plist")
            if not os.path.exists(os.path.dirname(plist)): os.makedirs(os.path.dirname(plist))
            
            # MacOS Plist definition
            content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.synk.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>{EXE_PATH}</string>
        <string>--silent</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/dev/null</string>
    <key>StandardErrorPath</key>
    <string>/dev/null</string>
</dict>
</plist>"""
            with open(plist, "w", encoding="utf-8") as f: f.write(content)
    except: pass

# -------------------------------------------------------------------------
# MAIN ENTRY POINT
# -------------------------------------------------------------------------
if __name__ == "__main__":
    multiprocessing.freeze_support() 
    
    # WINDOWS ICON FIX: Explicitly set AppUserModelID
    if platform.system() == "Windows":
        try:
            import ctypes
            myappid = 'rgipt.synk.ftpagent.1.0' # Arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except: pass

    # Check for silent flag
    if "--silent" in sys.argv:
        # BACKGROUND MODE
        try: 
            if platform.system() == "Windows": os.chdir(APP_DIR)
        except: pass
        
        while True:
            if os.path.exists(CONFIG_FILE):
                try:
                    # SENIOR DEV FIX: encoding='utf-8'
                    with open(CONFIG_FILE, 'r', encoding="utf-8") as f: tasks = json.load(f)
                    run_sync_cycle(tasks)
                except: pass
            time.sleep(POLL_INTERVAL)
    else:
        # GUI MODE
        root = tk.Tk()
        # Set icon if it exists
        try:
            if platform.system() == "Windows":
                # Ensure we look in the APP_DIR for the icon
                icon_path = os.path.join(APP_DIR, "app_icon.ico")
                if os.path.exists(icon_path):
                    # FIX: Use 'default=' to enforce Taskbar Icon
                    root.iconbitmap(default=icon_path)
        except: pass
        
        app = SetupApp(root)
        root.mainloop()