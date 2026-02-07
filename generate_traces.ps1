# ===============================
# Multimodal Microservices Trace Generator with Anomalies
# ===============================

$iterations = 5
$delay = 200 # milliseconds between requests

# -----------------------
# Helper function: POST request with try/catch
# -----------------------
function Safe-Post($url, $payload) {
    try {
        Invoke-RestMethod -Uri $url -Method POST -Headers @{ "Content-Type" = "application/json" } -Body $payload
    } catch {
        Write-Host "Request failed (expected for some payloads): $payload"
    }
}

# -----------------------
# 1. API Gateway GET /next
# -----------------------
Write-Host "`nGenerating GET /next traces..."
for ($i=0; $i -lt $iterations; $i++) {
    Invoke-RestMethod -Uri http://localhost:5000/next -Method GET
    Start-Sleep -Milliseconds $delay
}

# -----------------------
# 2. Auth Service POST /login
# -----------------------
Write-Host "`nGenerating POST /login traces..."
$authPayloads = @(
    '{"username":"invalid1","password":"wrong"}',   # failed login
    '{"username":"invalid2","password":"1234"}',   # failed login
    '{"username":"user1","password":"pass1"}'      # simulate success if user exists
)
foreach ($payload in $authPayloads) {
    for ($i=0; $i -lt $iterations; $i++) {
        Safe-Post "http://localhost:5001/login" $payload
        Start-Sleep -Milliseconds $delay
    }
}

# -----------------------
# 3. Transaction Service POST /transfer
# -----------------------
Write-Host "`nGenerating POST /transfer traces..."
$transactionPayloads = @(
    '{"from_account":"A1","to_account":"A2","amount":50}',    # normal
    '{"from_account":"A2","to_account":"A3","amount":200}',   # normal
    '{"from_account":"A3","to_account":"A1","amount":10000}'  # anomaly: large transfer
)
foreach ($payload in $transactionPayloads) {
    for ($i=0; $i -lt $iterations; $i++) {
        Safe-Post "http://localhost:5003/transfer" $payload
        Start-Sleep -Milliseconds $delay
    }
}

# -----------------------
# 4. Payment Service POST /pay
# -----------------------
Write-Host "`nGenerating POST /pay traces..."
$paymentPayloads = @(
    '{"account":"A1","amount":100}',       # normal
    '{"account":"A2","amount":5000}'       # anomaly: large payment
)
foreach ($payload in $paymentPayloads) {
    for ($i=0; $i -lt $iterations; $i++) {
        Safe-Post "http://localhost:5000/pay" $payload
        Start-Sleep -Milliseconds $delay
    }
}

# -----------------------
# 5. Notification Service POST /notify
# -----------------------
Write-Host "`nGenerating POST /notify traces..."
$notificationPayloads = @(
    '{"user":"U1","message":"Hello!"}',
    '{"user":"U2","message":"Payment received."}',
    '{"user":"U3","message":"' + ("A"*500) + '"}'  # anomaly: very large message
)
foreach ($payload in $notificationPayloads) {
    for ($i=0; $i -lt $iterations; $i++) {
        Safe-Post "http://localhost:5005/notify" $payload
        Start-Sleep -Milliseconds $delay
    }
}

Write-Host "`n✅ Trace generation completed! Check Jaeger UI at http://localhost:16686"
