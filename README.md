<div align="center">

# SynK - RGIPT FTP Agent
### The "Set it and Forget it" Course Material Sync for RGIPTians

[![Downloads](https://img.shields.io/github/downloads/Anishk362/SynK-RGIPT-FTP-Agent/total?style=for-the-badge&color=2ea44f)](https://github.com/Anishk362/SynK-RGIPT-FTP-Agent/releases/latest)

[![Version](https://img.shields.io/badge/version-1.0.0-blue?style=flat-square)](https://github.com/Anishk362/SynK-RGIPT-FTP-Agent/releases/latest)
[![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](https://github.com/Anishk362/SynK-RGIPT-FTP-Agent/blob/main/README_Windows.txt)
[![macOS](https://img.shields.io/badge/Platform-macOS-000000?style=flat-square&logo=apple&logoColor=white)](https://github.com/Anishk362/SynK-RGIPT-FTP-Agent/blob/main/README_Mac.txt)
[![Status](https://img.shields.io/badge/Status-Stable-success?style=flat-square)](https://github.com/Anishk362/SynK-RGIPT-FTP-Agent/actions)

</div>

---

## 📖 About
**SynK** is a background utility designed exclusively for students of **Rajiv Gandhi Institute of Petroleum Technology (RGIPT)**. It automatically connects to the college FTP server and mirrors course materials (slides, assignments, PDFs) to your local laptop.

Once configured, SynK runs silently in the background. You never have to manually check the FTP server again.

> [!WARNING]
> **Important Note on File Syncing:**
> SynK is designed to keep your folder identical to the Professor's folder.
> * If a professor updates/fixes a file, **SynK will overwrite your local copy** with the new version.
> * **Do not save your personal notes directly inside the synced PDF files.** Save your notes in a separate file or folder to prevent them from being overwritten.

## 🚀 Key Features

* **Zero Distraction:** Runs silently in the system tray/background. No open windows.
* **Intranet Only:** Works strictly on the local RGIPT Wi-Fi (`192.168.x.x`). **It works without a Cyberoam login** and consumes zero internet data.
* **Smart Sync:** Checks for changes every 60 minutes. It intelligently detects file updates based on size changes.
* **Cross-Platform:** Native executable support for **Windows 10/11** and **macOS** (Silicon & Intel).
* **Auto-Start:** Automatically launches when you reboot your computer.

## 📥 Download & Install

**[Click here to download the latest version (v1.0.0)](https://github.com/Anishk362/SynK-RGIPT-FTP-Agent/releases/latest)**

*Detailed installation instructions (including how to bypass Windows Defender/macOS Security) are provided on the download page.*

## 📸 How to Use

1.  **Launch App:** The setup window will appear.
2.  **Enter Credentials:** Input your FTP Username/Password.
3.  **Folder Name:** Enter the specific subject folder name exactly as it appears on the FTP server (e.g., `MA 221 @25-26`).
4.  **Verify & Add:** Click "Verify & Add Task" to ensure the connection works.
5.  **Start:** Click "Save & Start". The app will close and run silently in the background.

To add more subjects later, simply run the application again.

---

## 🛠 Tech Stack
* **Language:** Python 3.12
* **GUI:** Tkinter (Native UI)
* **Core:** `ftplib`, `multiprocessing`
* **Automation:** GitHub Actions (CI/CD)

---
<div align="center">

**Developed by Anish Kalra**
*Roll No: 24MC3006 | Dept. of Mathematical Sciences*

</div>
