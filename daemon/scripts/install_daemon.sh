#!/bin/bash
# Script d'installation du daemon CryptUSBee pour Linux

set -e

SERVICE_NAME="cryptusbee-daemon"
SERVICE_USER="cryptusbee"
SERVICE_GROUP="cryptusbee"
INSTALL_DIR="/opt/cryptusbee"
CONFIG_DIR="/etc/cryptusbee"
LOG_DIR="/var/log/cryptusbee"
SYSTEMD_DIR="/etc/systemd/system"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification des privilèges root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo_error "Ce script doit être exécuté en tant que root"
        exit 1
    fi
}

# Détection de la distribution
detect_distro() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    else
        echo_error "Impossible de détecter la distribution Linux"
        exit 1
    fi
    
    echo_info "Distribution détectée: $DISTRO $VERSION"
}

# Installation des dépendances
install_dependencies() {
    echo_info "Installation des dépendances..."
    
    case $DISTRO in
        ubuntu|debian)
            apt-get update
            apt-get install -y python3 python3-pip python3-venv libudev-dev
            ;;
        centos|rhel|fedora)
            if command -v dnf &> /dev/null; then
                dnf install -y python3 python3-pip python3-venv libudev-devel
            else
                yum install -y python3 python3-pip python3-venv libudev-devel
            fi
            ;;
        *)
            echo_warning "Distribution non testée, installation manuelle des dépendances nécessaire"
            ;;
    esac
}

# Création de l'utilisateur système
create_user() {
    echo_info "Création de l'utilisateur système $SERVICE_USER..."
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd --system --no-create-home --shell /usr/sbin/nologin \
                --comment "CryptUSBee daemon user" \
                --user-group "$SERVICE_USER"
        echo_success "Utilisateur $SERVICE_USER créé"
    else
        echo_warning "L'utilisateur $SERVICE_USER existe déjà"
    fi
}

# Création des répertoires
create_directories() {
    echo_info "Création des répertoires..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"
    
    # Permissions
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$CONFIG_DIR"
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$LOG_DIR"
    
    chmod 755 "$INSTALL_DIR"
    chmod 750 "$CONFIG_DIR"
    chmod 750 "$LOG_DIR"
    
    echo_success "Répertoires créés"
}

# Installation du daemon
install_daemon() {
    echo_info "Installation des fichiers du daemon..."
    
    # Copie des fichiers Python
    cp -r ../cryptusbee_daemon.py "$INSTALL_DIR/"
    cp -r ../config_manager.py "$INSTALL_DIR/"
    cp -r ../usb_monitor.py "$INSTALL_DIR/"
    cp -r ../websocket_server.py "$INSTALL_DIR/"
    cp -r ../requirements-daemon.txt "$INSTALL_DIR/"
    
    # Installation de l'environnement virtuel
    python3 -m venv "$INSTALL_DIR/venv"
    "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
    "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements-daemon.txt"
    
    # Permissions
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"
    chmod +x "$INSTALL_DIR/cryptusbee_daemon.py"
    
    echo_success "Daemon installé"
}

# Création du fichier service systemd
create_systemd_service() {
    echo_info "Création du service systemd..."
    
    cat > "$SYSTEMD_DIR/$SERVICE_NAME.service" << EOF
[Unit]
Description=CryptUSBee USB Authentication Daemon
Documentation=https://github.com/remiv1/crypt_us_bee
After=network.target
Wants=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/cryptusbee_daemon.py
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=process
Restart=on-failure
RestartSec=5s
TimeoutStartSec=60s
TimeoutStopSec=30s

# Sécurité
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$LOG_DIR $CONFIG_DIR
CapabilityBoundingSet=CAP_SYS_ADMIN
AmbientCapabilities=CAP_SYS_ADMIN

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=cryptusbee-daemon

[Install]
WantedBy=multi-user.target
EOF

    # Rechargement de systemd
    systemctl daemon-reload
    
    echo_success "Service systemd créé"
}

# Configuration des permissions udev
configure_udev() {
    echo_info "Configuration des règles udev..."
    
    cat > "/etc/udev/rules.d/99-cryptusbee.rules" << EOF
# Règles udev pour CryptUSBee
# Autoriser l'accès aux périphériques USB pour l'utilisateur cryptusbee

# Périphériques USB avec label CRYPTUSB
SUBSYSTEM=="block", ENV{ID_FS_LABEL}=="CRYPTUSB", GROUP="$SERVICE_GROUP", MODE="0660"

# Tous les périphériques USB amovibles
SUBSYSTEM=="block", ATTRS{removable}=="1", GROUP="$SERVICE_GROUP", MODE="0660"

# Notification des événements à systemd
ACTION=="add|remove", SUBSYSTEM=="block", ATTRS{removable}=="1", TAG+="systemd"
EOF

    # Rechargement des règles udev
    udevadm control --reload-rules
    udevadm trigger
    
    echo_success "Règles udev configurées"
}

# Installation du daemon
install() {
    echo_info "🔧 Installation du daemon CryptUSBee..."
    
    detect_distro
    install_dependencies
    create_user
    create_directories
    install_daemon
    create_systemd_service
    configure_udev
    
    echo_success "✅ Installation terminée!"
    echo_info "Pour démarrer le service : sudo systemctl start $SERVICE_NAME"
    echo_info "Pour l'activer au démarrage : sudo systemctl enable $SERVICE_NAME"
}

# Désinstallation du daemon
uninstall() {
    echo_info "🗑️ Désinstallation du daemon CryptUSBee..."
    
    # Arrêt et désactivation du service
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        systemctl stop "$SERVICE_NAME"
    fi
    
    if systemctl is-enabled --quiet "$SERVICE_NAME"; then
        systemctl disable "$SERVICE_NAME"
    fi
    
    # Suppression des fichiers
    rm -f "$SYSTEMD_DIR/$SERVICE_NAME.service"
    rm -f "/etc/udev/rules.d/99-cryptusbee.rules"
    rm -rf "$INSTALL_DIR"
    rm -rf "$CONFIG_DIR"
    rm -rf "$LOG_DIR"
    
    # Suppression de l'utilisateur
    if id "$SERVICE_USER" &>/dev/null; then
        userdel "$SERVICE_USER"
    fi
    
    # Rechargement
    systemctl daemon-reload
    udevadm control --reload-rules
    
    echo_success "✅ Désinstallation terminée!"
}

# Affichage du statut
status() {
    echo_info "📊 Statut du daemon CryptUSBee:"
    systemctl status "$SERVICE_NAME" --no-pager
}

# Usage
usage() {
    echo "Usage: $0 {install|uninstall|status}"
    echo ""
    echo "Commands:"
    echo "  install    - Installer le daemon CryptUSBee"
    echo "  uninstall  - Désinstaller le daemon CryptUSBee"
    echo "  status     - Afficher le statut du daemon"
    exit 1
}

# Point d'entrée principal
main() {
    check_root
    
    case "${1:-}" in
        install)
            install
            ;;
        uninstall)
            uninstall
            ;;
        status)
            status
            ;;
        *)
            usage
            ;;
    esac
}

main "$@"
