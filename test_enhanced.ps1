# Enhanced test script for HackRx 6.0 API
$baseUrl = "https://ironwill-hackrx.vercel.app"
$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer hackrx_secret_token_2024"
}

Write-Host "=== HackRx 6.0 Enhanced API Test Suite ===" -ForegroundColor Cyan
Write-Host "Base URL: $baseUrl" -ForegroundColor Yellow

# Test 1: Health Check
Write-Host "`n1. Testing Health Check..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET
    $healthData = $response.Content | ConvertFrom-Json
    Write-Host "✅ Health Check PASSED" -ForegroundColor Green
    Write-Host "   Status: $($healthData.status)" -ForegroundColor White
    Write-Host "   Version: $($healthData.version)" -ForegroundColor White
    Write-Host "   Cache Size: $($healthData.cache_size)" -ForegroundColor White
} catch {
    Write-Host "❌ Health Check FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Cache Stats
Write-Host "`n2. Testing Cache Stats..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/cache/stats" -Method GET -Headers $headers
    $cacheData = $response.Content | ConvertFrom-Json
    Write-Host "✅ Cache Stats PASSED" -ForegroundColor Green
    Write-Host "   Cache Size: $($cacheData.cache_size)" -ForegroundColor White
    Write-Host "   Cache TTL: $($cacheData.cache_ttl)s" -ForegroundColor White
} catch {
    Write-Host "❌ Cache Stats FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Main API with Insurance Document
Write-Host "`n3. Testing Main API with Insurance Document..." -ForegroundColor Green
$body = @{
    documents = "https://nationalinsurance.nic.co.in/sites/default/files/2025-06/NPMPP%20Policy%20Wordings.pdf"
    questions = @("What are the main policies in this document?", "What are the key requirements?")
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/hackrx/run" -Method POST -Headers $headers -Body $body
    $apiData = $response.Content | ConvertFrom-Json
    Write-Host "✅ Main API PASSED" -ForegroundColor Green
    Write-Host "   Status Code: $($response.StatusCode)" -ForegroundColor White
    Write-Host "   Number of Answers: $($apiData.answers.Count)" -ForegroundColor White
    Write-Host "   Processing Time: $($apiData.metadata.processing_time)s" -ForegroundColor White
    Write-Host "   Cache Hit: $($apiData.metadata.cache_hit)" -ForegroundColor White
    
    # Display first answer
    if ($apiData.answers.Count -gt 0) {
        Write-Host "   First Answer Preview: $($apiData.answers[0].Substring(0, [Math]::Min(100, $apiData.answers[0].Length)))..." -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Main API FAILED: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "   Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        Write-Host "   Response: $($_.Exception.Response.Content)" -ForegroundColor Red
    }
}

# Test 4: Test with Text Document
Write-Host "`n4. Testing with Text Document..." -ForegroundColor Green
$textBody = @{
    documents = "https://raw.githubusercontent.com/microsoft/vscode/main/README.md"
    questions = @("What is this document about?", "What are the main features?")
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/hackrx/run" -Method POST -Headers $headers -Body $textBody
    $textData = $response.Content | ConvertFrom-Json
    Write-Host "✅ Text Document Test PASSED" -ForegroundColor Green
    Write-Host "   Status Code: $($response.StatusCode)" -ForegroundColor White
    Write-Host "   Number of Answers: $($textData.answers.Count)" -ForegroundColor White
} catch {
    Write-Host "❌ Text Document Test FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Error Handling - Invalid URL
Write-Host "`n5. Testing Error Handling (Invalid URL)..." -ForegroundColor Green
$invalidBody = @{
    documents = "https://invalid-url-that-does-not-exist.com/document.pdf"
    questions = @("What is this about?")
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/hackrx/run" -Method POST -Headers $headers -Body $invalidBody
    Write-Host "❌ Should have failed but didn't" -ForegroundColor Red
} catch {
    Write-Host "✅ Error Handling PASSED (expected failure)" -ForegroundColor Green
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
}

# Test 6: Error Handling - Invalid Token
Write-Host "`n6. Testing Error Handling (Invalid Token)..." -ForegroundColor Green
$invalidHeaders = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer invalid_token"
}

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/hackrx/run" -Method POST -Headers $invalidHeaders -Body $body
    Write-Host "❌ Should have failed but didn't" -ForegroundColor Red
} catch {
    Write-Host "✅ Invalid Token Handling PASSED (expected failure)" -ForegroundColor Green
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
}

# Test 7: Cache Test - Same Request
Write-Host "`n7. Testing Cache Functionality..." -ForegroundColor Green
try {
    # First request
    $response1 = Invoke-WebRequest -Uri "$baseUrl/hackrx/run" -Method POST -Headers $headers -Body $body
    $data1 = $response1.Content | ConvertFrom-Json
    $time1 = $data1.metadata.processing_time
    
    # Second request (should be cached)
    $response2 = Invoke-WebRequest -Uri "$baseUrl/hackrx/run" -Method POST -Headers $headers -Body $body
    $data2 = $response2.Content | ConvertFrom-Json
    $time2 = $data2.metadata.processing_time
    
    Write-Host "✅ Cache Test PASSED" -ForegroundColor Green
    Write-Host "   First Request Time: $time1 seconds" -ForegroundColor White
    Write-Host "   Second Request Time: $time2 seconds" -ForegroundColor White
    Write-Host "   Cache Hit: $($data2.metadata.cache_hit)" -ForegroundColor White
} catch {
    Write-Host "❌ Cache Test FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 8: Clear Cache
Write-Host "`n8. Testing Cache Clear..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/cache/clear" -Method DELETE -Headers $headers
    $clearData = $response.Content | ConvertFrom-Json
    Write-Host "✅ Cache Clear PASSED" -ForegroundColor Green
    Write-Host "   Message: $($clearData.message)" -ForegroundColor White
} catch {
    Write-Host "❌ Cache Clear FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Test Suite Complete ===" -ForegroundColor Cyan
Write-Host "Check the results above for any failures." -ForegroundColor Yellow 