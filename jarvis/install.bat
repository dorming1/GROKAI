@echo off
chcp 65001 >nul
title Установка Джарвиса
echo ============================================
echo   Установка Джарвиса — подождите немного
echo ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [!] Python не найден. Сейчас откроется сайт python.org —
    echo     установите Python и ОБЯЗАТЕЛЬНО отметьте "Add Python to PATH",
    echo     затем запустите install.bat ещё раз.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

python -m pip install --upgrade pip
python -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo.
    echo [!] Обычная установка не прошла, пробую запасной способ для PyAudio...
    python -m pip install SpeechRecognition pyttsx3 anthropic
    python -m pip install pipwin
    python -m pipwin install pyaudio
)

echo.
echo ============================================
echo   Готово! Запускайте Джарвиса через start.bat
echo ============================================
pause
