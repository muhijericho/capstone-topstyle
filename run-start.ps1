param(
    [switch]$SkipDependencies,
    [switch]$SkipMigrations,
    [string]$Port = "8000",
    [string]$BindHost = "0.0.0.0"
)

# run-start.ps1 - safe launcher that runs START_SYSTEM.ps1 from the script folder
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $scriptDir
try {
    $argsList = @()
    if ($SkipDependencies) { $argsList += "-SkipDependencies" }
    if ($SkipMigrations) { $argsList += "-SkipMigrations" }
    if ($Port) { $argsList += "-Port"; $argsList += $Port }
    if ($BindHost) { $argsList += "-BindHost"; $argsList += $BindHost }

    Write-Host "Running START_SYSTEM_clean.ps1 from: $scriptDir" -ForegroundColor Cyan
    # Call the clean startup script with the constructed args
    & "${scriptDir}\START_SYSTEM_clean.ps1" @argsList
}
finally {
    Pop-Location
}
