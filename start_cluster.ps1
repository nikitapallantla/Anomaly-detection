# # ==========================================
# # Microservices Cluster Launcher (Updated)
# # ==========================================

# # Set Global OTel Environment Variables
# $env:OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
# $env:OTEL_TRACES_EXPORTER="otlp"
# $env:OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED="true"

# Write-Host "🚀 Starting Microservices Cluster..." -ForegroundColor Cyan

# # Start API Gateway (using your folder structure)
# $env:OTEL_SERVICE_NAME="api-gateway"
# Start-Process powershell "-NoExit", "-Command", "Set-Location '$PWD'; $env:OTEL_SERVICE_NAME='api-gateway'; "opentelemetry-instrument python services/api-gateway/app.py"

# # Start Auth Service
# $env:OTEL_SERVICE_NAME="auth-service"
# Start-Process powershell "-NoExit", "-Command", "Set-Location '$PWD'; $env:OTEL_SERVICE_NAME='auth-service'; "opentelemetry-instrument python services/auth-service/app.py"

# # Start Transaction Service
# $env:OTEL_SERVICE_NAME="transaction-service"
# Start-Process powershell "-NoExit", "-Command", "opentelemetry-instrument python services/transaction-service/app.py"

# # Start Payment Service
# $env:OTEL_SERVICE_NAME="payment-service"
# Start-Process powershell "-NoExit", "-Command", "opentelemetry-instrument python services/payment-service/app.py"

# # Start Notification Service
# $env:OTEL_SERVICE_NAME="notification-service"
# Start-Process powershell "-NoExit", "-Command", "opentelemetry-instrument python services/notification-service/app.py"

# Write-Host "✅ All services are launching. Wait 15 seconds for them to warm up!" -ForegroundColor Green

$env:OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
$env:OTEL_TRACES_EXPORTER="otlp"

Write-Host "🚀 Starting Microservices Cluster..." -ForegroundColor Cyan

# Use absolute paths to be 100% sure
$basePath = "C:\Users\nikit\OneDrive\Desktop\Anomaly-1"

# The corrected service list (syntax fixed)
$services = @(
    @{name="api-gateway"; path="services/api-gateway/app.py"},
    @{name="auth-service"; path="services/auth-service/app.py"},
    @{name="user-service"; path="services/user-service/app.py"},
    @{name="transaction-service"; path="services/transaction-service/app.py"},
    @{name="account-service"; path="services/account-service/app.py"},
    @{name="fraud-service"; path="services/fraud-service/app.py"},
    @{name="notification-service"; path="services/notification-service/app.py"},
    @{name="audit-service"; path="services/audit-service/app.py"},
    @{name="database-service"; path="services/database-service/app.py"}
)

foreach ($svc in $services) {
    $name = $svc.name
    $fullPath = "$basePath\$($svc.path)"
    
    if (Test-Path $fullPath) {
        # We use just 'python' because your script already handles instrumentation
        $cmd = "cd '$basePath'; python '$fullPath'"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
        Write-Host "✅ Launching $name..." -ForegroundColor Yellow
        Start-Sleep -Seconds 1 
    } else {
        Write-Host "❌ File Not Found: $fullPath" -ForegroundColor Red
    }
}

Write-Host "`n---`n✅ All 9 windows triggered!" -ForegroundColor Green