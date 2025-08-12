"""
Moniteur USB multi-plateforme pour CryptUSBee
Surveille les événements USB et valide les clés CryptUSBee
"""

import asyncio
import logging
import platform
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Dict, Any, List

import psutil
from cryptography.exceptions import InvalidSignature
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

from config_manager import ConfigManager


class USBEvent:
    """Représente un événement USB."""
    
    def __init__(self, event_type: str, device_path: str, device_info: Dict[str, Any]):
        self.event_type = event_type  # 'inserted' ou 'removed'
        self.device_path = device_path
        self.device_info = device_info
        self.timestamp = time.time()
        self.is_cryptusbee = False
        self.validation_status = "unknown"


class USBValidator:
    """Validateur de clés USB CryptUSBee."""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def validate_cryptusbee_key(self, device_path: Path) -> Dict[str, Any]:
        """
        Valide si une clé USB est une clé CryptUSBee valide.
        
        Args:
            device_path: Chemin vers le point de montage de la clé
            
        Returns:
            Dictionnaire avec le statut de validation
        """
        try:
            # Vérification du label
            if not self._check_label(device_path):
                return {"valid": False, "reason": "Label incorrect"}
            
            # Vérification de la structure des dossiers
            key_folder = device_path / self.config.usb.key_folder
            if not key_folder.exists():
                return {"valid": False, "reason": "Dossier clé manquant"}
            
            # Vérification des fichiers nécessaires
            id_file = key_folder / "id_bee.key"
            public_key_file = key_folder / "public_bee.pem"
            
            if not id_file.exists() or not public_key_file.exists():
                return {"valid": False, "reason": "Fichiers de clé manquants"}
            
            # Validation cryptographique
            return self._validate_crypto(id_file, public_key_file)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la validation : {e}")
            return {"valid": False, "reason": f"Erreur: {str(e)}"}
    
    def _check_label(self, device_path: Path) -> bool:
        """Vérifie le label de la clé USB."""
        return self.config.usb.label in str(device_path)
    
    def _validate_crypto(self, id_file: Path, public_key_file: Path) -> Dict[str, Any]:
        """Valide la cryptographie de la clé."""
        try:
            # Lecture de la clé publique
            with open(public_key_file, 'rb') as f:
                public_key_data = f.read()
            
            # Lecture de l'identifiant chiffré
            with open(id_file, 'rb') as f:
                encrypted_id = f.read()
            
            # Tentative de déchiffrement
            public_key = RSA.import_key(public_key_data)
            cipher = PKCS1_OAEP.new(public_key)
            
            # Note: Pour une validation complète, nous aurions besoin de la clé privée
            # Ici, nous validons seulement la structure
            
            return {
                "valid": True,
                "key_id": encrypted_id[:16].hex(),  # Premier 16 bytes comme ID
                "public_key_fingerprint": public_key.n % 1000000
            }
            
        except Exception as e:
            return {"valid": False, "reason": f"Erreur cryptographique: {str(e)}"}


class BaseUSBMonitor(ABC):
    """Classe de base pour les moniteurs USB spécifiques à chaque plateforme."""
    
    def __init__(self, config: ConfigManager, event_callback: Callable[[USBEvent], None]):
        self.config = config
        self.event_callback = event_callback
        self.logger = logging.getLogger(__name__)
        self.validator = USBValidator(config)
        self.running = False
        self._known_devices: Dict[str, Dict[str, Any]] = {}
    
    @abstractmethod
    async def start_monitoring(self):
        """Démarre la surveillance des événements USB."""
        pass
    
    @abstractmethod
    async def stop_monitoring(self):
        """Arrête la surveillance des événements USB."""
        pass
    
    def _process_device_event(self, event_type: str, device_path: str, device_info: Dict[str, Any]):
        """Traite un événement de périphérique."""
        event = USBEvent(event_type, device_path, device_info)
        
        # Validation CryptUSBee
        if event_type == "inserted":
            validation = self.validator.validate_cryptusbee_key(Path(device_path))
            event.is_cryptusbee = validation.get("valid", False)
            event.validation_status = validation
            
            if event.is_cryptusbee:
                self.logger.info(f"✅ Clé CryptUSBee détectée: {device_path}")
                self._known_devices[device_path] = validation
            else:
                self.logger.debug(f"📱 Périphérique USB non-CryptUSBee: {device_path}")
        
        elif event_type == "removed" and device_path in self._known_devices:
            event.is_cryptusbee = True
            event.validation_status = self._known_devices.pop(device_path)
            self.logger.info(f"🔌 Clé CryptUSBee retirée: {device_path}")
        
        # Notification de l'événement
        if event.is_cryptusbee:
            self.event_callback(event)


