param(
    [Parameter(Mandatory = $true)]
    [string]$HostName
)

Write-Host "DNS resolution for: $HostName"
Write-Host ''

foreach ($recordType in @('A', 'AAAA')) {
    Write-Host "${recordType} records:"
    try {
        $records = @(Resolve-DnsName -Name $HostName -Type $recordType -ErrorAction Stop)
        $addresses = @($records |
            Where-Object { $_.IPAddress } |
            Select-Object -ExpandProperty IPAddress -Unique)
        if ($addresses.Count -eq 0) {
            Write-Host '  No address records returned.'
        } else {
            foreach ($address in $addresses) {
                Write-Host "  $address"
            }
        }
    } catch {
        Write-Host "  Resolution failed: $($_.Exception.Message)"
    }
    Write-Host ''
}
