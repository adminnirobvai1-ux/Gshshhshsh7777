"""
Auto Package Installer Module
বট রান করার শুরুতে প্রয়োজনীয় সকল ডিপেন্ডেন্সি নিজে নিজেই ইনস্টল করে নেবে
"""
import sys
import subprocess
import importlib

REQUIRED_PACKAGES = [
    ("pyTelegramBotAPI", "telebot"),
    ("selenium", "selenium"),
    ("webdriver-manager", "webdriver_manager"),
    ("requests", "requests")
]

def auto_install_packages():
    """চেক করে প্রয়োজনীয় প্যাকেজ না থাকলে স্বয়ংক্রিয়ভাবে ইনস্টল করে"""
    print("[*] Checking system dependencies...")
    all_ok = True
    for package_name, import_name in REQUIRED_PACKAGES:
        try:
            importlib.import_module(import_name)
        except ImportError:
            print(f"[*] Dependency missing: {package_name}. Installing automatically...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "--upgrade", package_name
                ])
                print(f"[+] Successfully installed: {package_name}")
            except Exception as e:
                print(f"[-] Failed to install {package_name}: {e}")
                all_ok = False
    return all_ok

if __name__ == "__main__":
    auto_install_packages()
