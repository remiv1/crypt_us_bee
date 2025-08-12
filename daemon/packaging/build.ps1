# Script de build pour créer les packages CryptUSBee
param(
    [switch]$BuildWindows,
    [switch]$BuildLinux,
    [switch]$BuildMSI,
    [switch]$Sign,
    [string]$CertificatePath = "",
    [string]$CertificatePassword = "",
    [switch]$Clean,
    [switch]$All
)

# Configuration
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BuildDir = Join-Path $ProjectRoot "build"
$DistDir = Join-Path $ProjectRoot "dist"
$PackagingDir = Join-Path $ProjectRoot "packaging"

# Couleurs pour l'affichage
function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    switch ($Color) {
        "Green" { Write-Host $Message -ForegroundColor Green }
        "Red" { Write-Host $Message -ForegroundColor Red }
        "Yellow" { Write-Host $Message -ForegroundColor Yellow }
        "Blue" { Write-Host $Message -ForegroundColor Blue }
        "Cyan" { Write-Host $Message -ForegroundColor Cyan }
        default { Write-Host $Message }
    }
}

function Clean-BuildDirectories {
    Write-ColoredOutput "🧹 Nettoyage des répertoires de build..." "Yellow"
    
    if (Test-Path $BuildDir) {
        Remove-Item $BuildDir -Recurse -Force
    }
    
    if (Test-Path $DistDir) {
        Remove-Item $DistDir -Recurse -Force
    }
    
    Write-ColoredOutput "✅ Nettoyage terminé" "Green"
}

function Test-Dependencies {
    Write-ColoredOutput "🔍 Vérification des dépendances..." "Blue"
    
    # Vérification de PyInstaller
    try {
        & pyinstaller --version | Out-Null
        Write-ColoredOutput "✅ PyInstaller détecté" "Green"
    } catch {
        Write-ColoredOutput "❌ PyInstaller non trouvé. Installation..." "Red"
        & pip install pyinstaller
    }
    
    # Vérification de cx_Freeze (pour les builds multi-plateformes)
    try {
        & python -c "import cx_Freeze" 2>$null
        Write-ColoredOutput "✅ cx_Freeze détecté" "Green"
    } catch {
        Write-ColoredOutput "⚠️ cx_Freeze non trouvé. Installation..." "Yellow"
        & pip install cx_Freeze
    }
    
    # Vérification des outils de signature Windows
    if ($Sign -and $IsWindows) {
        $signtool = Get-Command "signtool.exe" -ErrorAction SilentlyContinue
        if (-not $signtool) {
            Write-ColoredOutput "❌ SignTool.exe non trouvé. Installez Windows SDK." "Red"
            return $false
        }
        Write-ColoredOutput "✅ SignTool.exe détecté" "Green"
    }
    
    return $true
}

function Build-WindowsExecutable {
    Write-ColoredOutput "🖥️ Build de l'exécutable Windows..." "Blue"
    
    Push-Location $ProjectRoot
    
    try {
        # Build avec PyInstaller
        $specFile = Join-Path $PackagingDir "cryptusbee_daemon.spec"
        
        if (-not (Test-Path $specFile)) {
            Write-ColoredOutput "❌ Fichier .spec non trouvé: $specFile" "Red"
            return $false
        }
        
        Write-ColoredOutput "📦 Exécution de PyInstaller..." "Cyan"
        & pyinstaller --clean --noconfirm $specFile
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "✅ Build Windows réussi" "Green"
            
            # Copie des fichiers additionnels
            $exeDir = Join-Path $DistDir "CryptUSBeeDaemon"
            Copy-Item (Join-Path $ProjectRoot "scripts\install_service.ps1") $exeDir -Force
            Copy-Item (Join-Path $ProjectRoot "README.md") $exeDir -Force
            
            return $true
        } else {
            Write-ColoredOutput "❌ Échec du build Windows" "Red"
            return $false
        }
        
    } finally {
        Pop-Location
    }
}

