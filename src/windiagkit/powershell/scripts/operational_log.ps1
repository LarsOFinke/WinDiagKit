param(
    [Parameter(Mandatory = $true)]
    [string]$LogName,
    [ValidateRange(1, 1440)]
    [int]$Minutes = 15,
    [ValidateRange(1, 1000)]
    [int]$MaxEvents = 100
)

try {
    $log = Get-WinEvent -ListLog $LogName -ErrorAction Stop
} catch {
    Write-Host "Could not inspect log: $($_.Exception.Message)"
    exit 1
}
if (-not $log) {
    Write-Host "Log not available: $LogName"
    exit
}

Write-Host "Log: $LogName"
Write-Host "Enabled: $($log.IsEnabled)"
Write-Host "Window: last $Minutes minute(s)"
Write-Host ""

if (-not $log.IsEnabled) {
    Write-Host "This Operational log is currently disabled."
    Write-Host "WinDiagKit will not enable it automatically because that changes system state."
    exit
}

$start = (Get-Date).AddMinutes(-$Minutes)
try {
    $events = @(Get-WinEvent -FilterHashtable @{
        LogName = $LogName
        StartTime = $start
    } -ErrorAction Stop |
    Select-Object -First $MaxEvents TimeCreated, Id, LevelDisplayName, ProviderName, Message)
} catch {
    if ($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*') {
        Write-Host "No matching events found."
        exit
    }
    Write-Host "Event query failed: $($_.Exception.Message)"
    exit 1
}

if ($events.Count -eq 0) {
    Write-Host "No matching events found."
} else {
    $events | Format-List
}
