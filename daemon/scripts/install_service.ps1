# Script d'installation du service Windows pour CryptUSBee
param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Start,
    [switch]$Stop,
    [string]$ServiceName = "CryptUSBeeDaemon"
)

# Vérification des privilèges administrateur
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "Ce script doit être exécuté en tant qu'administrateur."
    exit 1
}

$ServiceDisplayName = "CryptUSBee Daemon"
$ServiceDescription = "Service de surveillance USB pour l'authentification CryptUSBee"
$ServicePath = Join-Path $PSScriptRoot "..\cryptusbee_daemon.exe"
$ServiceStartMode = "Automatic"

function Install-CryptUSBeeService {
    Write-Host "🔧 Installation du service CryptUSBee..." -ForegroundColor Green
    
    try {
        # Vérification que l'exécutable existe
        if (-not (Test-Path $ServicePath)) {
            Write-Error "L'exécutable du service n'a pas été trouvé : $ServicePath"
            return $false
        }
        
        # Arrêt du service s'il existe déjà
        $existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($existingService) {
            Write-Host "⏹️ Arrêt du service existant..." -ForegroundColor Yellow
            Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
            
            Write-Host "🗑️ Suppression du service existant..." -ForegroundColor Yellow
            sc.exe delete $ServiceName
            Start-Sleep -Seconds 2
        }
        
        # Création du service
        Write-Host "📦 Création du nouveau service..." -ForegroundColor Green
        New-Service -Name $ServiceName `
                   -DisplayName $ServiceDisplayName `
                   -Description $ServiceDescription `
                   -BinaryPathName $ServicePath `
                   -StartupType $ServiceStartMode `
                   -Credential (Get-Credential -Message "Entrez les identifiants pour exécuter le service")
        
        # Configuration des paramètres de récupération
        Write-Host "⚙️ Configuration des paramètres de récupération..." -ForegroundColor Green
        sc.exe failure $ServiceName reset=86400 actions=restart/5000/restart/10000/restart/20000
        
        Write-Host "✅ Service CryptUSBee installé avec succès!" -ForegroundColor Green
        return $true
        
    } catch {
        Write-Error "❌ Erreur lors de l'installation du service : $($_.Exception.Message)"
        return $false
    }
}

function Uninstall-CryptUSBeeService {
    Write-Host "🗑️ Désinstallation du service CryptUSBee..." -ForegroundColor Yellow
    
    try {
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($service) {
            # Arrêt du service
            if ($service.Status -eq "Running") {
                Write-Host "⏹️ Arrêt du service..." -ForegroundColor Yellow
                Stop-Service -Name $ServiceName -Force
            }
            
            # Suppression du service
            Write-Host "🗑️ Suppression du service..." -ForegroundColor Yellow
            sc.exe delete $ServiceName
            
            Write-Host "✅ Service CryptUSBee désinstallé avec succès!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠️ Le service CryptUSBee n'est pas installé." -ForegroundColor Yellow
            return $true
        }
        
    } catch {
        Write-Error "❌ Erreur lors de la désinstallation : $($_.Exception.Message)"
        return $false
    }
}

function Start-CryptUSBeeService {
    Write-Host "🚀 Démarrage du service CryptUSBee..." -ForegroundColor Green
    
    try {
        Start-Service -Name $ServiceName
        Write-Host "✅ Service CryptUSBee démarré avec succès!" -ForegroundColor Green
        return $true
    } catch {
        Write-Error "❌ Erreur lors du démarrage : $($_.Exception.Message)"
        return $false
    }
}

function Stop-CryptUSBeeService {
    Write-Host "⏹️ Arrêt du service CryptUSBee..." -ForegroundColor Yellow
    
    try {
        Stop-Service -Name $ServiceName -Force
        Write-Host "✅ Service CryptUSBee arrêté avec succès!" -ForegroundColor Green
        return $true
    } catch {
        Write-Error "❌ Erreur lors de l'arrêt : $($_.Exception.Message)"
        return $false
    }
}

function Show-ServiceStatus {
    Write-Host "📊 Statut du service CryptUSBee:" -ForegroundColor Cyan
    
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service) {
        Write-Host "   Nom: $($service.Name)" -ForegroundColor White
        Write-Host "   Statut: $($service.Status)" -ForegroundColor $(if ($service.Status -eq "Running") { "Green" } else { "Red" })
        Write-Host "   Type de démarrage: $($service.StartType)" -ForegroundColor White
    } else {
        Write-Host "   ❌ Service non installé" -ForegroundColor Red
    }
}

# Configuration du pare-feu
function Configure-Firewall {
    Write-Host "🔥 Configuration du pare-feu Windows..." -ForegroundColor Cyan
    
    try {
        # Règle pour le port WebSocket (8765 par défaut)
        $ruleName = "CryptUSBee WebSocket"
        $existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
        
        if ($existingRule) {
            Write-Host "⚠️ Règle de pare-feu existante trouvée, suppression..." -ForegroundColor Yellow
            Remove-NetFirewallRule -DisplayName $ruleName
        }
        
        Write-Host "🔥 Création de la règle de pare-feu..." -ForegroundColor Green
        New-NetFirewallRule -DisplayName $ruleName `
                           -Direction Inbound `
                           -Protocol TCP `
                           -LocalPort 8765 `
                           -Action Allow `
                           -Profile Domain,Private `
                           -Description "Autoriser les connexions WebSocket pour CryptUSBee"
        
        Write-Host "✅ Pare-feu configuré avec succès!" -ForegroundColor Green
        
    } catch {
        Write-Warning "⚠️ Impossible de configurer le pare-feu : $($_.Exception.Message)"
    }
}

# Exécution des actions
Write-Host "🔐 CryptUSBee Service Manager" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

if ($Install) {
    if (Install-CryptUSBeeService) {
        Configure-Firewall
        Start-CryptUSBeeService
    }
} elseif ($Uninstall) {
    Uninstall-CryptUSBeeService
} elseif ($Start) {
    Start-CryptUSBeeService
} elseif ($Stop) {
    Stop-CryptUSBeeService
} else {
    Write-Host "Usage:"
    Write-Host "  .\install_service.ps1 -Install    # Installer et démarrer le service"
    Write-Host "  .\install_service.ps1 -Uninstall  # Désinstaller le service"
    Write-Host "  .\install_service.ps1 -Start      # Démarrer le service"
    Write-Host "  .\install_service.ps1 -Stop       # Arrêter le service"
    Write-Host ""
}

Show-ServiceStatus
