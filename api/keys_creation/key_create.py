import uuid
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from pathlib import Path
from keys_creation import USB_LABEL, KEY_FOLDER, IDENTIFIER_FILE, PUBLIC_KEY_FILE
import tkinter as tk
from tkinter import messagebox
import psutil


def find_usb_mount() -> Path | None:
    """🔍 Détecte la clé USB avec psutil (cross-platform)."""
    try:
        for partition in psutil.disk_partitions():
            if ('removable' in partition.opts) or (partition.fstype in ['vfat', 'exfat', 'ntfs']):
                mount_path = Path(partition.mountpoint)
                if (mount_path.name == USB_LABEL) or (USB_LABEL in mount_path.name):
                    return mount_path
    except ImportError:
        print("⚠️ psutil non installé. Utilisez: pip install psutil")
    return None

def generate_keys() -> tuple[bytes, bytes]:
    """🔐 Génère une paire de clés RSA."""
    key = RSA.generate(2048)
    private_key: bytes = key.export_key(format='PEM')
    public_key: bytes = key.publickey().export_key(format='PEM')
    return private_key, public_key

def encrypt_identifier(public_key: bytes) -> bytes:
    """🔒 Chiffre un UUID avec la clé publique."""
    identifier: bytes = str(uuid.uuid4()).encode()
    cipher = PKCS1_OAEP.new(RSA.import_key(public_key))
    encrypted_id: bytes = cipher.encrypt(identifier)
    return encrypted_id

def write_to_usb(mount_point: Path, public_key: bytes, encrypted_id: bytes) -> None:
    """💾 Écrit les fichiers sur la clé USB."""
    target_dir: Path = mount_point / KEY_FOLDER
    target_dir.mkdir(exist_ok=True)

    # TODO: Stocker la clé privée en base de données sécurisée

    with open(target_dir / PUBLIC_KEY_FILE, "wb") as f:
        f.write(public_key)
    with open(target_dir / IDENTIFIER_FILE, "wb") as f:
        f.write(encrypted_id)

def main() -> None:
    root = tk.Tk()
    root.withdraw()  # Masque la fenêtre principale de tkinter

    mount_point: Path | None = find_usb_mount()
    if not mount_point:
        messagebox.showerror("Erreur", "❌ Clé USB non détectée. Assurez-vous qu'elle est montée et nommée correctement.")
        return

    _, public_key = generate_keys()
    encrypted_id = encrypt_identifier(public_key)
    write_to_usb(mount_point, public_key, encrypted_id)
    messagebox.showinfo("Succès", f"✅ Clé USB d'authentification créée sur {mount_point}")

if __name__ == "__main__":
    main()