# 🚀 Guide Complet - Daemon CryptUSBee et Signature de Code

## 📋 Résumé Exécutif

Ce guide couvre la création complète d'un daemon multi-plateforme pour CryptUSBee, ainsi que le processus de signature numérique pour la distribution sécurisée des exécutables et MSI.

## 🏗️ Architecture du Daemon

### Vue d'ensemble

Le daemon CryptUSBee est un service système qui :

- Surveille les événements USB en temps réel
- Valide l'authenticité des clés CryptUSBee
- Communique avec les navigateurs via WebSocket sécurisé
- Déclenche la déconnexion automatique lors du retrait de clé

### Composants Principaux

```ini
📁 daemon/
├── 📄 cryptusbee_daemon.py      # Service principal
├── 📄 config_manager.py         # Gestionnaire de configuration
├── 📄 usb_monitor.py           # Surveillance USB multi-OS
├── 📄 websocket_server.py      # Serveur WebSocket
├── 📄 requirements-daemon.txt   # Dépendances Python
├── 📁 scripts/                 # Scripts d'installation
│   ├── 📄 install_service.ps1  # Installation Windows
│   └── 📄 install_daemon.sh    # Installation Linux
├── 📁 packaging/               # Fichiers de build
│   ├── 📄 build.ps1            # Script de build principal
│   ├── 📄 cryptusbee_daemon.spec # Configuration PyInstaller
│   └── 📄 version_info.txt     # Métadonnées Windows
├── 📁 tests/                   # Tests unitaires
└── 📄 SIGNING_GUIDE.md         # Guide de signature de code
```

## 🔧 Démarrage Rapide

### 1. Installation des Dépendances

```powershell
# Navigation vers le répertoire daemon
cd daemon

# Installation des dépendances Python
pip install -r requirements-daemon.txt

# Installation des outils de build
pip install pyinstaller cx-Freeze
```

### 2. Configuration

Le daemon utilise un fichier de configuration JSON auto-généré :

```json
{
    "websocket": {
        "host": "localhost",
        "port": 8765,
        "ssl_enabled": true
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

### 3. Développement et Tests

```powershell
# Exécution en mode développement
python cryptusbee_daemon.py

# Tests unitaires
python -m pytest tests/ -v

# Tests spécifiques
python -m pytest tests/test_daemon.py::TestConfigManager -v
```

## 📦 Build et Packaging

### Build Windows

```powershell
# Build simple
cd packaging
.\build.ps1 -BuildWindows

# Build avec signature
.\build.ps1 -All -Sign -CertificatePath "cert.pfx" -CertificatePassword "password"

# Build MSI uniquement
.\build.ps1 -BuildMSI
```

### Résultats du Build

Après un build réussi, vous obtiendrez :

```ini
📁 dist/
├── 📁 CryptUSBeeDaemon/
│   ├── 📄 cryptusbee_daemon.exe    # Exécutable principal
│   ├── 📄 install_service.ps1      # Script d'installation
│   └── 📄 README.md                # Documentation
└── 📄 CryptUSBeeDaemon.msi         # Package d'installation
```

## 🔐 Signature de Code

### 1. Obtention d'un Certificat

**Option Recommandée** : Certificat commercial EV

- **DigiCert** : Certificat EV Code Signing (~400€/an)
- **GlobalSign** : Code Signing Certificate (~300€/an)
- **Sectigo** : Code Signing Certificate (~250€/an)

### 2. Configuration de la Signature

Créer un fichier `sign_config.json` :

```json
{
    "certificate": {
        "pfx_path": "C:\\path\\to\\certificate.pfx",
        "pfx_password": "votre_mot_de_passe"
    },
    "timestamp": {
        "url": "http://timestamp.digicert.com",
        "algorithm": "sha256"
    },
    "files_to_sign": [
        "cryptusbee_daemon.exe",
        "CryptUSBeeDaemon.msi"
    ]
}
```

### 3. Signature Automatique

```powershell
# Signature intégrée au build
.\build.ps1 -All -Sign -CertificatePath "cert.pfx" -CertificatePassword "password"

# Vérification de la signature
signtool.exe verify /pa /v "dist\CryptUSBeeDaemon\cryptusbee_daemon.exe"
```

## 🚀 Déploiement

### Installation Windows

```powershell
# Installation comme service Windows
.\install_service.ps1 -Install

