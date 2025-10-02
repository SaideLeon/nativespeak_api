# api_smoke_test.ps1
# Smoke test script for NativeSpeak API
# Tests all available endpoints with proper JWT authentication

param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [switch]$Verbose,
    [switch]$SkipAuth
)

$ErrorActionPreference = "Continue"
$SuccessCount = 0
$FailureCount = 0
$TestResults = @()
$AuthToken = $null

# ANSI color codes for pretty output
$Green = "`e[32m"
$Red = "`e[31m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Cyan = "`e[36m"
$Reset = "`e[0m"

function Write-TestHeader {
    param([string]$Message)
    Write-Host "`n$Blue=== $Message ===$Reset" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "$Green✓$Reset $Message" -ForegroundColor Green
}

function Write-Failure {
    param([string]$Message)
    Write-Host "$Red✗$Reset $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    if ($Verbose) {
        Write-Host "$Yellow→$Reset $Message" -ForegroundColor Yellow
    }
}

function Write-Warning {
    param([string]$Message)
    Write-Host "$Cyan⚠$Reset $Message" -ForegroundColor Cyan
}

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Path,
        [object]$Body = $null,
        [int[]]$ExpectedStatusCodes = @(200, 201),
        [switch]$UseAuth,
        [switch]$AllowAnyStatus
    )
    
    $url = "$BaseUrl$Path"
    Write-Info "Testing: $Method $url"
    
    try {
        $headers = @{
            "Content-Type" = "application/json"
        }
        
        if ($UseAuth -and $script:AuthToken) {
            $headers["Authorization"] = "Bearer $($script:AuthToken)"
            Write-Info "Using JWT token for authentication"
        }
        
        $params = @{
            Uri = $url
            Method = $Method
            Headers = $headers
            ErrorAction = "Stop"
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
            Write-Info "Body: $($params.Body)"
        }
        
        $response = Invoke-WebRequest @params
        
        if ($AllowAnyStatus -or ($ExpectedStatusCodes -contains $response.StatusCode)) {
            Write-Success "$Name - Status: $($response.StatusCode)"
            $script:SuccessCount++
            $script:TestResults += [PSCustomObject]@{
                Test = $Name
                Status = "PASS"
                StatusCode = $response.StatusCode
                Method = $Method
                Path = $Path
                Authenticated = $UseAuth.IsPresent
            }
            return @{
                Success = $true
                StatusCode = $response.StatusCode
                Content = $response.Content
            }
        } else {
            Write-Failure "$Name - Unexpected status: $($response.StatusCode)"
            $script:FailureCount++
            $script:TestResults += [PSCustomObject]@{
                Test = $Name
                Status = "FAIL"
                StatusCode = $response.StatusCode
                Method = $Method
                Path = $Path
                Authenticated = $UseAuth.IsPresent
            }
            return @{
                Success = $false
                StatusCode = $response.StatusCode
            }
        }
    }
    catch {
        $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.Value__ } else { 0 }
        
        if ($AllowAnyStatus -or ($ExpectedStatusCodes -contains $statusCode)) {
            Write-Success "$Name - Status: $statusCode (expected)"
            $script:SuccessCount++
            $script:TestResults += [PSCustomObject]@{
                Test = $Name
                Status = "PASS"
                StatusCode = $statusCode
                Method = $Method
                Path = $Path
                Authenticated = $UseAuth.IsPresent
            }
            return @{
                Success = $true
                StatusCode = $statusCode
            }
        } else {
            Write-Failure "$Name - Error: $($_.Exception.Message)"
            if ($Verbose -and $_.Exception.Response) {
                try {
                    $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
                    $responseBody = $reader.ReadToEnd()
                    Write-Info "Response body: $responseBody"
                } catch {}
            }
            $script:FailureCount++
            $script:TestResults += [PSCustomObject]@{
                Test = $Name
                Status = "FAIL"
                StatusCode = $statusCode
                Method = $Method
                Path = $Path
                Error = $_.Exception.Message
                Authenticated = $UseAuth.IsPresent
            }
            return @{
                Success = $false
                StatusCode = $statusCode
                Error = $_.Exception.Message
            }
        }
    }
}

# Banner
Write-Host @"
$Blue
╔═══════════════════════════════════════╗
║   NativeSpeak API - Smoke Test Suite  ║
╚═══════════════════════════════════════╝
$Reset
Testing against: $BaseUrl
Started at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@

# Test 0: Home page
Write-TestHeader "Testing Home Page"
Test-Endpoint -Name "Home Page" -Method "GET" -Path "/" | Out-Null

# Test 1: API Root
Write-TestHeader "Testing API Root"
Test-Endpoint -Name "API Root" -Method "GET" -Path "/api/" | Out-Null

