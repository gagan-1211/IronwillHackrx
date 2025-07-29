# Test with a simple JSON document (not PDF)
$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer hackrx_secret_token_2024"
}

$body = @{
    documents = "https://jsonplaceholder.typicode.com/posts/1"
    questions = @("What is this document about?")
} | ConvertTo-Json

Write-Host "Testing with simple JSON document..."
try {
    $response = Invoke-WebRequest -Uri "https://ironwill-hackrx.vercel.app/hackrx/run" -Method POST -Headers $headers -Body $body
    Write-Host "SUCCESS! Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
} 