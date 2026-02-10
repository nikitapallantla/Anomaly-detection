$iterations = 1500  # Set this to 1500 to get the full count
Write-Host "🚀 Generating FULL CHAIN Traces (Gateway -> Database)..." -ForegroundColor Cyan

for ($i=1; $i -le $iterations; $i++) {
    try {
        # We ONLY hit port 5000. It triggers the rest!
        $null = Invoke-RestMethod -Uri "http://127.0.0.1:5000/process" -Method GET -TimeoutSec 60
        
        if ($i % 10 -eq 0) {
            Write-Host "✅ Progress: $i / $iterations traces completed." -ForegroundColor Green
        }
    }
    catch {
        Write-Host "⚠️ Trace $i timed out, but it's likely still processing in the background." -ForegroundColor Yellow
    }
}

Write-Host "`n✅ Done! Check Jaeger: http://localhost:16686" -ForegroundColor Green