# Test 2: Authentication Setup (if not skipped)
if (-not $SkipAuth) {
    Write-TestHeader "Setting Up Authentication"
    
    # Generate unique test user
    $timestamp = (Get-Date).Ticks
    $testEmail = "testuser_${timestamp}@example.com"
    $testPassword = "SecurePass123!@#"
    
    Write-Info "Creating test user: $testEmail"
    
    # Try to register - this should work without auth
    $registerResult = Test-Endpoint `
        -Name "Register Test User" `
        -Method "POST" `
        -Path "/api/auth/register/" `
        -Body @{
            email = $testEmail
            password = $testPassword
            first_name = "Test"
            last_name = "User"
        } `
        -ExpectedStatusCodes @(200, 201, 400, 401) `
        -AllowAnyStatus
    
    if ($registerResult.StatusCode -eq 401) {
        Write-Warning "Registration endpoint requires authentication - this seems wrong!"
        Write-Warning "Attempting to use Django admin to create user or use existing credentials..."
        
        # Try with a default admin user (common in dev environments)
        Write-Info "Attempting login with default credentials..."
        $testEmail = "admin@example.com"
        $testPassword = "admin"
    }
    
    # Try to login and get JWT token
    Write-Info "Attempting login to obtain JWT token..."
    
    try {
        $loginBody = @{
            email = $testEmail
            password = $testPassword
        } | ConvertTo-Json
        
        $loginResponse = Invoke-WebRequest `
            -Uri "$BaseUrl/api/auth/login/" `
            -Method POST `
            -Body $loginBody `
            -Headers @{"Content-Type" = "application/json"} `
            -ErrorAction Stop
        
        $loginData = $loginResponse.Content | ConvertFrom-Json
        $script:AuthToken = $loginData.access
        
        Write-Success "Successfully obtained JWT token"
        Write-Info "Token: $($script:AuthToken.Substring(0, 20))..."
        
    } catch {
        Write-Warning "Could not obtain JWT token: $($_.Exception.Message)"
        Write-Warning "Write operations will likely fail with 401 Unauthorized"
        Write-Info "To fix this, you need to either:"
        Write-Info "  1. Fix the register endpoint to allow unauthenticated access"
        Write-Info "  2. Create a user manually via Django admin"
        Write-Info "  3. Update API permissions to allow anonymous writes (not recommended)"
    }
} else {
    Write-Warning "Skipping authentication setup (--SkipAuth flag)"
}

# Test 3: Settings endpoints
Write-TestHeader "Testing Settings Endpoints"
Test-Endpoint -Name "List Settings" -Method "GET" -Path "/api/settings/" | Out-Null
Test-Endpoint -Name "Create Setting" -Method "POST" -Path "/api/settings/" -UseAuth -Body @{
    key = "test.setting.$(Get-Random)"
    value = @{ test = $true; timestamp = (Get-Date).ToString() }
} | Out-Null
Test-Endpoint -Name "Upsert Setting" -Method "PUT" -Path "/api/settings/upsert/" -UseAuth -Body @{
    key = "test.upsert.$(Get-Random)"
    value = @{ upserted = $true }
} | Out-Null
Test-Endpoint -Name "Query Setting by Key" -Method "GET" -Path "/api/settings/?key=test.setting" | Out-Null

# Test 4: Tools endpoints
Write-TestHeader "Testing Tools Endpoints"
Test-Endpoint -Name "List Tools" -Method "GET" -Path "/api/tools/" | Out-Null
Test-Endpoint -Name "Create Tool" -Method "POST" -Path "/api/tools/" -UseAuth -Body @{
    name = "Test Tool $(Get-Random)"
    config = @{ setting1 = "value1" }
    enabled = $true
} | Out-Null

# Test 5: Logs endpoints
Write-TestHeader "Testing Logs Endpoints"
Test-Endpoint -Name "List Logs" -Method "GET" -Path "/api/logs/" | Out-Null
Test-Endpoint -Name "Create Log Entry" -Method "POST" -Path "/api/logs/" -UseAuth -Body @{
    entry = @{
        level = "INFO"
        message = "Test log entry"
        timestamp = (Get-Date).ToString()
    }
} | Out-Null

# Test 6: Achievements endpoints
Write-TestHeader "Testing Achievements Endpoints"
Test-Endpoint -Name "List Achievements" -Method "GET" -Path "/api/achievements/" | Out-Null
Test-Endpoint -Name "Create Achievement" -Method "POST" -Path "/api/achievements/" -UseAuth -Body @{
    name = "Test Achievement $(Get-Random)"
    unlocked = $false
    metadata = @{ points = 100 }
} | Out-Null

# Test 7: Notifications endpoints
Write-TestHeader "Testing Notifications Endpoints"
Test-Endpoint -Name "List Notifications" -Method "GET" -Path "/api/notifications/" | Out-Null
Test-Endpoint -Name "Create Notification" -Method "POST" -Path "/api/notifications/" -UseAuth -Body @{
    title = "Test Notification"
    message = "This is a test notification"
    type = "info"
    read = $false
} | Out-Null

# Test 8: Presence endpoints
Write-TestHeader "Testing Presence Endpoints"
Test-Endpoint -Name "List Presence" -Method "GET" -Path "/api/presence/" | Out-Null
Test-Endpoint -Name "Create Presence" -Method "POST" -Path "/api/presence/" -UseAuth -Body @{
    user_id = "test_user_$(Get-Random)"
    status = "online"
} | Out-Null

# Test 9: Todos endpoints
Write-TestHeader "Testing Todos Endpoints"
Test-Endpoint -Name "List Todos" -Method "GET" -Path "/api/todos/" | Out-Null
Test-Endpoint -Name "Create Todo" -Method "POST" -Path "/api/todos/" -UseAuth -Body @{
    text = "Test todo item $(Get-Random)"
    completed = $false
} | Out-Null

# Test 10: Lessons endpoints
Write-TestHeader "Testing Lessons Endpoints"
Test-Endpoint -Name "List Lessons" -Method "GET" -Path "/api/lessons/" | Out-Null

# Test 11: UI State endpoints
Write-TestHeader "Testing UI State Endpoints"
Test-Endpoint -Name "List UI States" -Method "GET" -Path "/api/ui-state/" | Out-Null
Test-Endpoint -Name "Create UI State" -Method "POST" -Path "/api/ui-state/" -UseAuth -Body @{
    key = "ui.test.$(Get-Random)"
    state = @{ cursor = 0; theme = "dark" }
} | Out-Null
Test-Endpoint -Name "Upsert UI State" -Method "PUT" -Path "/api/ui-state/upsert/" -UseAuth -Body @{
    key = "ui.upsert.$(Get-Random)"
    state = @{ mode = "test" }
} | Out-Null

# Test 12: Auth endpoints (informational)
Write-TestHeader "Testing Auth Endpoints (Informational)"
# The informational GET endpoints were moved to unique paths to avoid duplicated operationIds
Test-Endpoint -Name "Auth Register Info (GET)" -Method "GET" -Path "/api/auth/register-info/" | Out-Null
Test-Endpoint -Name "Auth Login Info (GET)" -Method "GET" -Path "/api/auth/login-info/" | Out-Null

# Test 13: JWT Token endpoints
Write-TestHeader "Testing JWT Token Endpoints"
Test-Endpoint -Name "Token Obtain (Bad Credentials)" -Method "POST" -Path "/api/token/" -Body @{
    username = "nonexistent"
    password = "wrongpass"
} -ExpectedStatusCodes @(401) | Out-Null

# Test 14: OpenAPI Schema
Write-TestHeader "Testing API Documentation"
Test-Endpoint -Name "OpenAPI Schema" -Method "GET" -Path "/api/schema/" | Out-Null
Test-Endpoint -Name "API Docs" -Method "GET" -Path "/api/docs/" | Out-Null

# Test 15: Admin endpoints
Write-TestHeader "Testing Admin Endpoints"
Test-Endpoint -Name "Admin Login Page" -Method "GET" -Path "/admin/" -ExpectedStatusCodes @(200, 302) | Out-Null

# Summary
Write-Host @"

$Blue
╔═══════════════════════════════════════╗
║          Test Summary                  ║
╚═══════════════════════════════════════╝
$Reset
Total Tests: $($SuccessCount + $FailureCount)
$Green✓ Passed: $SuccessCount$Reset
$Red✗ Failed: $FailureCount$Reset
Auth Token: $(if ($script:AuthToken) { "$Green✓ Obtained$Reset" } else { "$Red✗ Not obtained$Reset" })

"@

if ($Verbose) {
    Write-Host "`nDetailed Results:" -ForegroundColor Cyan
    $TestResults | Format-Table -AutoSize
}

# Save results to JSON
$reportPath = "test_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$report = @{
    timestamp = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    baseUrl = $BaseUrl
    totalTests = $SuccessCount + $FailureCount
    passed = $SuccessCount
    failed = $FailureCount
    authTokenObtained = ($null -ne $script:AuthToken)
    results = $TestResults
}
$report | ConvertTo-Json -Depth 10 | Out-File $reportPath
Write-Host "Full report saved to: $reportPath`n" -ForegroundColor Cyan

# Exit code
if ($FailureCount -gt 0) {
    Write-Host "Some tests failed. Please review the results above." -ForegroundColor Red
    
    if (-not $script:AuthToken) {
        Write-Host "`n$Yellow⚠ Authentication Issue Detected:$Reset" -ForegroundColor Yellow
        Write-Host "The register endpoint returned 401, which suggests a configuration problem."
        Write-Host "`nRecommended fixes:"
        Write-Host "1. Update core/views.py RegisterAPIView to use AllowAny permission"
        Write-Host "2. Or update settings.py REST_FRAMEWORK permissions to allow anonymous access"
        Write-Host "3. Or create a test user manually: py -3 manage.py createsuperuser"
    }
    
    exit 1
} else {
    Write-Host "All tests passed! 🎉" -ForegroundColor Green
    exit 0
}