function Sign-WindowsExecutable {
    param([string]$ExecutablePath)
    
    Write-ColoredOutput "✍️ Signature de l'exécutable..." "Blue"
    
    if (-not (Test-Path $CertificatePath)) {
        Write-ColoredOutput "❌ Certificat non trouvé: $CertificatePath" "Red"
        return $false
    }
    
    try {
        # Signature avec timestamping
        $signArgs = @(
            "sign",
            "/f", $CertificatePath,
            "/p", $CertificatePassword,
            "/t", "http://timestamp.digicert.com",
            "/fd", "sha256",
            "/v",
            $ExecutablePath
        )
        
        & signtool.exe @signArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "✅ Signature réussie" "Green"
            return $true
        } else {
            Write-ColoredOutput "❌ Échec de la signature" "Red"
            return $false
        }
        
    } catch {
        Write-ColoredOutput "❌ Erreur lors de la signature: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Build-WindowsMSI {
    Write-ColoredOutput "📦 Création du package MSI..." "Blue"
    
    # Vérification de WiX Toolset
    $wixPath = Get-Command "candle.exe" -ErrorAction SilentlyContinue
    if (-not $wixPath) {
        Write-ColoredOutput "❌ WiX Toolset non trouvé. Téléchargez depuis https://wixtoolset.org/" "Red"
        return $false
    }
    
    $wixDir = Join-Path $PackagingDir "wix"
    $wxsFile = Join-Path $wixDir "cryptusbee_daemon.wxs"
    
    if (-not (Test-Path $wxsFile)) {
        Write-ColoredOutput "⚠️ Fichier WiX non trouvé, création automatique..." "Yellow"
        New-WixFile
    }
    
    try {
        Push-Location $wixDir
        
        # Compilation WiX
        Write-ColoredOutput "🔥 Compilation du fichier WiX..." "Cyan"
        & candle.exe "cryptusbee_daemon.wxs" -out "cryptusbee_daemon.wixobj"
        
        if ($LASTEXITCODE -ne 0) {
            Write-ColoredOutput "❌ Échec de la compilation WiX" "Red"
            return $false
        }
        
        # Création du MSI
        Write-ColoredOutput "📦 Création du package MSI..." "Cyan"
        & light.exe "cryptusbee_daemon.wixobj" -out "CryptUSBeeDaemon.msi" -ext WixUIExtension
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "✅ Package MSI créé avec succès" "Green"
            
            # Déplacement vers le répertoire de distribution
            $msiPath = Join-Path $DistDir "CryptUSBeeDaemon.msi"
            Move-Item "CryptUSBeeDaemon.msi" $msiPath -Force
            
            # Signature du MSI si demandée
            if ($Sign -and $CertificatePath) {
                Sign-WindowsExecutable $msiPath
            }
            
            return $true
        } else {
            Write-ColoredOutput "❌ Échec de la création du MSI" "Red"
            return $false
        }
        
    } finally {
        Pop-Location
    }
}

