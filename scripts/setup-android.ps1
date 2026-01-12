# Check if running as administrator
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Please run this script as Administrator to set system environment variables." -ForegroundColor Yellow
    Write-Host "Right-click on PowerShell and select 'Run as administrator'." -ForegroundColor Yellow
    exit 1
}

$sdkPath = "C:\Users\LOQ\AppData\Local\Android\Sdk"
$platformTools = "$sdkPath\platform-tools"
$emulator = "$sdkPath\emulator"

# 1. Set ANDROID_HOME
Write-Host "Setting ANDROID_HOME to $sdkPath..."
[System.Environment]::SetEnvironmentVariable("ANDROID_HOME", $sdkPath, [System.EnvironmentVariableTarget]::User)

# 2. Add to PATH
$currentPath = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::User)
$needsUpdate = $false

if ($currentPath -notlike "*$platformTools*") {
    Write-Host "Adding platform-tools to PATH..."
    $currentPath = "$currentPath;$platformTools"
    $needsUpdate = $true
} else {
    Write-Host "platform-tools already in PATH."
}

if ($currentPath -notlike "*$emulator*") {
    Write-Host "Adding emulator to PATH..."
    $currentPath = "$currentPath;$emulator"
    $needsUpdate = $true
} else {
    Write-Host "emulator already in PATH."
}

if ($needsUpdate) {
    [System.Environment]::SetEnvironmentVariable("Path", $currentPath, [System.EnvironmentVariableTarget]::User)
    Write-Host "PATH updated." -ForegroundColor Green
}

Write-Host "Environment variables set." -ForegroundColor Green
Write-Host "Please RESTART your terminal (or VS Code) for changes to take effect." -ForegroundColor Cyan

