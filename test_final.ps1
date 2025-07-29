# Final test with better error handling
$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer hackrx_secret_token_2024"
}

$body = @{
    documents = "https://nationalinsurance.nic.co.in/sites/default/files/2025-06/NPMPP%20Policy%20Wordings.pdf"
    questions = @("What are the main policies in this document?")
} | ConvertTo-Json

Write-Host "Testing API endpoint..." -ForegroundColor Yellow
Write-Host "URL: https://ironwill-hackrx.vercel.app/hackrx/run" -ForegroundColor Cyan
Write-Host "Document: National Insurance PDF" -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "https://ironwill-hackrx.vercel.app/hackrx/run" -Method POST -Headers $headers -Body $body
    Write-Host "SUCCESS! Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        Write-Host "Response Content: $($_.Exception.Response.Content)" -ForegroundColor Red
    }
} 