function New-WixFile {
    Write-ColoredOutput "📝 Création du fichier WiX..." "Yellow"
    
    $wixDir = Join-Path $PackagingDir "wix"
    New-Item -ItemType Directory -Path $wixDir -Force | Out-Null
    
    $wxsContent = @"
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="CryptUSBee Daemon" 
           Language="1033" 
           Version="1.0.0.0" 
           Manufacturer="CryptUSBee Project" 
           UpgradeCode="{12345678-1234-1234-1234-123456789012}">
    
    <Package InstallerVersion="200" 
             Compressed="yes" 
             InstallScope="perMachine"
             Description="CryptUSBee USB Authentication Daemon"
             Comments="Service de surveillance USB pour l'authentification CryptUSBee" />

    <MajorUpgrade DowngradeErrorMessage="Une version plus récente de [ProductName] est déjà installée." />
    <MediaTemplate EmbedCab="yes" />

    <Feature Id="ProductFeature" Title="CryptUSBee Daemon" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
    </Feature>
    
    <!-- Interface utilisateur -->
    <UIRef Id="WixUI_Minimal" />
    <WixVariable Id="WixUILicenseRtf" Value="license.rtf" />
    
    <!-- Icône -->
    <Icon Id="icon.ico" SourceFile="icon.ico" />
    <Property Id="ARPPRODUCTICON" Value="icon.ico" />
  </Product>

  <Fragment>
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="CryptUSBee" />
      </Directory>
      
      <Directory Id="ProgramMenuFolder">
        <Directory Id="ApplicationProgramsFolder" Name="CryptUSBee" />
      </Directory>
    </Directory>
  </Fragment>

  <Fragment>
    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
      <Component Id="MainExecutable" Guid="{87654321-4321-4321-4321-210987654321}">
        <File Id="CryptUSBeeDaemonEXE" 
              Source="../../dist/CryptUSBeeDaemon/cryptusbee_daemon.exe" 
              KeyPath="yes" />
        
        <!-- Service Windows -->
        <ServiceInstall Id="CryptUSBeeService"
                       Type="ownProcess"
                       Name="CryptUSBeeDaemon"
                       DisplayName="CryptUSBee Daemon"
                       Description="Service de surveillance USB pour l'authentification CryptUSBee"
                       Start="auto"
                       Account="LocalSystem"
                       ErrorControl="normal" />
        
        <ServiceControl Id="StartCryptUSBeeService"
                       Start="install"
                       Stop="both"
                       Remove="uninstall"
                       Name="CryptUSBeeDaemon"
                       Wait="yes" />
      </Component>
      
      <!-- Scripts et documentation -->
      <Component Id="Scripts" Guid="{11111111-2222-3333-4444-555555555555}">
        <File Id="InstallScript" Source="../../scripts/install_service.ps1" />
        <File Id="ReadMe" Source="../../README.md" />
      </Component>
    </ComponentGroup>
  </Fragment>
</Wix>
"@
    
    $wxsFile = Join-Path $wixDir "cryptusbee_daemon.wxs"
    $wxsContent | Out-File -FilePath $wxsFile -Encoding UTF8
    
    Write-ColoredOutput "✅ Fichier WiX créé: $wxsFile" "Green"
}

function Show-Summary {
    Write-ColoredOutput "`n📊 Résumé du build:" "Cyan"
    Write-ColoredOutput "===================" "Cyan"
    
    if (Test-Path $DistDir) {
        $files = Get-ChildItem $DistDir -Recurse -File
        
        foreach ($file in $files) {
            $size = [math]::Round($file.Length / 1MB, 2)
            Write-ColoredOutput "📄 $($file.Name) ($size MB)" "White"
        }
        
        Write-ColoredOutput "`n📁 Répertoire de sortie: $DistDir" "Green"
    } else {
        Write-ColoredOutput "❌ Aucun fichier de sortie trouvé" "Red"
    }
}

# Exécution principale
Write-ColoredOutput "🔐 CryptUSBee Build System" "Cyan"
Write-ColoredOutput "==========================" "Cyan"

if ($Clean) {
    Clean-BuildDirectories
    exit 0
}

if (-not (Test-Dependencies)) {
    exit 1
}

$success = $true

if ($All -or $BuildWindows) {
    if (-not (Build-WindowsExecutable)) {
        $success = $false
    } elseif ($Sign -and $CertificatePath) {
        $exePath = Join-Path $DistDir "CryptUSBeeDaemon\cryptusbee_daemon.exe"
        if (-not (Sign-WindowsExecutable $exePath)) {
            $success = $false
        }
    }
}

if ($All -or $BuildMSI) {
    if (-not (Build-WindowsMSI)) {
        $success = $false
    }
}

Show-Summary

if ($success) {
    Write-ColoredOutput "`n✅ Build terminé avec succès!" "Green"
    exit 0
} else {
    Write-ColoredOutput "`n❌ Échec du build" "Red"
    exit 1
}
