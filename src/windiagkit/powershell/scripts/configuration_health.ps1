function Write-Status {
    param([string]$Status, [string]$Check, [string]$Details)
    Write-Host ('[{0,-7}] {1}: {2}' -f $Status, $Check, $Details)
}

Write-Host 'Hardware and configuration health'
Write-Host ('Captured: {0}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'))
Write-Host ''

try {
    $physicalDisks = @(Get-PhysicalDisk -ErrorAction Stop)
    if ($physicalDisks.Count -eq 0) {
        Write-Status 'INFO' 'Physical disks' 'No Storage-module disk data was returned.'
    }
    foreach ($disk in $physicalDisks) {
        $health = [string]$disk.HealthStatus
        $status = if ($health -eq 'Healthy') { 'OK' } else { 'WARNING' }
        Write-Status $status 'Physical disk' (
            '{0}: health={1}, operational={2}, media={3}, size={4:N1} GiB' -f $disk.FriendlyName,
                $health,
                ($disk.OperationalStatus -join ','),
                $disk.MediaType,
                ($disk.Size / 1GB)
        )
    }
} catch {
    Write-Status 'INFO' 'Physical disks' 'Storage-module health data is unavailable.'
}

$pendingReasons = @()
$pendingPaths = @(
    'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending',
    'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired'
)
foreach ($path in $pendingPaths) {
    if (Test-Path -LiteralPath $path) {
        $pendingReasons += $path
    }
}
try {
    $pendingRenameQuery = @{
        LiteralPath = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager'
        Name = 'PendingFileRenameOperations'
        ErrorAction = 'Stop'
    }
    $pendingRename = Get-ItemProperty @pendingRenameQuery
    if ($pendingRename.PendingFileRenameOperations) {
        $pendingReasons += 'Pending file rename operations'
    }
} catch {
    # A missing value means no pending file rename operation.
}

if ($pendingReasons.Count -eq 0) {
    Write-Status 'OK' 'Pending restart' 'No common pending-restart indicators found.'
} else {
    Write-Status 'WARNING' 'Pending restart' ($pendingReasons -join '; ')
}

try {
    $powerScheme = (& powercfg.exe /GetActiveScheme 2>$null) -join ' '
    if ($LASTEXITCODE -eq 0 -and $powerScheme) {
        Write-Status 'INFO' 'Active power plan' $powerScheme.Trim()
    } else {
        Write-Status 'WARNING' 'Active power plan' 'The active plan could not be queried.'
    }
} catch {
    Write-Status 'WARNING' 'Active power plan' $_.Exception.Message
}

try {
    $deviceQuery = @{
        ClassName = 'Win32_PnPEntity'
        Filter = 'ConfigManagerErrorCode <> 0'
        ErrorAction = 'Stop'
    }
    $deviceErrors = @(Get-CimInstance @deviceQuery)
    if ($deviceErrors.Count -eq 0) {
        Write-Status 'OK' 'Device Manager' 'No device configuration errors found.'
    } else {
        Write-Status 'WARNING' 'Device Manager' (
            '{0} device(s) report configuration errors.' -f $deviceErrors.Count
        )
        $deviceErrors |
            Select-Object -First 20 Name, PNPClass, ConfigManagerErrorCode |
            Format-Table -AutoSize
    }
} catch {
    Write-Status 'ERROR' 'Device Manager' $_.Exception.Message
}

try {
    $serviceQuery = @{
        ClassName = 'Win32_Service'
        Filter = "StartMode='Auto' AND State<>'Running'"
        ErrorAction = 'Stop'
    }
    $stoppedServices = @(Get-CimInstance @serviceQuery)
    if ($stoppedServices.Count -eq 0) {
        Write-Status 'OK' 'Automatic services' 'All automatic services report as running.'
    } else {
        Write-Status 'INFO' 'Automatic services' (
            '{0} service(s) are stopped; trigger-start services may make this normal.' -f
                $stoppedServices.Count
        )
        $stoppedServices |
            Select-Object -First 20 Name, DisplayName, State, StartMode |
            Format-Table -AutoSize
    }
} catch {
    Write-Status 'ERROR' 'Automatic services' $_.Exception.Message
}
