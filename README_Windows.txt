================================================================================
                                   SynK
                        Intelligent FTP Sync Agent
================================================================================

Developer:    Anish Kalra (Roll No: 24MC3006)
Department:   Mathematical Sciences, RGIPT
Release:      v1.0.0
Repository:   https://github.com/AnishKalra/SynK-RGIPT-FTP-Agent

--------------------------------------------------------------------------------
1. CRITICAL: PREVENTING AUTOMATIC DELETION
--------------------------------------------------------------------------------
Windows Defender aggressively deletes software not made by Microsoft. To run SynK,
you must create a "Safe Zone" folder.

FOLLOW THESE STEPS EXACTLY BEFORE UNZIPPING THE EXE:

1. Create a folder on your Desktop (or C: Drive) named "SynK".
2. Press the Windows Key -> Type "Virus & threat protection" -> Press Enter.
3. Under "Virus & threat protection settings", click the blue link [Manage settings].
4. Scroll down to the "Exclusions" section.
5. Click [Add or remove exclusions].
6. Click the [+ Add an exclusion] button -> Select [Folder].
7. Select the "SynK" folder you created in Step 1.
8. Click [Yes] on the admin prompt.

NOW, extract 'SynK.exe' into this specific folder.

--------------------------------------------------------------------------------
2. FIRST LAUNCH & SMARTSCREEN
--------------------------------------------------------------------------------
1. Go to your "SynK" folder and double-click 'SynK.exe'.
2. You will likely see a bright blue window saying "Windows protected your PC".
   - DO NOT close it.
   - Look for the small text that says "More info". Click it.
   - A new button will appear at the bottom labeled [Run anyway]. Click it.

(This warning only appears once).

--------------------------------------------------------------------------------
3. CONFIGURATION GUIDE
--------------------------------------------------------------------------------
The Setup Manager window will appear.

1. FTP Host IP: Default is 192.168.3.9.
2. Credentials: Enter your FTP User and Pass.
3. Remote Folder Name: Enter the EXACT name of the folder on the server.
   - Example: MA 221 @25-26
   - Note: Copy the spelling exactly.
4. Save to Local Folder: Click [Choose Folder] to pick where files go.
5. Click [+ VERIFY & ADD TASK].
   - SynK will test the connection. If it works, it adds it to the list.
6. Click [SAVE & START SynK].

The window will vanish. This is normal! SynK is now running in the background.

--------------------------------------------------------------------------------
4. TROUBLESHOOTING
--------------------------------------------------------------------------------
Q: I clicked "Save & Start" and nothing happened.
A: That means it worked. SynK is designed to be invisible. It will start checking
   for files immediately and then every 60 minutes.

Q: I moved 'SynK.exe' to a new folder and it stopped working.
A: SynK remembers its location for auto-startup. If you move the .exe, you must
   double-click it again in the new location to repair the link.

Q: How do I stop it/Uninstall?
A: 1. Open Task Manager (Ctrl+Shift+Esc).
   2. Details Tab -> Right-click 'SynK.exe' -> End Task.
   3. Press Win+R -> Type 'shell:startup' -> Delete 'SynK_Agent.vbs'.
   4. Delete the SynK folder.

--------------------------------------------------------------------------------
SUPPORT
--------------------------------------------------------------------------------
For updates or help, visit:
https://github.com/AnishKalra/SynK-RGIPT-FTP-Agent