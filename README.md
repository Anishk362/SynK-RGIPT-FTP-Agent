![Latest Release Downloads](https://img.shields.io/github/downloads/Anishk362/SynK-RGIPT-FTP-Agent/latest/total?style=for-the-badge&color=blue)
# SynK - RGIPT FTP Sync Agent

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/Anishk362/SynK-RGIPT-FTP-Agent/releases/latest)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-lightgrey) 
![Status](https://img.shields.io/badge/status-Stable-success)

**SynK** is a "Set it and Forget it" background utility designed for students of **Rajiv Gandhi Institute of Petroleum Technology (RGIPT)**. It automatically mirrors course materials from the college FTP server to your local machine, ensuring you never miss a professor's upload.

---

## 🚀 Features

* **Zero Distraction:** Configured once, it runs silently in the background. No open windows, no taskbar clutter.
* **Intranet Only:** Works strictly on the local RGIPT WiFi. It **does not** require active internet data (works even without Cyberoam login).
* **Smart Sync:** Checks for changes every 60 minutes. It intelligently detects if a file has been updated and replaces it.
* **Cross-Platform:** Native support for **Windows 10/11** and **macOS** (Silicon & Intel).
* **Auto-Start:** Automatically launches when you turn on your computer.

## 📥 Download

**[Click here to visit the Releases Page](https://github.com/Anishk362/SynK-RGIPT-FTP-Agent/releases)**

Please read the specific installation instructions for your OS on the download page, as this app is unsigned.

## 🛠 Tech Stack

* **Language:** Python 3.12
* **GUI:** Tkinter (Native UI)
* **Core:** ftplib, multiprocessing
* **Automation:** GitHub Actions (CI/CD)

## 📸 Usage

1. **Launch App:** Open SynK.
2. **Enter Details:** Input your FTP credentials and the specific subject folder name (e.g., `MA 221 @25-26`).
3. **Verify:** Click "Verify & Add Task".
4. **Run:** Click "Save & Start". The app will close and run in the background.

To add more subjects later, simply run the application again.

---
**Developer:** Anish Kalra | *Roll No: 24MC3006* | *Dept. of Mathematical Sciences*
