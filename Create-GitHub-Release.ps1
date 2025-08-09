# GitHub Release Creation Script
# This script helps create a GitHub release with the desktop binaries

param(
    [string]$GitHubToken = $env:GITHUB_TOKEN,
    [string]$RepoOwner = "Flopchamp",
    [string]$RepoName = "ENIGMA_APEX_PROFESSIONAL_ALGO_TRADER",
    [string]$TagName = "v1.0.0",
    [string]$ReleaseName = "Training Wheels Desktop v1.0.0 - Full Functionality"
)

# Release body content
$releaseBody = @"
# 🎯 Training Wheels for Prop Firm Traders - Desktop v1.0.0

## COMPLETE DESKTOP VERSION - FULL FUNCTIONALITY

This is the **full-featured desktop version** with ALL capabilities enabled for serious prop firm trading.

### ✅ What's Included:
- 🔔 **Desktop notifications** with audio alerts
- 🔌 **NinjaTrader 8 connectivity** (Socket + ATM)
- 📊 **Tradovate API integration** (REST + WebSocket)
- 👁️ **OCR signal reading** from any trading platform
- 🎵 **Priority-based audio alerts**
- 🚀 **Native desktop performance**
- ⚙️ **Complete customization** options

### 🆚 Desktop vs Cloud:
| Feature | Desktop v1.0.0 | Cloud Demo |
|---------|----------------|------------|
| Notifications | ✅ Full | ❌ Disabled |
| NinjaTrader | ✅ Full | ❌ Demo only |
| OCR Reading | ✅ Yes | ❌ No |
| Audio Alerts | ✅ Yes | ❌ Silent |
| Performance | 🚀 Native | 🐌 Limited |

## 📥 DOWNLOAD & INSTALL:

### Windows Users (Recommended):
1. Download **Training-Wheels-Desktop-v1.0.0-Windows.zip**
2. Extract to any folder
3. Double-click **LAUNCH_TRAINING_WHEELS_DESKTOP.bat**
4. Wait for automatic installation
5. Browser opens at http://localhost:8502

### Mac/Linux Users:
1. Download **Training-Wheels-Desktop-v1.0.0-MacOS-Linux.zip**
2. Extract to any folder
3. Run: `chmod +x launch_training_wheels_desktop.sh`
4. Execute: `./launch_training_wheels_desktop.sh`

### All Platforms:
Download **Training-Wheels-Complete-v1.0.0-All-Platforms.zip** for everything.

## ⚡ System Requirements:
- Python 3.8+
- Windows 10+, macOS 10.14+, or Linux
- 8GB RAM minimum

## 🎯 Quick Verification:
After install, you should see:
- Browser opens to http://localhost:8502
- "🖥️ DESKTOP VERSION LOADED" banner
- Desktop notification test works
- NinjaTrader connection options
- Full trading interface enabled

**🚀 Happy Trading with Full Desktop Power!**

## 🔗 Cloud Demo (Limited Features):
Try the cloud version: https://enigma-apex-professional-algo-trader.onrender.com
"@

Write-Host "=========================================" -ForegroundColor Green
Write-Host " GITHUB RELEASE CREATOR" -ForegroundColor Green  
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Check if GitHub token is provided
if (-not $GitHubToken) {
    Write-Host "⚠️  GitHub token not found!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To create the release automatically, you need a GitHub token:" -ForegroundColor White
    Write-Host "1. Go to: https://github.com/settings/tokens" -ForegroundColor Cyan
    Write-Host "2. Click 'Generate new token (classic)'" -ForegroundColor Cyan
    Write-Host "3. Select scopes: repo, write:packages" -ForegroundColor Cyan
    Write-Host "4. Set environment variable: `$env:GITHUB_TOKEN = 'your_token_here'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 MANUAL RELEASE INSTRUCTIONS:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://github.com/$RepoOwner/$RepoName/releases" -ForegroundColor White
    Write-Host "2. Click 'Create a new release'" -ForegroundColor White
    Write-Host "3. Tag: $TagName" -ForegroundColor White
    Write-Host "4. Title: $ReleaseName" -ForegroundColor White
    Write-Host "5. Upload files from release_assets folder:" -ForegroundColor White
    Get-ChildItem "release_assets\*.zip" | ForEach-Object {
        Write-Host "   - $($_.Name)" -ForegroundColor Cyan
    }
    Write-Host ""
    Read-Host "Press Enter to continue..."
    return
}

Write-Host "🚀 Creating GitHub release..." -ForegroundColor Green
Write-Host "Repository: $RepoOwner/$RepoName" -ForegroundColor White
Write-Host "Tag: $TagName" -ForegroundColor White
Write-Host "Title: $ReleaseName" -ForegroundColor White
Write-Host ""

try {
    # Create the release using GitHub API
    $headers = @{
        "Authorization" = "token $GitHubToken"
        "Accept" = "application/vnd.github.v3+json"
        "User-Agent" = "PowerShell-Release-Creator"
    }
    
    $releaseData = @{
        tag_name = $TagName
        target_commitish = "main"
        name = $ReleaseName
        body = $releaseBody
        draft = $false
        prerelease = $false
    } | ConvertTo-Json
    
    $apiUrl = "https://api.github.com/repos/$RepoOwner/$RepoName/releases"
    
    Write-Host "📡 Creating release via GitHub API..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Body $releaseData -Headers $headers
    
    Write-Host "✅ Release created successfully!" -ForegroundColor Green
    Write-Host "Release URL: $($response.html_url)" -ForegroundColor Cyan
    
    # Upload release assets
    $uploadUrl = $response.upload_url -replace "\{\?name,label\}", ""
    
    Write-Host ""
    Write-Host "📦 Uploading release assets..." -ForegroundColor Yellow
    
    $assetFiles = Get-ChildItem "release_assets\*.zip"
    foreach ($file in $assetFiles) {
        Write-Host "   Uploading: $($file.Name)" -ForegroundColor White
        
        $uploadHeaders = $headers.Clone()
        $uploadHeaders["Content-Type"] = "application/zip"
        
        $fileContent = [System.IO.File]::ReadAllBytes($file.FullName)
        $uploadUrlWithName = "$uploadUrl?name=$($file.Name)"
        
        try {
            $uploadResponse = Invoke-RestMethod -Uri $uploadUrlWithName -Method Post -Body $fileContent -Headers $uploadHeaders
            Write-Host "   ✅ $($file.Name) uploaded successfully" -ForegroundColor Green
        }
        catch {
            Write-Host "   ❌ Failed to upload $($file.Name): $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "🎉 GitHub Release Created Successfully!" -ForegroundColor Green
    Write-Host "🔗 Release URL: $($response.html_url)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Users can now:" -ForegroundColor White
    Write-Host "1. Go to the releases page" -ForegroundColor White
    Write-Host "2. Download the appropriate ZIP file" -ForegroundColor White  
    Write-Host "3. Extract and run the launcher" -ForegroundColor White
    Write-Host "4. Get full desktop functionality!" -ForegroundColor White
    
} catch {
    Write-Host "❌ Failed to create release: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 Please create the release manually:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://github.com/$RepoOwner/$RepoName/releases" -ForegroundColor Cyan
    Write-Host "2. Click 'Create a new release'" -ForegroundColor Cyan
    Write-Host "3. Use the tag: $TagName" -ForegroundColor Cyan
    Write-Host "4. Upload the ZIP files from release_assets folder" -ForegroundColor Cyan
}

Write-Host ""
Read-Host "Press Enter to exit..."
