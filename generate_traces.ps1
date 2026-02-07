# ==========================================
# Corrected High-Speed Trace Generator 
# ==========================================

$ProgressPreference = 'SilentlyContinue'
$iterations = 150 
$delay = 0 

Write-Host "🚀 Generating Traces for Professor's Procedure..." -ForegroundColor Cyan

# 1. API Gateway (Port 5000)
Write-Host "Targeting Gateway on /process..."
for ($i=0; $i -lt $iterations; $i++) {
    $null = Invoke-RestMethod -Uri "http://127.0.0.1:5000/process" -Method GET -ErrorAction SilentlyContinue
}

# 2. Auth Service (Port 5001)
Write-Host "Targeting Auth Service on /process..."
for ($i=0; $i -lt $iterations; $i++) {
    $null = Invoke-RestMethod -Uri "http://127.0.0.1:5001/process" -Method GET -ErrorAction SilentlyContinue
}

# 3. Transaction Service (Port 5003)
Write-Host "Targeting Transaction Service on /process..."
for ($i=0; $i -lt $iterations; $i++) {
    $null = Invoke-RestMethod -Uri "http://127.0.0.1:5003/process" -Method GET -ErrorAction SilentlyContinue
}

# 4. Payment Service (Port 5004)
Write-Host "Targeting Payment Service on /process..."
for ($i=0; $i -lt $iterations; $i++) {
    $null = Invoke-RestMethod -Uri "http://127.0.0.1:5004/process" -Method GET -ErrorAction SilentlyContinue
}

# 5. Notification Service (Port 5005)
Write-Host "Targeting Notification Service on /process..."
for ($i=0; $i -lt $iterations; $i++) {
    $null = Invoke-RestMethod -Uri "http://127.0.0.1:5005/process" -Method GET -ErrorAction SilentlyContinue
}

Write-Host "`n✅ Done! Check Jaeger: http://localhost:16686" -ForegroundColor Green