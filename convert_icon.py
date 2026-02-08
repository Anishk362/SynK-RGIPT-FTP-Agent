from PIL import Image
import os
import sys

# 1. Install Pillow if missing
try:
    import PIL
except ImportError:
    print("Installing Pillow...")
    os.system(f"{sys.executable} -m pip install pillow")
    from PIL import Image

# 2. Convert
try:
    img = Image.open("logo.jpeg")
    img.save("app_icon.ico", format='ICO', sizes=[(256, 256)])
    print("\n[SUCCESS] 'app_icon.ico' created successfully!")
except FileNotFoundError:
    print("\n[ERROR] Could not find 'logo.jpeg'. Did you rename it correctly?")
except Exception as e:
    print(f"\n[ERROR] {e}")