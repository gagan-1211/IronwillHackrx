# Test API endpoints for HackRx 6.0 with Official Test Document
$baseUrl = "https://ironwill-hackrx.vercel.app"
$token = "hackrx_secret_token_2024"

# Official HackRx 6.0 Test Document
$officialDocument = "https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D"

Write-Host "=== Testing HackRx 6.0 API with Official Document ===" -ForegroundColor Green
Write-Host "Base URL: $baseUrl" -ForegroundColor Yellow
Write-Host "Token: $token" -ForegroundColor Yellow
Write-Host "Document: Arogya Sanjeevani Policy (Official HackRx Test Document)" -ForegroundColor Yellow
Write-Host ""

# Test 1: Root endpoint
Write-Host "1. Testing Root Endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/" -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Health endpoint
Write-Host "2. Testing Health Endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Main API endpoint with Official Document
Write-Host "3. Testing Main API Endpoint with Official HackRx Document..." -ForegroundColor Cyan
$body = @{
    documents = $officialDocument
    questions = @(
        "What are the main policies covered in this Arogya Sanjeevani Policy?",
        "What is the definition of Cashless Facility in this policy?",
        "What are the exclusions mentioned in this policy?"
    )
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $token"
}

try {
    Write-Host "Sending request to: $baseUrl/hackrx/run" -ForegroundColor Gray
    Write-Host "Document: $officialDocument" -ForegroundColor Gray
    Write-Host "Questions: $($body | ConvertFrom-Json | ConvertTo-Json -Depth 1)" -ForegroundColor Gray
    Write-Host ""
    
    $response = Invoke-WebRequest -Uri "$baseUrl/hackrx/run" -Method POST -Body $body -Headers $headers -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $errorResponse = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($errorResponse)
        $errorContent = $reader.ReadToEnd()
        Write-Host "Error Details: $errorContent" -ForegroundColor Red
    }
}
Write-Host ""

Write-Host "=== API Testing Complete ===" -ForegroundColor Green 