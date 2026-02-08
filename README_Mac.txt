================================================================================
                                SynK (macOS)
                        Intelligent FTP Sync Agent
================================================================================

Developer:    Anish Kalra (Roll No: 24MC3006)
Department:   Mathematical Sciences, RGIPT
Release:      v1.0.0
Repository:   https://github.com/AnishKalra/SynK-RGIPT-FTP-Agent

--------------------------------------------------------------------------------
1. STOP! READ THIS BEFORE LAUNCHING
--------------------------------------------------------------------------------
Because I am a student developer and not a registered Apple Corporation, macOS 
"Gatekeeper" will block this app by default to protect you.

YOU MUST PERFORM THIS ONE-TIME SETUP OR THE APP WILL NOT OPEN.

STEP 1: MOVE THE APP
1. Open this folder in Finder.
2. Click and drag the 'SynK' icon into your 'Applications' folder in the sidebar.
3. Go to your 'Applications' folder.

STEP 2: THE "RIGHT-CLICK" TRICK (Crucial Step)
1. Locate 'SynK' in your Applications folder.
2. DO NOT double-click it yet.
3. Instead, RIGHT-CLICK (or Hold Control + Click) on the SynK icon.
4. Select 'Open' from the menu that appears.
5. A popup will ask: "macOS cannot verify the developer... Are you sure?"
6. Click the 'Open' button.

(You only need to do this once. Next time, you can just click it normally.)

--------------------------------------------------------------------------------
2. CONFIGURATION GUIDE
--------------------------------------------------------------------------------
Once the app opens, you will see the Setup Manager.

1. FTP Host IP: Leave this as '192.168.3.9' (RGIPT Default).
2. Username/Password: Type your college FTP credentials.
3. Remote Folder Name: Type the EXACT folder name from the server.
   - Example: MA 221 @25-26 
   - Warning: This is Case Sensitive! 'ma 221' will fail. Use 'MA 221'.
4. Save to Local Folder: Click 'Choose Folder' and select a folder on your Mac.
   - Recommendation: Create a folder named "College Material" on your Desktop.

5. Verification:
   - Click the [+ VERIFY & ADD TASK] button.
   - Watch for a "Success" popup.

6. Activation:
   - Click the green [SAVE & START SynK] button.

--------------------------------------------------------------------------------
3. PERMISSIONS (Don't miss this!)
--------------------------------------------------------------------------------
Immediately after clicking "Save & Start", macOS will ask for permission:
"SynK would like to access files in your Desktop..."

-> You MUST click [OK]. 
-> If you click "Don't Allow", SynK cannot save your PDFs.

The window will then close. SynK is now running silently in the background.

--------------------------------------------------------------------------------
4. HOW IT WORKS
--------------------------------------------------------------------------------
* SynK wakes up every 60 minutes.
* It checks if you are connected to RGIPT WiFi.
* It checks for new files on the FTP.
* It downloads them silently.
* It works entirely offline (Intranet), saving your internet data.

--------------------------------------------------------------------------------
5. FAQ
--------------------------------------------------------------------------------
Q: How do I add another subject later?
A: Go to Applications -> Double-click 'SynK'. The setup menu will reappear.

Q: How do I uninstall it completely?
A: 1. Open Terminal (Command+Space -> Type "Terminal").
   2. Copy/Paste this command: 
      launchctl unload ~/Library/LaunchAgents/com.synk.agent.plist
   3. Drag SynK from Applications to the Trash.

--------------------------------------------------------------------------------
SUPPORT
--------------------------------------------------------------------------------
Found a bug? Report it here:
https://github.com/AnishKalra/SynK-RGIPT-FTP-Agent