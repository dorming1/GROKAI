# -*- coding: utf-8 -*-
"""Джарвис — голосовой ассистент для ПК.

Запуск:
    python jarvis.py            # голосовой режим (нужен микрофон)
    python jarvis.py --text     # текстовый режим (ввод с клавиатуры)
    python jarvis.py --no-wake  # реагировать на любую фразу без слова «Джарвис»
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

DEPS_MARKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".deps_ok")


def ensure_dependencies():
    """При первом запуске сам ставит недостающие пакеты (pip install)."""
    if os.path.exists(DEPS_MARKER):
        return
    missing = []
    for module, package in [("speech_recognition", "SpeechRecognition"),
                            ("pyaudio", "PyAudio"),
                            ("pyttsx3", "pyttsx3"),
                            ("anthropic", "anthropic")]:
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    if missing:
        print(f"Первый запуск: устанавливаю {', '.join(missing)} — подождите…")
        subprocess.call([sys.executable, "-m", "pip", "install", *missing])
    # помечаем, что попытка была, чтобы не повторять её при каждом старте
    with open(DEPS_MARKER, "w") as marker:
        marker.write("ok")


ensure_dependencies()

from brain import Brain
from commands import handle
from voice import Voice

WAKE_WORD = re.compile(
    r"^(привет|привіт|здравствуй|хей|эй|окей|ок|hey|ok)?[,!\s]*(джарвис|джарвіс|jarvis)[,!.\s]*",
    re.IGNORECASE)
EXIT_WORDS = re.compile(r"^(выход|выйди|стоп|пока|отключись|хватит)\b", re.IGNORECASE)


def main():
    parser = argparse.ArgumentParser(description="Джарвис — голосовой ассистент для ПК")
    parser.add_argument("--text", action="store_true",
                        help="текстовый режим без микрофона и озвучки")
    parser.add_argument("--no-wake", action="store_true",
                        help="не требовать слово «Джарвис» перед командой")
    args = parser.parse_args()

    voice = Voice(voice_enabled=not args.text)
    brain = Brain()

    def confirm(question: str) -> bool:
        voice.speak(question)
        answer = voice.listen() or ""
        return bool(re.search(r"\b(да|подтверждаю|конечно)\b", answer.lower()))

    voice.speak("Джарвис на связи, сэр. Чем могу помочь?")
    if voice.has_microphone and not args.no_wake:
        print("Подсказка: начинайте фразу со слова «Джарвис». Для выхода скажите «выход».")

    while True:
        phrase = voice.listen()
        if not phrase:
            continue

        # в голосовом режиме ждём обращения «Джарвис …», в текстовом — нет
        if voice.has_microphone and not args.no_wake:
            match = WAKE_WORD.match(phrase)
            if not match:
                continue
            phrase = phrase[match.end():].strip()
            if not phrase:
                voice.speak("Слушаю, сэр.")
                phrase = voice.listen() or ""
                if not phrase:
                    continue

        if EXIT_WORDS.match(phrase.strip()):
            voice.speak("До встречи!")
            break

        response = handle(phrase, voice.speak, confirm)
        if response is None:
            response = brain.ask(phrase)
        voice.speak(response)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПока!")
        sys.exit(0)
