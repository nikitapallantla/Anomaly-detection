# Define your service chain
$services = @(
    @{ name = "api-gateway";    port = 5000; next = "localhost:5001" },
    @{ name = "fraud-service";  port = 5001; next = "localhost:5002" },
    @{ name = "payment-svc";    port = 5002; next = "localhost:5003" },
    @{ name = "shipping-svc";   port = 5003; next = $null } # End of chain
)

foreach ($s in $services) {
    Write-Host "Starting $($s.name) on port $($s.port)..." -ForegroundColor Cyan
    
    # Set the environment variables for this specific process
    $env:SERVICE_NAME = $s.name
    $env:SERVICE_PORT = $s.port
    $env:NEXT_SERVICE = $s.next
    
    # Start the service in its own window
    Start-Process powershell -ArgumentList "python app.py"
}