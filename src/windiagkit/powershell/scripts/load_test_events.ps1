$start = (Get-Date).AddMinutes(-__MINUTES__)
$applicationProviders = @(
    'Application Error',
    'Application Hang',
    '.NET Runtime',
    'Windows Error Reporting',
    'SideBySide'
)
$systemProviders = @(
    'WHEA-Logger',
    'Disk',
    'Ntfs',
    'stornvme',
    'storahci',
    'storport',
    'volmgr',
    'Display',
    'nvlddmkm',
    'Microsoft-Windows-Kernel-Power',
    'Microsoft-Windows-Kernel-Processor-Power',
    'EventLog',
    'Microsoft-Windows-Resource-Exhaustion-Detector',
    'Microsoft-Windows-WER-SystemErrorReporting',
    'Service Control Manager',
    'Tcpip',
    'Microsoft-Windows-TCPIP',
    'Microsoft-Windows-NDIS',
    'Microsoft-Windows-DNS-Client'
)

function Get-ProviderEvents {
    param(
        [string]$LogName,
        [string[]]$Providers,
        [datetime]$StartTime,
        [int]$MaximumEvents
    )

    foreach ($provider in $Providers) {
        $metadata = Get-WinEvent -ListProvider $provider -ErrorAction SilentlyContinue
        if (-not $metadata -or $metadata.LogLinks.LogName -notcontains $LogName) {
            continue
        }
        try {
            Get-WinEvent -FilterHashtable @{
                LogName = $LogName
                ProviderName = $provider
                StartTime = $StartTime
                Level = 1, 2, 3
            } -MaxEvents $MaximumEvents -ErrorAction Stop
        } catch {
            if ($_.FullyQualifiedErrorId -notlike 'NoMatchingEventsFound*') {
                Write-Host "Could not query $provider in ${LogName}: $($_.Exception.Message)"
            }
        }
    }
}

Write-Host 'Load-test relevant event triage'
Write-Host "Window: last __MINUTES__ minute(s)"
Write-Host 'Logs: System and Application'
Write-Host ''

$matches = @(
    Get-ProviderEvents 'Application' $applicationProviders $start __MAX_EVENTS__
    Get-ProviderEvents 'System' $systemProviders $start __MAX_EVENTS__
)

$matches = @($matches | Sort-Object TimeCreated -Descending | Select-Object -First __MAX_EVENTS__)
if ($matches.Count -eq 0) {
    Write-Host 'No load-test-relevant warnings or errors were found.'
    exit
}

Write-Host 'Summary by provider, event ID, and level:'
$matches |
    Group-Object ProviderName, Id, LevelDisplayName |
    Sort-Object Count -Descending |
    Select-Object Count, Name |
    Format-Table -AutoSize

Write-Host 'Event details:'
$matches |
    Select-Object TimeCreated, LogName, Id, LevelDisplayName, ProviderName, Message |
    Format-List
