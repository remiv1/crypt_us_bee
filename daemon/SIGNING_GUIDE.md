# Guide de Signature de Code pour CryptUSBee

## 🔐 Processus de Signature Numérique

La signature de code est essentielle pour garantir l'authenticité et l'intégrité des exécutables et des packages MSI CryptUSBee.

## 📋 Prérequis

### 1. Certificat de Signature de Code

Vous avez besoin d'un certificat de signature de code valide. Voici les options :

#### Options Certificats

- **Certificat Commercial** (Recommandé)
  - DigiCert, GlobalSign, Sectigo, etc.
  - Certificat EV (Extended Validation) pour éviter les avertissements SmartScreen
  - Coût: ~300-600€/an

- **Certificat Auto-signé** (Développement uniquement)
  - Gratuit mais non reconnu par Windows
  - Génère des avertissements de sécurité

#### Achat d'un Certificat Commercial

1. [**DigiCert**](https://www.digicert.com/code-signing/)
2. [**GlobalSign**](https://www.globalsign.com/en/code-signing-certificate)
3. [**Sectigo**](https://sectigo.com/ssl-certificates-tls/code-signing)

### 2. Outils Nécessaires

#### Windows SDK

```powershell
# Installation via Visual Studio Installer ou téléchargement direct
# Windows 10/11 SDK inclut SignTool.exe
winget install Microsoft.WindowsSDK
```

#### Utilitaires PowerShell

```powershell
# Module pour la gestion des certificats
Install-Module -Name PKI -Force
```

## 🔧 Configuration des Certificats

### 1. Installation du Certificat

#### Méthode 1: Fichier PFX/P12

```powershell
# Import du certificat dans le magasin personnel
$certPath = "C:\path\to\certificate.pfx"
$certPassword = Read-Host -AsSecureString "Mot de passe du certificat"

Import-PfxCertificate -FilePath $certPath -CertStoreLocation "Cert:\CurrentUser\My" -Password $certPassword
```

#### Méthode 2: Token USB/HSM

```powershell
# Pour les certificats sur token USB (ex: SafeNet eToken)
# Installation du driver CSP approprié nécessaire
```

### 2. Vérification du Certificat

```powershell
# Lister les certificats de signature de code
Get-ChildItem -Path "Cert:\CurrentUser\My" -CodeSigningCert

# Vérifier la validité
$cert = Get-ChildItem -Path "Cert:\CurrentUser\My" -CodeSigningCert | Select-Object -First 1
$cert.NotAfter  # Date d'expiration
$cert.Thumbprint  # Empreinte
```

## 📝 Scripts de Signature

### 1. Signature Automatique

Créer un fichier `sign_config.json` :

```json
{
    "certificate": {
        "store_location": "CurrentUser",
        "store_name": "My",
        "thumbprint": "VOTRE_EMPREINTE_CERTIFICAT",
        "pfx_path": "C:\\path\\to\\cert.pfx",
        "pfx_password": "VOTRE_MOT_DE_PASSE"
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

### 2. Script PowerShell de Signature

```powershell
# sign_cryptusbee.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$ConfigPath,
    
    [Parameter(Mandatory=$true)]
    [string]$TargetDirectory
)

function Sign-CryptUSBeeFiles {
    param($Config, $Directory)
    
    $cert = $Config.certificate
    $timestamp = $Config.timestamp
    
    foreach ($fileName in $Config.files_to_sign) {
        $filePath = Join-Path $Directory $fileName
        
        if (Test-Path $filePath) {
            Write-Host "🖊️ Signature de $fileName..." -ForegroundColor Green
            
            if ($cert.pfx_path) {
                # Signature avec fichier PFX
                & signtool.exe sign `
                    /f $cert.pfx_path `
                    /p $cert.pfx_password `
                    /t $timestamp.url `
                    /fd $timestamp.algorithm `
                    /v $filePath
            } else {
                # Signature avec certificat du magasin
                & signtool.exe sign `
                    /sha1 $cert.thumbprint `
                    /t $timestamp.url `
                    /fd $timestamp.algorithm `
                    /v $filePath
            }
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "$fileName signé avec succès" -ForegroundColor Green
            } else {
                Write-Host "Échec de la signature de $fileName" -ForegroundColor Red
            }
        } else {
            Write-Host "Fichier non trouvé: $fileName" -ForegroundColor Yellow
        }
    }
}

# Chargement de la configuration
$config = Get-Content $ConfigPath | ConvertFrom-Json

# Signature des fichiers
Sign-CryptUSBeeFiles -Config $config -Directory $TargetDirectory
```

### 3. Intégration avec le Build

Modifier le script `build.ps1` pour inclure la signature automatique :

```powershell
# Ajout des paramètres de signature
param(
    # ... paramètres existants ...
    [switch]$AutoSign,
    [string]$SignConfigPath = "sign_config.json"
)

# Après le build réussi
if ($AutoSign -and (Test-Path $SignConfigPath)) {
    Write-ColoredOutput "🖊️ Signature automatique des fichiers..." "Blue"
    & .\sign_cryptusbee.ps1 -ConfigPath $SignConfigPath -TargetDirectory $DistDir
}
```

## 🔍 Vérification de la Signature

### 1. Vérification avec SignTool

```powershell
# Vérifier la signature d'un fichier
signtool.exe verify /pa /v "cryptusbee_daemon.exe"

# Vérifier avec informations détaillées
signtool.exe verify /pa /v /tw "cryptusbee_daemon.exe"
```

### 2. Script de Vérification PowerShell

```powershell
function Test-FileSignature {
    param([string]$FilePath)
    
    $signature = Get-AuthenticodeSignature $FilePath
    
    Write-Host "Fichier: $(Split-Path $FilePath -Leaf)" -ForegroundColor Cyan
    Write-Host "Statut: $($signature.Status)" -ForegroundColor $(if ($signature.Status -eq "Valid") { "Green" } else { "Red" })
    Write-Host "Certificat: $($signature.SignerCertificate.Subject)" -ForegroundColor White
    Write-Host "Horodatage: $($signature.TimeStamperCertificate.Subject)" -ForegroundColor White
    Write-Host ""
}

# Vérification de tous les fichiers signés
Get-ChildItem "dist\" -Include "*.exe", "*.msi" -Recurse | ForEach-Object {
    Test-FileSignature $_.FullName
}
```

## 🚀 Automatisation CI/CD

### 1. GitHub Actions

```yaml
# .github/workflows/sign-and-release.yml
name: Build and Sign CryptUSBee

on:
  push:
    tags: ['v*']

jobs:
  build-and-sign:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r daemon/requirements-daemon.txt
        pip install pyinstaller
    
    - name: Decode certificate
      env:
        CERTIFICATE_BASE64: ${{ secrets.CODESIGN_CERTIFICATE }}
      run: |
        $bytes = [Convert]::FromBase64String($env:CERTIFICATE_BASE64)
        [IO.File]::WriteAllBytes("cert.pfx", $bytes)
    
    - name: Build and sign
      env:
        CERT_PASSWORD: ${{ secrets.CODESIGN_PASSWORD }}
      run: |
        cd daemon/packaging
        .\build.ps1 -All -Sign -CertificatePath "..\..\cert.pfx" -CertificatePassword $env:CERT_PASSWORD
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: cryptusbee-signed
        path: daemon/dist/
```

### 2. Secrets GitHub Requis

Dans les paramètres du repository GitHub :

- `CODESIGN_CERTIFICATE`: Certificat PFX encodé en Base64
- `CODESIGN_PASSWORD`: Mot de passe du certificat

### 3. Génération du Base64

```powershell
# Encoder le certificat en Base64 pour GitHub Secrets
$certBytes = [System.IO.File]::ReadAllBytes("cert.pfx")
$certBase64 = [System.Convert]::ToBase64String($certBytes)
$certBase64 | Out-File "cert_base64.txt"
```

## 🛡️ Bonnes Pratiques de Sécurité

### 1. Protection du Certificat

- ✅ Stockage sécurisé du certificat (HSM recommandé)
- ✅ Mot de passe fort et unique
- ✅ Limitation d'accès au certificat
- ✅ Révocation immédiate en cas de compromission

### 2. Horodatage

- ✅ Toujours utiliser un serveur d'horodatage
- ✅ URLs recommandées :
  - `http://timestamp.digicert.com`
  - `http://timestamp.globalsign.com/scripts/timstamp.dll`
  - `http://timestamp.comodoca.com/authenticode`

### 3. Vérification

- ✅ Tester la signature avant distribution
- ✅ Vérifier sur des machines propres
- ✅ Contrôler les avertissements SmartScreen

## 📚 Ressources Additionnelles

### Documentation Microsoft

- [Signature de code avec SignTool](https://docs.microsoft.com/en-us/windows/msix/package/sign-app-package-using-signtool)
- [Certificats de signature de code](https://docs.microsoft.com/en-us/windows-hardware/drivers/dashboard/get-a-code-signing-certificate)

### Outils Utiles

- **Windows SDK**: SignTool.exe
- **OpenSSL**: Gestion des certificats
- **DigiCert Certificate Utility**: Outil de gestion DigiCert
- **GlobalSign CodeSigning**: Outil GlobalSign

Ce guide vous permettra de mettre en place un processus complet de signature de code pour CryptUSBee, garantissant la confiance des utilisateurs et évitant les avertissements de sécurité.
