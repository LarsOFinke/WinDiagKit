$start = (Get-Date).AddMinutes(-__MINUTES__)
Write-Host "System log - Critical / Error / Warning"
Write-Host "Window: last __MINUTES__ minute(s)"
Write-Host ""

try {
    $events = @(Get-WinEvent -FilterHashtable @{
        LogName = 'System'
        StartTime = $start
        Level = 1,2,3
    } -ErrorAction Stop |
    Select-Object -First __MAX_EVENTS__ TimeCreated, Id, LevelDisplayName, ProviderName, Message)
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
