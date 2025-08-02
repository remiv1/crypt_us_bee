import uuid
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from pathlib import Path
from keys_creation import USB_LABEL, KEY_FOLDER, IDENTIFIER_FILE, PUBLIC_KEY_FILE, PRIVATE_KEY_FILE
import tkinter as tk
from tkinter import messagebox


def find_usb_mount_linux() -> Path | None:
    """🔍 Détecte le point de montage de la clé USB (Linux uniquement pour l'instant)."""
    media_path = Path("/media")
    for user_dir in media_path.iterdir():
        for device in user_dir.iterdir():
            if USB_LABEL in device.name:
                return device
    return None

def find_usb_mount_windows() -> Path | None:
    """🔍 Détecte le point de montage de la clé USB (Windows)."""
    import win32api
    drives = win32api.GetLogicalDriveStrings().split('\\\\')
    for drive in drives:
        if drive and USB_LABEL in drive:
            return Path(drive)
    return None 


def find_usb_mount() -> Path | None:
    """🔍 Combine les fonctions de détection pour Linux et Windows."""
    return find_usb_mount_linux() or find_usb_mount_windows()

def generate_keys() -> tuple[bytes, bytes]:
    """🔐 Génère une paire de clés RSA."""
    key = RSA.generate(2048)
    private_key: bytes = key.export_key()
    public_key: bytes = key.publickey().export_key()
    return private_key, public_key

def encrypt_identifier(public_key: bytes) -> bytes:
    """🔒 Chiffre un UUID avec la clé publique."""
    identifier: bytes = str(uuid.uuid4()).encode()
    cipher = PKCS1_OAEP.new(RSA.import_key(public_key))
    encrypted_id: bytes = cipher.encrypt(identifier)
    return encrypted_id

def write_to_usb(mount_point: Path, private_key: bytes, public_key: bytes, encrypted_id: bytes) -> None:
    """💾 Écrit les fichiers sur la clé USB."""
    target_dir: Path = mount_point / KEY_FOLDER
    target_dir.mkdir(exist_ok=True)

    with open(target_dir / PRIVATE_KEY_FILE, "wb") as f:
        f.write(private_key)
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

    private_key, public_key = generate_keys()
    encrypted_id = encrypt_identifier(public_key)
    write_to_usb(mount_point, private_key, public_key, encrypted_id)
    messagebox.showinfo("Succès", f"✅ Clé USB d'authentification créée sur {mount_point}")

if __name__ == "__main__":
    main()