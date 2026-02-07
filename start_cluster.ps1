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


# ==========================================
# Microservices Cluster Launcher (Final Fix)
# ==========================================

$env:OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
$env:OTEL_TRACES_EXPORTER="otlp"

Write-Host "🚀 Starting Microservices Cluster..." -ForegroundColor Cyan

# Service Configuration List
$services = @(
    @{name="api-gateway"; path="services/api-gateway/app.py"},
    @{name="auth-service"; path="services/auth-service/app.py"},
    @{name="transaction-service"; path="services/transaction-service/app.py"},
    @{name="payment-service"; path="services/payment-service/app.py"},
    @{name="notification-service"; path="services/notification-service/app.py"}
)

foreach ($svc in $services) {
    $name = $svc.name
    $path = $svc.path
    # We use a single string with escaped quotes to ensure it travels to the new window correctly
    $cmd = "Set-Location '$PWD'; `$env:OTEL_SERVICE_NAME='$name'; opentelemetry-instrument python $path"
    
    Start-Process powershell "-NoExit", "-Command", $cmd
    Write-Host "Starting $name..." -ForegroundColor Yellow
}

Write-Host "✅ All windows opened. Check them for errors!" -ForegroundColor Green