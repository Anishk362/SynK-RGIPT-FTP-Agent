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

if getattr(sys, 'frozen', False):
    EXE_PATH = sys.executable
    if platform.system() == "Darwin":
        APP_BUNDLE_PATH = os.path.abspath(os.path.join(os.path.dirname(EXE_PATH), "../../.."))
        APP_NAME = "SynK"
        CONFIG_DIR = os.path.join(os.path.expanduser("~"), "Library", "Application Support", APP_NAME)
        if not os.path.exists(CONFIG_DIR):
            try: os.makedirs(CONFIG_DIR)
            except: pass
        CONFIG_FILE = os.path.join(CONFIG_DIR, "SynK_config.json")
        APP_DIR = APP_BUNDLE_PATH 
    else:
        APP_DIR = os.path.dirname(sys.executable)
        try: os.chdir(APP_DIR)
        except: pass
        CONFIG_FILE = os.path.join(APP_DIR, "SynK_config.json")
else:
    EXE_PATH = os.path.abspath(__file__)
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    try: os.chdir(APP_DIR)
    except: pass
    CONFIG_FILE = os.path.join(APP_DIR, "SynK_config.json")

POLL_INTERVAL = 3600 
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
        
        # --- MAC FIX: Enforce White Background for High Contrast ---
        # This fixes the dark-grey-on-black text issue in Dark Mode
        self.bg_color = "white"
        self.root.configure(bg=self.bg_color)
        
        self.tasks = [] 

        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.tasks = json.load(f)
            except: pass

        # Apply bg_color to ALL Labels to prevent grey boxes
        tk.Label(root, text='Add New "SynK" Task', font=("Segoe UI", 12, "bold"), bg=self.bg_color, fg="black").pack(pady=10)

        tk.Label(root, text="FTP Host IP:", bg=self.bg_color, fg="black").pack(anchor="w", padx=20)
        self.entry_host = tk.Entry(root, width=50, bg="#f0f0f0", fg="black", insertbackground="black")
        self.entry_host.insert(0, DEFAULT_HOST)
        self.entry_host.pack(padx=20)

        tk.Label(root, text="Username:", bg=self.bg_color, fg="black").pack(anchor="w", padx=20)
        self.entry_user = tk.Entry(root, width=50, bg="#f0f0f0", fg="black", insertbackground="black")
        self.entry_user.pack(padx=20)

        tk.Label(root, text="Password:", bg=self.bg_color, fg="black").pack(anchor="w", padx=20)
        self.entry_pass = tk.Entry(root, width=50, show="*", bg="#f0f0f0", fg="black", insertbackground="black")
        self.entry_pass.pack(padx=20)

        tk.Label(root, text="Remote Folder Name (Exact Spelling):", bg=self.bg_color, fg="black").pack(anchor="w", padx=20)
        tk.Label(root, text="(e.g. 'MA 221 @25-26')", font=("Segoe UI", 8, "italic"), fg="gray", bg=self.bg_color).pack(anchor="w", padx=20)
        self.entry_remote = tk.Entry(root, width=50, bg="#f0f0f0", fg="black", insertbackground="black")
        self.entry_remote.pack(padx=20)

        tk.Label(root, text="Save to Local Folder:", bg=self.bg_color, fg="black").pack(anchor="w", padx=20, pady=(10,0))
        self.lbl_local_path = tk.Label(root, text="No folder selected", fg="blue", bg=self.bg_color)
        self.lbl_local_path.pack(padx=20)
        
        tk.Button(root, text="Choose Folder", command=self.browse_folder).pack(pady=5)
        
        tk.Button(root, text="+ VERIFY & ADD TASK", command=self.add_task, bg="#e1e1e1", fg="black", font=("Segoe UI", 9, "bold")).pack(pady=15)

        tk.Label(root, text="Configured Tasks:", font=("Segoe UI", 10, "bold"), bg=self.bg_color, fg="black").pack(pady=5)
        
        # SAVE BUTTON DOCKED BOTTOM
        tk.Button(root, text="SAVE & START SynK", command=self.save_and_start, bg="#007bff", fg="white", font=("Segoe UI", 11, "bold"), height=2).pack(side=tk.BOTTOM, fill="x", padx=20, pady=20)

        # SCROLLABLE FRAME
        self.list_container = tk.Frame(root, relief="sunken", bd=1, bg="white")
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
        self.current_local_path = ""

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.current_local_path = folder
            self.lbl_local_path.config(text=folder)

    def refresh_task_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for i, task in enumerate(self.tasks):
            row = tk.Frame(self.scrollable_frame, bg="white", pady=2)
            row.pack(fill="x", expand=True, pady=1)

            display_text = f"{task['user']} -> .../{os.path.basename(task['local_dir'])}"
            # Force Black Text on White Background for tasks
            tk.Label(row, text=display_text, bg="white", fg="black", anchor="w", font=("Segoe UI", 9)).pack(side="left", padx=5, fill="x", expand=True)

            btn = tk.Button(row, text="✖", bg="#dc3545", fg="white", font=("Segoe UI", 8, "bold"), width=3,
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
            self.root.config(cursor="wait"); self.root.update()
            ftp = ftplib.FTP(host, timeout=5)
            ftp.login(user, pwd)
            if remote: ftp.cwd(remote)
            ftp.quit()
        except Exception as e:
            messagebox.showerror("Verification Failed", f"Error: {e}"); return
        finally: self.root.config(cursor="")

        self.tasks.append({"host": host, "user": user, "pass": pwd, "remote_dir": remote, "local_dir": local})
        self.refresh_task_list()
        self.entry_remote.delete(0, tk.END)
        self.lbl_local_path.config(text="No folder selected")
        self.current_local_path = ""
        messagebox.showinfo("Success", "Task Verified & Added!")

    def save_and_start(self):
        try:
            with open(CONFIG_FILE, 'w') as f: json.dump(self.tasks, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}"); return
        
        add_to_startup() 
        if platform.system() == "Windows":
            try:
                startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
                vbs_path = os.path.join(startup_folder, "SynK_Agent.vbs")
                if os.path.exists(vbs_path): subprocess.Popen(['wscript.exe', vbs_path], shell=False, close_fds=True)
            except: pass
        elif platform.system() == "Darwin":
             try:
                plist = os.path.expanduser("~/Library/LaunchAgents/com.synk.agent.plist")
                os.system(f"launchctl unload {plist} 2>/dev/null")
                os.system(f"launchctl load {plist}")
             except: pass
        messagebox.showinfo("Success", "SynK is now running in the background."); self.root.destroy(); sys.exit(0)

def add_to_startup():
    if not getattr(sys, 'frozen', False): return
    try:
        if platform.system() == "Windows":
            startup = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
            vbs = os.path.join(startup, "SynK_Agent.vbs")
            with open(vbs, "w", encoding="utf-8") as f:
                f.write('Set WshShell = CreateObject("WScript.Shell")\n')
                f.write(f'WshShell.Run chr(34) & "{EXE_PATH}" & chr(34) & " --silent", 0\n')
                f.write('Set WshShell = Nothing')
        elif platform.system() == "Darwin":
            plist = os.path.expanduser("~/Library/LaunchAgents/com.synk.agent.plist")
            if not os.path.exists(os.path.dirname(plist)): os.makedirs(os.path.dirname(plist))
            content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict><key>Label</key><string>com.synk.agent</string><key>ProgramArguments</key><array><string>{EXE_PATH}</string><string>--silent</string></array><key>RunAtLoad</key><true/><key>StandardOutPath</key><string>/dev/null</string><key>StandardErrorPath</key><string>/dev/null</string></dict></plist>"""
            with open(plist, "w", encoding="utf-8") as f: f.write(content)
    except: pass

if __name__ == "__main__":
    multiprocessing.freeze_support() 
    if platform.system() == "Windows":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('rgipt.synk.ftpagent.1.0')
        except: pass

    if "--silent" in sys.argv:
        try: 
            if platform.system() == "Windows": os.chdir(APP_DIR)
        except: pass
        while True:
            if os.path.exists(CONFIG_FILE):
                try:
                    with open(CONFIG_FILE, 'r') as f: tasks = json.load(f)
                    run_sync_cycle(tasks)
                except: pass
            time.sleep(POLL_INTERVAL)
    else:
        root = tk.Tk()
        # WINDOWS TASKBAR FIX: 'default=icon_path' assigns the icon to the whole process
        try:
            if platform.system() == "Windows":
                icon_path = os.path.join(APP_DIR, "app_icon.ico")
                if os.path.exists(icon_path): root.iconbitmap(default=icon_path)
        except: pass
        app = SetupApp(root)
        root.mainloop()