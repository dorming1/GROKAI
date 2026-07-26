# -*- coding: utf-8 -*-
"""Голос Джарвиса: распознавание речи (микрофон) и озвучка ответов.

Все зависимости опциональны — без них модуль автоматически
переключается на текстовый режим (ввод с клавиатуры, вывод в консоль).
"""

from __future__ import annotations

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class Voice:
    def __init__(self, language: str = "ru-RU", voice_enabled: bool = True):
        self.language = language
        self.recognizer = None
        self.microphone = None
        self.tts = None

        if voice_enabled and sr is not None:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            except Exception as e:
                print(f"[!] Микрофон недоступен ({e}), перехожу в текстовый режим.")
                self.recognizer = None
                self.microphone = None

        if voice_enabled and pyttsx3 is not None:
            try:
                self.tts = pyttsx3.init()
                self._pick_russian_voice()
                self.tts.setProperty("rate", 180)
            except Exception as e:
                print(f"[!] Синтез речи недоступен ({e}), отвечаю текстом.")
                self.tts = None

    def _pick_russian_voice(self):
        lang_tag = self.language.split("-")[0].lower()
        for voice in self.tts.getProperty("voices"):
            haystack = (voice.id + " " + (voice.name or "")).lower()
            if lang_tag in haystack or "russian" in haystack or "irina" in haystack:
                self.tts.setProperty("voice", voice.id)
                return

    @property
    def has_microphone(self) -> bool:
        return self.microphone is not None

    def listen(self) -> str | None:
        """Возвращает распознанную фразу или None, если ничего не услышал."""
        if not self.has_microphone:
            try:
                return input("Вы: ").strip()
            except (EOFError, KeyboardInterrupt):
                return "выход"

        with self.microphone as source:
            print("… слушаю")
            try:
                audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=12)
            except sr.WaitTimeoutError:
                return None

        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            print(f"Вы: {text}")
            return text.strip()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"[!] Сервис распознавания недоступен: {e}")
            return None

    def speak(self, text: str):
        print(f"Джарвис: {text}")
        if self.tts is not None:
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except Exception as e:
                print(f"[!] Ошибка озвучки: {e}")
