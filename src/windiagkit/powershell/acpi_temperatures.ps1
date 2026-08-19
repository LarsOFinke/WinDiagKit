Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction SilentlyContinue |
ForEach-Object { '{0:F1}' -f (($_.CurrentTemperature / 10.0) - 273.15) }