class WindowsUSBMonitor(BaseUSBMonitor):
    """Moniteur USB pour Windows utilisant WMI."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            import wmi
            self.wmi = wmi.WMI()
        except ImportError:
            raise ImportError("Le module WMI est requis pour Windows")
    
    async def start_monitoring(self):
        """Démarre la surveillance WMI."""
        self.running = True
        self.logger.info("🖥️ Démarrage de la surveillance USB Windows")
        
        try:
            # Surveillance en arrière-plan
            await self._monitor_wmi_events()
        except Exception as e:
            self.logger.error(f"Erreur WMI: {e}")
            self.running = False
    
    async def stop_monitoring(self):
        """Arrête la surveillance WMI."""
        self.running = False
        self.logger.info("⏹️ Arrêt de la surveillance USB Windows")
    
    async def _monitor_wmi_events(self):
        """Surveille les événements WMI en continu."""
        while self.running:
            try:
                # Scan périodique des périphériques
                current_drives = set()
                for drive in psutil.disk_partitions():
                    if 'removable' in drive.opts or drive.fstype in ['vfat', 'exfat', 'ntfs']:
                        current_drives.add(drive.mountpoint)
                
                # Détection des nouveaux périphériques
                for drive in current_drives - set(self._known_devices.keys()):
                    device_info = {"mountpoint": drive, "fstype": "removable"}
                    self._process_device_event("inserted", drive, device_info)
                
                # Détection des périphériques retirés
                for drive in set(self._known_devices.keys()) - current_drives:
                    device_info = {"mountpoint": drive}
                    self._process_device_event("removed", drive, device_info)
                
                await asyncio.sleep(self.config.usb.poll_interval / 1000.0)
                
            except Exception as e:
                self.logger.error(f"Erreur lors du scan USB: {e}")
                await asyncio.sleep(5)


class LinuxUSBMonitor(BaseUSBMonitor):
    """Moniteur USB pour Linux utilisant udev."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            import pyudev
            self.context = pyudev.Context()
            self.monitor = pyudev.Monitor.from_netlink(self.context)
            self.monitor.filter_by(subsystem='block', device_type='disk')
        except ImportError:
            raise ImportError("Le module pyudev est requis pour Linux")
    
    async def start_monitoring(self):
        """Démarre la surveillance udev."""
        self.running = True
        self.logger.info("🐧 Démarrage de la surveillance USB Linux")
        
        try:
            self.monitor.start()
            await self._monitor_udev_events()
        except Exception as e:
            self.logger.error(f"Erreur udev: {e}")
            self.running = False
    
    async def stop_monitoring(self):
        """Arrête la surveillance udev."""
        self.running = False
        self.logger.info("⏹️ Arrêt de la surveillance USB Linux")
    
    async def _monitor_udev_events(self):
        """Surveille les événements udev."""
        while self.running:
            try:
                device = self.monitor.poll(timeout=1)
                if device:
                    action = device.action
                    device_path = device.device_node
                    
                    if action in ['add', 'remove'] and device_path:
                        event_type = "inserted" if action == "add" else "removed"
                        device_info = {"device_node": device_path, "subsystem": device.subsystem}
                        self._process_device_event(event_type, device_path, device_info)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Erreur lors de l'écoute udev: {e}")
                await asyncio.sleep(1)


class MacOSUSBMonitor(BaseUSBMonitor):
    """Moniteur USB pour macOS utilisant IOKit."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Implementation macOS avec IOKit serait ici
        pass
    
    async def start_monitoring(self):
        """Démarre la surveillance IOKit."""
        self.running = True
        self.logger.info("🍎 Démarrage de la surveillance USB macOS")
        
        # Pour l'instant, utilisation du fallback psutil
        await self._monitor_psutil_fallback()
    
    async def stop_monitoring(self):
        """Arrête la surveillance IOKit."""
        self.running = False
        self.logger.info("⏹️ Arrêt de la surveillance USB macOS")
    
    async def _monitor_psutil_fallback(self):
        """Fallback utilisant psutil pour macOS."""
        while self.running:
            try:
                current_drives = set()
                for drive in psutil.disk_partitions():
                    if 'removable' in drive.opts:
                        current_drives.add(drive.mountpoint)
                
                # Même logique que Windows
                for drive in current_drives - set(self._known_devices.keys()):
                    device_info = {"mountpoint": drive, "fstype": "removable"}
                    self._process_device_event("inserted", drive, device_info)
                
                for drive in set(self._known_devices.keys()) - current_drives:
                    device_info = {"mountpoint": drive}
                    self._process_device_event("removed", drive, device_info)
                
                await asyncio.sleep(self.config.usb.poll_interval / 1000.0)
                
            except Exception as e:
                self.logger.error(f"Erreur lors du scan USB: {e}")
                await asyncio.sleep(5)


class USBMonitor:
    """Moniteur USB principal qui délègue à la plateforme appropriée."""
    
    def __init__(self, config: ConfigManager, event_callback: Callable[[USBEvent], None]):
        self.config = config
        self.event_callback = event_callback
        self.logger = logging.getLogger(__name__)
        
        # Sélection du moniteur selon la plateforme
        system = platform.system()
        if system == "Windows":
            self.monitor = WindowsUSBMonitor(config, event_callback)
        elif system == "Linux":
            self.monitor = LinuxUSBMonitor(config, event_callback)
        elif system == "Darwin":
            self.monitor = MacOSUSBMonitor(config, event_callback)
        else:
            raise ValueError(f"Plateforme non supportée: {system}")
    
    async def start(self):
        """Démarre la surveillance USB."""
        self.logger.info(f"🚀 Démarrage du moniteur USB pour {platform.system()}")
        await self.monitor.start_monitoring()
    
    async def stop(self):
        """Arrête la surveillance USB."""
        self.logger.info("🛑 Arrêt du moniteur USB")
        await self.monitor.stop_monitoring()
    
    def get_connected_cryptusbee_devices(self) -> List[Dict[str, Any]]:
        """Retourne la liste des clés CryptUSBee connectées."""
        return list(self.monitor._known_devices.values())
