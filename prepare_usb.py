import os
import platform
import subprocess
from pathlib import Path
from keys_creation import KEY_FOLDER, USB_LABEL
from keys_creation.key_create import generate_keys, encrypt_identifier, write_to_usb
import tkinter as tk
from tkinter import messagebox, filedialog

def clear_drive(drive_path: Path):
    """Supprime tous les fichiers et dossiers d'un chemin donné."""
    for item in drive_path.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            subprocess.run(["rmdir", "/S", "/Q", str(item)], shell=True)

def format_usb(drive_path: Path) -> bool:
    """Formate la clé USB avec triple validation utilisateur."""
    print("⚠️ ATTENTION : Vous êtes sur le point de formater la clé USB !")
    for i in range(3):
        confirmation = input(f"Confirmez-vous le formatage ? (oui/non) [{i+1}/3] : ").strip().lower()
        if confirmation != "oui":
            print("❌ Formatage annulé.")
            return False

    print("⏳ Formatage en cours...")
    if platform.system() == "Windows":
        subprocess.run(["format", drive_path, "/FS:exFAT", "/Q", "/Y"], shell=True)
        subprocess.run(["label", str(drive_path), USB_LABEL], shell=True)
    else:
        subprocess.run(["mkfs.exfat", drive_path], check=True)

    # Suppression des fichiers restants sur la clé USB
    drive_path = Path(drive_path)  # Assurez-vous que drive_path est un objet Path
    clear_drive(drive_path)

    print("✅ Formatage terminé.")
    return True

def format_usb_gui():
    """Formate la clé USB via une interface graphique."""
    root = tk.Tk()
    root.withdraw()  # Masque la fenêtre principale

    messagebox.showwarning("Attention", "⚠️ Vous êtes sur le point de formater une clé USB !")

    # Sélection du chemin de la clé USB
    drive_path_str = filedialog.askdirectory(title="Sélectionnez la clé USB à formater")
    if not drive_path_str:
        messagebox.showerror("Erreur", "❌ Aucun chemin sélectionné.")
        return None

    confirm = messagebox.askyesno("Confirmation", "Confirmez-vous le formatage de la clé USB ?")
    if not confirm:
        messagebox.showinfo("Annulé", "❌ Formatage annulé.")
        return None

    # Formatage (commande système)
    try:
        drive_path = Path(drive_path_str)  # Conversion explicite en Path
        clear_drive(drive_path)

        if platform.system() == "Windows":
            drive_letter = drive_path.drive  # Récupère la lettre du lecteur, par exemple "E:"
            print(f"Lettre du lecteur : {drive_letter}")
            if not drive_path.is_dir() or not drive_path.drive:
                messagebox.showerror("Erreur", "❌ Veuillez sélectionner la racine de la clé USB (par exemple, E:\\).")
                return None
            subprocess.run(["format", drive_letter, "/FS:exFAT", "/Q", "/Y"], shell=True)
            subprocess.run(["label", drive_letter, f"{USB_LABEL}"], shell=True)
        else:
            subprocess.run(["mkfs.exfat", str(drive_path)], check=True)

        messagebox.showinfo("Succès", "✅ Formatage terminé.")
        return drive_path
    except Exception as e:
        messagebox.showerror("Erreur", f"❌ Une erreur s'est produite lors du formatage : {e}")
        return None

def prepare_usb():
    """Prépare la clé USB en créant les dossiers et fichiers nécessaires."""
    drive_path_text: str = input("Entrez le chemin de la clé USB (ex: E:\\ ou /media/CRYPTUSB) : ").strip()
    drive_path = Path(drive_path_text)
    mount_point = Path(drive_path)

    if not mount_point.exists():
        print("❌ Le chemin spécifié n'existe pas.")
        return

    if not format_usb(drive_path):
        return

    # Création des clés et des fichiers
    _, public_key = generate_keys()
    encrypted_id = encrypt_identifier(public_key)

    # Création du dossier et des fichiers cachés
    target_dir = mount_point / KEY_FOLDER
    target_dir.mkdir(exist_ok=True)
    os.system(f"attrib +h {target_dir}")  # Rendre le dossier caché (Windows uniquement)

    write_to_usb(mount_point, public_key, encrypted_id)
    # TODO: Prévoir une fonction pour stocker la clé privée de manière sécurisée
    # TODO: Option SQLite
    # TODO: Option Base de données sécurisée
    print(f"✅ Clé USB préparée avec succès dans {mount_point}.")

def prepare_usb_gui():
    """Prépare la clé USB via une interface graphique."""
    drive_path = format_usb_gui()
    if not drive_path:
        return

    mount_point = Path(drive_path)

    # Création des clés et des fichiers
    _, public_key = generate_keys()
    encrypted_id = encrypt_identifier(public_key)

    # Création du dossier et des fichiers cachés
    target_dir = mount_point / KEY_FOLDER
    target_dir.mkdir(exist_ok=True)
    os.system(f"attrib +h {target_dir}")  # Rendre le dossier caché (Windows uniquement)

    write_to_usb(mount_point, public_key, encrypted_id)
    messagebox.showinfo("Succès", f"✅ Clé USB préparée avec succès dans {mount_point}.")

if __name__ == "__main__":
    # Choisissez entre l'interface en ligne de commande ou l'interface graphique
    interface = input("Choisissez l'interface (1: CLI, 2: GUI) : ").strip()
    if interface == "1":
        prepare_usb()
    elif interface == "2":
        prepare_usb_gui()
    else:
        print("❌ Option invalide.")
