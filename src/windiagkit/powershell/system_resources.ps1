function Write-Status {
    param([string]$Status, [string]$Check, [string]$Details)
    Write-Host ('[{0,-7}] {1}: {2}' -f $Status, $Check, $Details)
}

Write-Host 'System resources and load-test readiness'
Write-Host ('Captured: {0}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'))
Write-Host ''

try {
    $os = Get-CimInstance -ClassName Win32_OperatingSystem -ErrorAction Stop
    $computer = Get-CimInstance -ClassName Win32_ComputerSystem -ErrorAction Stop
    $uptime = (Get-Date) - $os.LastBootUpTime
    Write-Status 'INFO' 'Operating system' (
        '{0} ({1}), build {2}' -f $os.Caption, $os.OSArchitecture, $os.BuildNumber
    )
    Write-Status 'INFO' 'Uptime' (
        '{0} day(s), {1} hour(s)' -f [int]$uptime.TotalDays, $uptime.Hours
    )

    $totalMemory = [double]$os.TotalVisibleMemorySize
    $freeMemory = [double]$os.FreePhysicalMemory
    $freePercent = if ($totalMemory -gt 0) {
        100.0 * $freeMemory / $totalMemory
    } else {
        0.0
    }
    $status = if ($freePercent -lt 15.0) { 'WARNING' } else { 'OK' }
    Write-Status $status 'Available memory' (
        '{0:N1}% ({1:N1} GiB of {2:N1} GiB)' -f $freePercent,
            ($freeMemory / 1MB),
            ($totalMemory / 1MB)
    )
    Write-Status 'INFO' 'Automatic page file' ([string]$computer.AutomaticManagedPagefile)
} catch {
    Write-Status 'ERROR' 'Operating system and memory' $_.Exception.Message
}

try {
    $processors = @(Get-CimInstance -ClassName Win32_Processor -ErrorAction Stop)
    $logicalCount = ($processors |
        Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum
    $load = ($processors | Measure-Object -Property LoadPercentage -Average).Average
    $cpuNames = ($processors | Select-Object -ExpandProperty Name -Unique) -join '; '
    Write-Status 'INFO' 'Processor' $cpuNames
    Write-Status 'INFO' 'Logical processors' ([string]$logicalCount)
    Write-Status 'INFO' 'Current processor load' ('{0:N1}%' -f $load)
} catch {
    Write-Status 'ERROR' 'Processor' $_.Exception.Message
}

try {
    $pageFiles = @(Get-CimInstance -ClassName Win32_PageFileUsage -ErrorAction Stop)
    if ($pageFiles.Count -eq 0) {
        Write-Status 'WARNING' 'Page file' 'No active page file was reported.'
    } else {
        foreach ($pageFile in $pageFiles) {
            Write-Status 'INFO' 'Page file' (
                '{0}: {1:N0} MiB allocated, {2:N0} MiB used, {3:N0} MiB peak' -f $pageFile.Name,
                    $pageFile.AllocatedBaseSize,
                    $pageFile.CurrentUsage,
                    $pageFile.PeakUsage
            )
        }
    }
} catch {
    Write-Status 'ERROR' 'Page file' $_.Exception.Message
}

try {
    $diskQuery = @{
        ClassName = 'Win32_LogicalDisk'
        Filter = 'DriveType=3'
        ErrorAction = 'Stop'
    }
    $disks = @(Get-CimInstance @diskQuery)
    foreach ($disk in $disks) {
        if ($disk.Size -le 0) {
            continue
        }
        $freePercent = 100.0 * [double]$disk.FreeSpace / [double]$disk.Size
        $status = if ($freePercent -lt 15.0) { 'WARNING' } else { 'OK' }
        Write-Status $status ('Disk {0}' -f $disk.DeviceID) (
            '{0:N1}% free ({1:N1} GiB of {2:N1} GiB)' -f $freePercent,
                ($disk.FreeSpace / 1GB),
                ($disk.Size / 1GB)
        )
    }
} catch {
    Write-Status 'ERROR' 'Disk capacity' $_.Exception.Message
}
