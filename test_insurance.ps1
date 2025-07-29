# Test with National Insurance document
$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer hackrx_secret_token_2024"
}

$body = @{
    documents = "https://nationalinsurance.nic.co.in/sites/default/files/2025-06/NPMPP%20Policy%20Wordings.pdf"
    questions = @("What are the main policies in this document?", "What are the key requirements?")
} | ConvertTo-Json

Write-Host "Testing with National Insurance document..."
try {
    $response = Invoke-WebRequest -Uri "https://ironwill-hackrx.vercel.app/hackrx/run" -Method POST -Headers $headers -Body $body
    Write-Host "SUCCESS! Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "Response Content: $($_.Exception.Response.Content)" -ForegroundColor Red
} 