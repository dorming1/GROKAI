#!/usr/bin/env bash
# Установка Джарвиса на Linux / macOS
set -e
cd "$(dirname "$0")"

echo "=== Установка Джарвиса ==="

if [ "$(uname)" = "Darwin" ]; then
    command -v brew >/dev/null && brew list portaudio >/dev/null 2>&1 || brew install portaudio
else
    if command -v apt-get >/dev/null; then
        sudo apt-get install -y portaudio19-dev espeak-ng python3-dev
    fi
fi

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo
echo "=== Готово! Запуск: python3 jarvis.py ==="
