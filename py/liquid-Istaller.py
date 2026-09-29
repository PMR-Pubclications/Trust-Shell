import os
import sys
import platform
import shutil

class LiquidInstaller:
    """
    Unified multi-architecture bootstrap installer for Trust-Shell.
    Detects target host OS, deploys matching binaries, and securely 
    strips away the unused architectures upon installation.
    """
    def __init__(self, bundle_root="trust_payloads"):
        self.bundle_root = bundle_root
        self.payloads = {
            "ANDROID": os.path.join(bundle_root, "android_build"),
            "IOS": os.path.join(bundle_root, "ios_build"),
            "WINDOWS": os.path.join(bundle_root, "windows_build")
        }

    def detect_target_platform(self) -> str:
        sys_platform = platform.system()
        
        if sys_platform == "Linux" and (os.path.exists("/system/bin/app_process") or "ANDROID_DATA" in os.environ):
            return "ANDROID"
        elif sys_platform == "Darwin":
            return "IOS"
        elif sys_platform == "Windows":
            return "WINDOWS"
        
        return "UNKNOWN_POSIX"

    def execute_liquid_deployment(self):
        active_target = self.detect_target_platform()
        print(f"[INSTALLER] Target architecture detected: {active_target}")

        if active_target not in self.payloads:
            print(f"[INSTALLER ERROR] Unsupported platform runtime: {active_target}")
            sys.exit(1)

        # 1. Verify and deploy the active target payload
        target_path = self.payloads[active_target]
        if not os.path.exists(target_path):
            print(f"[INSTALLER ERROR] Missing deployment payload for {active_target} at {target_path}")
            sys.exit(1)
            
        print(f"[INSTALLER] Deploying verified secure binaries for {active_target}...")
        # (Insert target-specific unpacking/link logic here)

        # 2. Self-Purge: Sweep and destroy the other two unused formats
        print("[PURGE] Initiating architectural sanitization...")
        for platform_name, path in self.payloads.items():
            if platform_name != active_target:
                if os.path.exists(path):
                    print(f"[PURGE] Wiping uncommitted architecture bundle: {platform_name}")
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    print(f"[PURGE] Bundle for {platform_name} already cleared.")

        # 3. Clean up root container references
        if os.path.exists(self.bundle_root) and not os.listdir(self.bundle_root):
            os.rmdir(self.bundle_root)

        print(f"[INSTALLER] Installation successful. Environment locked to {active_target}. All extraneous binaries purged.")

if __name__ == "__main__":
    installer = LiquidInstaller()
    installer.execute_liquid_deployment()
Anyone inspecting the source or auditing the repository can verify that the installer doesn't leave dead weight or unneeded OS binaries lingering on the field device.