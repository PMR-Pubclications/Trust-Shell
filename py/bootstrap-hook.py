import urllib.request
import subprocess
import os

def bootstrap_liquid_installation():
    """
    Pulls the master installation script from Trust-Main and executes 
    the local platform deployment and self-purging sequence.
    """
    installer_url = "https://raw.githubusercontent.com/PMR-Pubclications/Trust-Main/main/install_trust_shell.py"
    local_installer_path = "install_trust_shell.py"

    print("[BOOTSTRAP] Fetching master installation protocol from Trust-Main...")
    
    try:
        urllib.request.urlretrieve(installer_url, local_installer_path)
        print("[BOOTSTRAP] Secure bootstrap payload retrieved. Executing deployment...")
        
        # Execute the self-purging liquid installer locally
        subprocess.run(["python3", local_installer_path], check=True)
        
        # Clean up the bootstrap launcher script itself post-execution
        if os.path.exists(local_installer_path):
            os.remove(local_installer_path)
            
        print("[BOOTSTRAP] Installation lifecycle complete.")
        
    except Exception as e:
        print(f"[BOOTSTRAP ERROR] Failed to execute remote bootstrap sequence: {e}")

if __name__ == "__main__":
    bootstrap_liquid_installation()
