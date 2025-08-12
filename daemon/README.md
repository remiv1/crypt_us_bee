# CryptUSBee Daemon

## Vue d'ensemble

Le daemon CryptUSBee est un service système multi-plateforme qui :

- Surveille les événements USB (insertion/retrait de clés)
- Maintient un WebSocket local pour communiquer avec le navigateur
- Valide l'authenticité des clés USB CryptUSBee
- Déclenche la déconnexion automatique lors du retrait de la clé

## Architecture

```ini
┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Navigateur    │ ←─────────────→ │   Daemon Local  │
│   (Frontend)    │   ws://localhost │  (Service OS)   │
└─────────────────┘                 └─────────────────┘
                                            │
                                            │ USB Events
                                            ▼
                                    ┌─────────────────┐
                                    │  Système USB    │
                                    │   (Hardware)    │
                                    └─────────────────┘
```

## Composants

### 1. Service Principal (`cryptusbee_daemon.py`)

- Point d'entrée principal du daemon
- Gestion du cycle de vie du service
- Orchestration des composants

### 2. Surveillant USB (`usb_monitor.py`)

- Détection des événements USB
- Validation des clés CryptUSBee
- Implémentation spécifique par OS

### 3. Serveur WebSocket (`websocket_server.py`)

- Communication avec le navigateur
- Authentification JWT
- Diffusion des événements USB

### 4. Gestionnaire de Configuration (`config_manager.py`)

- Chargement des paramètres
- Gestion des certificats
- Configuration par environnement

## Installation

### Windows

```powershell
# Installation comme service Windows
.\install_service.ps1
```

### Linux

```bash
# Installation comme daemon systemd
sudo ./install_daemon.sh
```

### macOS

```bash
# Installation comme LaunchDaemon
sudo ./install_daemon_macos.sh
```

## Configuration

Le daemon utilise un fichier de configuration `config.json` :

```json
{
    "websocket": {
        "host": "localhost",
        "port": 8765,
        "ssl_enabled": true,
        "cert_file": "daemon.crt",
        "key_file": "daemon.key"
    },
    "usb": {
        "label": "CRYPTUSB",
        "key_folder": ".cryptusbee",
        "poll_interval": 1000
    },
    "security": {
        "jwt_secret": "auto-generated",
        "token_expiry": 3600
    },
    "logging": {
        "level": "INFO",
        "file": "cryptusbee_daemon.log"
    }
}
```

## Sécurité

- Communication WebSocket chiffrée (WSS)
- Authentification JWT avec rotation automatique
- Validation cryptographique des clés USB
- Journalisation horodatée des événements

## Développement

Pour contribuer au daemon :

1. Clonez le repository
2. Installez les dépendances : `pip install -r requirements-daemon.txt`
3. Exécutez les tests : `python -m pytest tests/`
4. Suivez les conventions de codage du projet

## Logs et Surveillance

Le daemon génère des logs structurés :

- Événements USB (insertion/retrait)
- Connexions WebSocket
- Erreurs de validation
- Statistiques de performance
