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
# When frozen, sys.executable is the EXE/App path.
# When raw, __file__ is the script path.
if getattr(sys, 'frozen', False):
    EXE_PATH = sys.executable
    if platform.system() == "Darwin":
        # On Mac, sys.executable points inside the .app bundle (Contents/MacOS/SynK)
        # We want the folder containing the .app
        APP_DIR = os.path.abspath(os.path.join(os.path.dirname(EXE_PATH), "../../.."))
    else:
        # On Windows, it's the folder containing the .exe
        APP_DIR = os.path.dirname(sys.executable)
else:
    EXE_PATH = os.path.abspath(__file__)
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure config is saved where the user actually put the app, not in a temp folder
os.chdir(APP_DIR)

CONFIG_FILE = os.path.join(APP_DIR, "SynK_config.json")
POLL_INTERVAL = 3600  # 1 Hour
DEFAULT_HOST = "192.168.3.9" 

# -------------------------------------------------------------------------
# SYNC ENGINE
# -------------------------------------------------------------------------

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
        try:
            ftp = ftplib.FTP(task['host'], timeout=30)
            ftp.login(task['user'], task['pass'])
            if task['remote_dir']: ftp.cwd(task['remote_dir'])
            sync_recursive(ftp, task['local_dir'])
            ftp.quit()
        except: pass

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
                with open(CONFIG_FILE, 'r') as f:
                    self.tasks = json.load(f)
            except: pass

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
        self.listbox = tk.Listbox(root, height=6, width=60)
        self.listbox.pack(padx=20)

        # Populate list
        for t in self.tasks:
            display_text = f"{t['user']} -> .../{os.path.basename(t['local_dir'])}"
            self.listbox.insert(tk.END, display_text)

        tk.Button(root, text="SAVE & START SynK", command=self.save_and_start, bg="#007bff", fg="white", font=("Segoe UI", 11, "bold"), height=2).pack(pady=20, fill="x", padx=20)

        self.current_local_path = ""

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.current_local_path = folder
            self.lbl_local_path.config(text=folder)

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
        self.listbox.insert(tk.END, f"{user} -> .../{os.path.basename(local)}")
        
        self.entry_remote.delete(0, tk.END)
        self.lbl_local_path.config(text="No folder selected")
        self.current_local_path = ""
        messagebox.showinfo("Success", "Task Verified & Added!")

    def save_and_start(self):
        if not self.tasks:
            messagebox.showerror("Error", "No tasks to save!")
            return
        
        try:
            with open(CONFIG_FILE, 'w') as f:
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
            with open(vbs, "w") as f:
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
            with open(plist, "w") as f: f.write(content)
    except: pass

# -------------------------------------------------------------------------
# MAIN ENTRY POINT
# -------------------------------------------------------------------------
if __name__ == "__main__":
    multiprocessing.freeze_support() 
    
    # Check for silent flag
    if "--silent" in sys.argv:
        # BACKGROUND MODE
        try: os.chdir(APP_DIR)
        except: pass
        
        while True:
            if os.path.exists(CONFIG_FILE):
                try:
                    with open(CONFIG_FILE, 'r') as f: tasks = json.load(f)
                    run_sync_cycle(tasks)
                except: pass
            time.sleep(POLL_INTERVAL)
    else:
        # GUI MODE
        root = tk.Tk()
        # Set icon if it exists
        try:
            if platform.system() == "Windows":
                root.iconbitmap(os.path.join(APP_DIR, "app_icon.ico"))
            # Linux/Mac often use .png for tk window icons
            # else: 
            #    img = tk.PhotoImage(file=os.path.join(APP_DIR, "app_icon.png"))
            #    root.iconphoto(False, img)
        except: pass
        
        app = SetupApp(root)
        root.mainloop()