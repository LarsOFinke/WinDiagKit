param(
    [string]$ProcessNamesCsv = '',
    [ValidateRange(5, 50)]
    [int]$TopCount = 15
)

$targetNames = @($ProcessNamesCsv.Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ })

Write-Host 'Process resource snapshot'
Write-Host ('Captured: {0}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'))
Write-Host 'CPU is cumulative processor time since process start; memory values are current.'
Write-Host ''

try {
    $processes = @(Get-Process -ErrorAction Stop)
} catch {
    Write-Host "Could not query processes: $($_.Exception.Message)"
    exit 1
}

$projection = @{
    Property = @(
        'ProcessName',
        'Id',
        @{Name = 'CPU_s'; Expression = { if ($null -eq $_.CPU) { 0 } else { [math]::Round($_.CPU, 1) } }},
        @{Name = 'WorkingSet_MiB'; Expression = { [math]::Round($_.WorkingSet64 / 1MB, 1) }},
        @{Name = 'Private_MiB'; Expression = { [math]::Round($_.PrivateMemorySize64 / 1MB, 1) }},
        'HandleCount',
        @{Name = 'Threads'; Expression = { $_.Threads.Count }},
        'Responding'
    )
}

function Show-TopProcesses {
    param(
        [object[]]$Processes,
        [string]$SortProperty,
        [int]$Count,
        [string]$Title,
        [hashtable]$Properties
    )

    Write-Host $Title
    $Processes |
        Sort-Object $SortProperty -Descending |
        Select-Object -First $Count |
        Select-Object @Properties |
        Format-Table -AutoSize
}

$totalHandles = ($processes | Measure-Object -Property HandleCount -Sum).Sum
$totalThreads = ($processes | ForEach-Object { $_.Threads.Count } | Measure-Object -Sum).Sum
Write-Host ('System totals: {0} processes, {1} threads, {2} handles' -f $processes.Count, $totalThreads, $totalHandles)
Write-Host ''

if ($targetNames.Count -gt 0) {
    Write-Host ('Configured targets: {0}' -f ($targetNames -join ', '))
    $targets = @($processes | Where-Object { $targetNames -contains $_.ProcessName })
    if ($targets.Count -eq 0) {
        Write-Host 'None of the configured target processes are currently running.'
    } else {
        $targets | Sort-Object ProcessName, Id | Select-Object @projection | Format-Table -AutoSize
    }
    Write-Host ''
} else {
    Write-Host 'No target process names are configured.'
    Write-Host ''
}

Show-TopProcesses $processes 'PrivateMemorySize64' $TopCount "Top $TopCount processes by private memory:" $projection
Show-TopProcesses $processes 'CPU' $TopCount "Top $TopCount processes by cumulative CPU time:" $projection
Show-TopProcesses $processes 'HandleCount' $TopCount "Top $TopCount processes by handle count:" $projection
