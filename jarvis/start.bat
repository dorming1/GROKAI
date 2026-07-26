@echo off
chcp 65001 >nul
title Джарвис
cd /d "%~dp0"
python jarvis.py
echo.
pause
