param(
    [ValidateRange(1, 1440)]
    [int]$Minutes = 15,
    [ValidateRange(1, 1000)]
    [int]$MaxEvents = 100
)

$start = (Get-Date).AddMinutes(-$Minutes)
Write-Host "System log - Critical / Error / Warning"
Write-Host "Window: last $Minutes minute(s)"
Write-Host ""

try {
    $events = @(Get-WinEvent -FilterHashtable @{
        LogName = 'System'
        StartTime = $start
        Level = 1,2,3
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