# Démarrage du service
.\install_service.ps1 -Start

# Vérification du statut
Get-Service -Name "CryptUSBeeDaemon"
```

### Installation Linux

```bash
# Installation du daemon
sudo ./install_daemon.sh install

# Activation et démarrage
sudo systemctl enable cryptusbee-daemon
sudo systemctl start cryptusbee-daemon

# Vérification du statut
systemctl status cryptusbee-daemon
```

## 🔍 Surveillance et Logs

### Logs Windows

```powershell
# Journaux d'événements Windows
Get-WinEvent -LogName "Application" | Where-Object {$_.ProviderName -eq "CryptUSBeeDaemon"}

# Fichier de log direct
Get-Content "C:\Users\[User]\cryptusbee_daemon.log" -Tail 50
```

### Logs Linux

```bash
# Journaux systemd
journalctl -u cryptusbee-daemon -f

# Fichier de log direct
tail -f /var/log/cryptusbee/cryptusbee_daemon.log
```

## 🛠️ Développement Avancé

### Ajout de Fonctionnalités

1. **Extension de la surveillance USB** :
   - Modifier `usb_monitor.py`
   - Ajouter de nouveaux types d'événements
   - Implémenter la validation spécifique

2. **Amélioration du WebSocket** :
   - Étendre `websocket_server.py`
   - Ajouter de nouveaux types de messages
   - Implémenter l'authentification avancée

3. **Configuration dynamique** :
   - Étendre `config_manager.py`
   - Ajouter des validateurs de configuration
   - Implémenter le rechargement à chaud

### Tests et Qualité

```powershell
# Tests avec couverture
python -m pytest tests/ --cov=. --cov-report=html

# Analyse statique
flake8 . --max-line-length=100

# Vérification de sécurité
bandit -r . -x tests/
```

## 🚨 Dépannage

### Problèmes Courants

1. **Service ne démarre pas**

    ```powershell
    # Vérification des logs
    Get-EventLog -LogName Application -Source "CryptUSBeeDaemon" -Newest 10

    # Test en mode console
    .\cryptusbee_daemon.exe --console
    ```

2. **Clés USB non détectées**

    ```powershell
    # Vérification des permissions
    icacls "E:\" /grant "CryptUSBeeDaemon:(OI)(CI)F"

    # Test de détection manuelle
    python -c "import psutil; print([p for p in psutil.disk_partitions() if 'removable' in p.opts])"
    ```

3. **Problèmes de WebSocket**

```powershell
# Test de connectivité
Test-NetConnection -ComputerName localhost -Port 8765

# Vérification du pare-feu
Get-NetFirewallRule -DisplayName "CryptUSBee*"
```

## 📚 Ressources et Documentation

### Documentation Technique

- [WebSocket RFC 6455](https://tools.ietf.org/html/rfc6455)
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
- [Windows Services](https://docs.microsoft.com/en-us/windows/win32/services/services)
- [systemd Services](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

### Outils de Développement

- **PyInstaller** : Création d'exécutables Python
- **WiX Toolset** : Création de MSI Windows
- **SignTool** : Signature de code Windows
- **systemd** : Gestion des services Linux

### Communauté et Support

- **Issues GitHub** : [Repository CryptUSBee](https://github.com/remiv1/crypt_us_bee)
- **Documentation** : Wiki du projet
- **Discussions** : GitHub Discussions

## 🎯 Prochaines Étapes

1. **Phase 1** : Implémentation du daemon de base ✅
2. **Phase 2** : Tests et validation sur différents OS
3. **Phase 3** : Intégration avec l'interface web existante
4. **Phase 4** : Optimisations et fonctionnalités avancées
5. **Phase 5** : Distribution et déploiement automatisés

## 📝 Notes Importantes

- **Sécurité** : Toujours utiliser des certificats valides en production
- **Performance** : Surveiller la consommation de ressources
- **Compatibilité** : Tester sur différentes versions d'OS
- **Maintenance** : Prévoir les mises à jour automatiques

Ce guide vous donne tous les éléments nécessaires pour créer, signer et déployer le daemon CryptUSBee de manière professionnelle et sécurisée.
