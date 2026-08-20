$ErrorActionPreference = "Continue"
$repo = "yigenfeng0707-netizen/yiwu-global-ai-agent"
$apiBase = "repos/$repo/git"

# Get current main branch head
$refResponse = gh api "$apiBase/refs/heads/main" --jq ".object.sha" 2>&1
$parentSha = $refResponse.Trim()
Write-Host "Current main SHA: $parentSha"

# Get current tree SHA from the parent commit
$commitResponse = gh api "$apiBase/commits/$parentSha" --jq ".tree.sha" 2>&1
$baseTreeSha = $commitResponse.Trim()
Write-Host "Base tree SHA: $baseTreeSha"

# Get all tracked files (exclude README.md already uploaded)
$files = git ls-files | Where-Object { $_ -ne "README.md" }
Write-Host "Files to upload: $($files.Count)"

# Step 1: Create blobs for all files
$blobShas = @{}
$fileIndex = 0
$totalFiles = $files.Count

foreach ($file in $files) {
    $fileIndex++
    Write-Host "[$fileIndex/$totalFiles] Creating blob for: $file"

    $filePath = Join-Path $PSScriptRoot $file
    if (-not (Test-Path $filePath)) {
        Write-Host "  SKIP: File not found: $filePath"
        continue
    }

    $fileInfo = Get-Item $filePath
    if ($fileInfo.Length -gt 50MB) {
        Write-Host "  SKIP: File too large ($($fileInfo.Length) bytes)"
        continue
    }

    $bytes = [System.IO.File]::ReadAllBytes($filePath)
    $base64 = [Convert]::ToBase64String($bytes)

    $bodyObj = @{
        content = $base64
        encoding = "base64"
    }
    $bodyJson = $bodyObj | ConvertTo-Json -Compress

    $tempFile = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($tempFile, $bodyJson, [System.Text.Encoding]::UTF8)

    try {
        $response = gh api "$apiBase/blobs" --method POST --input $tempFile 2>&1
        $json = $response | ConvertFrom-Json
        $blobShas[$file] = $json.sha
        Write-Host "  OK: $($json.sha)"
    } catch {
        Write-Host "  ERROR: $_"
    } finally {
        Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "`nBlobs created: $($blobShas.Count)"

if ($blobShas.Count -eq 0) {
    Write-Host "No blobs created, aborting."
    exit 1
}

# Step 2: Create tree (with base_tree to inherit README.md)
Write-Host "`nCreating tree..."
$treeItems = @()
foreach ($file in $blobShas.Keys) {
    $treeItems += @{
        path = $file
        mode = "100644"
        type = "blob"
        sha = $blobShas[$file]
    }
}

$treeBodyObj = @{
    base_tree = $baseTreeSha
    tree = $treeItems
}
$treeBodyJson = $treeBodyObj | ConvertTo-Json -Depth 10

$tempFile = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($tempFile, $treeBodyJson, [System.Text.Encoding]::UTF8)

Write-Host "Creating tree with $($treeItems.Count) items..."
$treeResponse = gh api "$apiBase/trees" --method POST --input $tempFile 2>&1
Remove-Item $tempFile -Force -ErrorAction SilentlyContinue

$treeJson = $treeResponse | ConvertFrom-Json
$treeSha = $treeJson.sha
Write-Host "Tree SHA: $treeSha"

# Step 3: Create commit with parent
Write-Host "`nCreating commit..."
$commitBodyObj = @{
    message = "feat: 义乌小商品出海智能体-OPC V2.0冠军版 - 7大AI Agent全链路 - 义乌发展经验国家战略 - 39城1039模式复制推广 - OPC模式1人+7Agent - DashScope LLM集成 - GitHub Actions CI/CD"
    tree = $treeSha
    parents = @($parentSha)
}
$commitBodyJson = $commitBodyObj | ConvertTo-Json -Depth 5

$tempFile = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($tempFile, $commitBodyJson, [System.Text.Encoding]::UTF8)

$commitResponse = gh api "$apiBase/commits" --method POST --input $tempFile 2>&1
Remove-Item $tempFile -Force -ErrorAction SilentlyContinue

$commitJson = $commitResponse | ConvertFrom-Json
$commitSha = $commitJson.sha
Write-Host "Commit SHA: $commitSha"

# Step 4: Update main branch ref
Write-Host "`nUpdating main branch ref..."
$refBodyObj = @{
    sha = $commitSha
    force = $true
}
$refBodyJson = $refBodyObj | ConvertTo-Json -Compress

$tempFile = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($tempFile, $refBodyJson, [System.Text.Encoding]::UTF8)

$refResponse = gh api "$apiBase/refs/heads/main" --method PATCH --input $tempFile 2>&1
Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
Write-Host "Ref update response (first 300 chars): $($refResponse.Substring(0, [Math]::Min(300, $refResponse.Length)))"

Write-Host "`n=== PUSH COMPLETE ==="
