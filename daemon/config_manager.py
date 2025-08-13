"""
Gestionnaire de configuration pour le daemon CryptUSBee
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from cryptography.fernet import Fernet

DAEMON_PORT = 8552

@dataclass
class WebSocketConfig:
    """Configuration du serveur WebSocket."""
    host: str = "localhost"
    port: int = DAEMON_PORT
    ssl_enabled: bool = True
    cert_file: str = "daemon.crt"
    key_file: str = "daemon.key"


@dataclass
class USBConfig:
    """Configuration de surveillance USB."""
    label: str = "CRYPTUSB"
    key_folder: str = ".cryptusbee"
    poll_interval: int = 1000
    allowed_devices: List[Any] | None = None

    def __post_init__(self):
        if self.allowed_devices is None:
            self.allowed_devices = []


@dataclass
class SecurityConfig:
    """Configuration de sécurité."""
    jwt_secret: str = ""
    token_expiry: int = 3600
    encryption_key: str = ""

    def __post_init__(self):
        if not self.jwt_secret:
            self.jwt_secret = Fernet.generate_key().decode()
        if not self.encryption_key:
            self.encryption_key = Fernet.generate_key().decode()


@dataclass
class LoggingConfig:
    """Configuration des logs."""
    level: str = "INFO"
    file: str = "cryptusbee_daemon.log"
    max_size: int = 10485760  # 10MB
    backup_count: int = 5


class ConfigManager:
    """Gestionnaire de configuration du daemon CryptUSBee."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialise le gestionnaire de configuration.
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config_path = config_path or self._get_default_config_path()
        self._load_config()
    
    def _get_default_config_path(self) -> Path:
        """Retourne le chemin par défaut du fichier de configuration."""
        if os.name == 'nt':  # Windows
            config_dir = Path.home() / "AppData" / "Local" / "CryptUSBee"
        else:  # Linux/macOS
            config_dir = Path.home() / ".config" / "cryptusbee"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"
    
    def _load_config(self):
        """Charge la configuration depuis le fichier."""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data: Dict[str, Any] = json.load(f)
        else:
            config_data = {}
            self._create_default_config()
        
        # Initialisation des sections de configuration
        self.websocket = WebSocketConfig(**config_data.get('websocket', {}))
        self.usb = USBConfig(**config_data.get('usb', {}))
        self.security = SecurityConfig(**config_data.get('security', {}))
        self.logging = LoggingConfig(**config_data.get('logging', {}))
    
    def _create_default_config(self):
        """Crée un fichier de configuration par défaut."""
        default_config: Dict[str, Any] = {
            "websocket": {
                "host": "localhost",
                "port": 8765,
                "ssl_enabled": True,
                "cert_file": "daemon.crt",
                "key_file": "daemon.key"
            },
            "usb": {
                "label": "CRYPTUSB",
                "key_folder": ".cryptusbee",
                "poll_interval": 1000,
                "allowed_devices": []
            },
            "security": {
                "jwt_secret": Fernet.generate_key().decode(),
                "token_expiry": 3600,
                "encryption_key": Fernet.generate_key().decode()
            },
            "logging": {
                "level": "INFO",
                "file": str(Path.home() / "cryptusbee_daemon.log"),
                "max_size": 10485760,
                "backup_count": 5
            }
        }
        
        self.save_config(default_config)
    
    def save_config(self, config_data: Optional[Dict[str, Any]] | None = None) -> None:
        """
        Sauvegarde la configuration dans le fichier.
        
        Args:
            config_data: Données de configuration à sauvegarder
        """
        if config_data is None:
            config_data = self.to_dict()
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire."""
        return {
            "websocket": {
                "host": self.websocket.host,
                "port": self.websocket.port,
                "ssl_enabled": self.websocket.ssl_enabled,
                "cert_file": self.websocket.cert_file,
                "key_file": self.websocket.key_file
            },
            "usb": {
                "label": self.usb.label,
                "key_folder": self.usb.key_folder,
                "poll_interval": self.usb.poll_interval,
                "allowed_devices": self.usb.allowed_devices
            },
            "security": {
                "jwt_secret": self.security.jwt_secret,
                "token_expiry": self.security.token_expiry,
                "encryption_key": self.security.encryption_key
            },
            "logging": {
                "level": self.logging.level,
                "file": self.logging.file,
                "max_size": self.logging.max_size,
                "backup_count": self.logging.backup_count
            }
        }
    
    def update_config(self, section: str, key: str, value: Any):
        """
        Met à jour une valeur de configuration.
        
        Args:
            section: Section de configuration
            key: Clé à mettre à jour
            value: Nouvelle valeur
        """
        config_section = getattr(self, section, None)
        if config_section and hasattr(config_section, key):
            setattr(config_section, key, value)
            self.save_config()
        else:
            raise ValueError(f"Section '{section}' ou clé '{key}' invalide")
    
    def get_ssl_context(self) -> Optional[Tuple[str, str]]:
        """
        Retourne le contexte SSL pour le WebSocket.
        
        Returns:
            Tuple (cert_file, key_file) ou None si SSL désactivé
        """
        if self.websocket.ssl_enabled:
            cert_path = Path(self.websocket.cert_file)
            key_path = Path(self.websocket.key_file)
            
            if cert_path.exists() and key_path.exists():
                return (str(cert_path), str(key_path))
        
        return None
