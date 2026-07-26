# Установка Джарвиса одной командой (Windows PowerShell):
#   irm https://raw.githubusercontent.com/dorming1/GROKAI/claude/jarvis-pc-assistant-ve6n1v/jarvis/setup.ps1 | iex

$ErrorActionPreference = "Stop"
Write-Host ""
Write-Host "=== Установка Джарвиса ===" -ForegroundColor Cyan

# 1. Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python не найден — устанавливаю через winget..."
    try {
        winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                    [Environment]::GetEnvironmentVariable("Path", "User")
        $python = Get-Command python -ErrorAction SilentlyContinue
    } catch {}
    if (-not $python) {
        Write-Host "Не получилось поставить Python автоматически." -ForegroundColor Yellow
        Write-Host "Установите его вручную (галочка 'Add Python to PATH'!) и запустите команду ещё раз."
        Start-Process "https://www.python.org/downloads/"
        return
    }
}

# 2. Скачиваем Джарвиса
$dest = Join-Path $env:USERPROFILE "Jarvis"
Write-Host "Скачиваю Джарвиса в $dest ..."
$zip = Join-Path $env:TEMP "jarvis.zip"
$tmp = Join-Path $env:TEMP "jarvis_unzip"
Invoke-WebRequest "https://codeload.github.com/dorming1/GROKAI/zip/refs/heads/claude/jarvis-pc-assistant-ve6n1v" -OutFile $zip
Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
Expand-Archive $zip -DestinationPath $tmp -Force
$src = Get-ChildItem $tmp -Directory | Select-Object -First 1
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item (Join-Path $src.FullName "jarvis\*") $dest -Recurse -Force
Remove-Item $zip, $tmp -Recurse -Force -ErrorAction SilentlyContinue

# 3. Библиотеки
Write-Host "Устанавливаю библиотеки (пара минут)..."
python -m pip install --upgrade pip --quiet
python -m pip install -r (Join-Path $dest "requirements.txt") --quiet

# 4. Ярлык на рабочем столе
$desktop = [Environment]::GetFolderPath("Desktop")
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut((Join-Path $desktop "Джарвис.lnk"))
$shortcut.TargetPath = (Join-Path $dest "start.bat")
$shortcut.WorkingDirectory = $dest
$shortcut.Save()

Write-Host ""
Write-Host "=== Готово! Ярлык «Джарвис» на рабочем столе. Запускаю... ===" -ForegroundColor Green
Start-Process (Join-Path $dest "start.bat")
