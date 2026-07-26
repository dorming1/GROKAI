# -*- coding: utf-8 -*-
"""Встроенные команды Джарвиса: управление компьютером без нейросети.

Каждый обработчик получает уже нормализованную (нижний регистр) фразу
и возвращает текст ответа, либо None — тогда фраза уходит в «мозг» (LLM).
"""

from __future__ import annotations

import datetime
import os
import platform
import random
import re
import subprocess
import threading
import webbrowser
from urllib.parse import quote_plus

SYSTEM = platform.system()  # Windows / Darwin / Linux

SITES = {
    "ютуб": "https://www.youtube.com",
    "youtube": "https://www.youtube.com",
    "гугл": "https://www.google.com",
    "google": "https://www.google.com",
    "почт": "https://mail.google.com",
    "телеграм": "https://web.telegram.org",
    "вконтакте": "https://vk.com",
    "github": "https://github.com",
    "гитхаб": "https://github.com",
}

APPS = {
    "калькулятор": {"Windows": "calc", "Darwin": "open -a Calculator", "Linux": "gnome-calculator"},
    "блокнот": {"Windows": "notepad", "Darwin": "open -a TextEdit", "Linux": "gedit"},
    "проводник": {"Windows": "explorer", "Darwin": "open .", "Linux": "xdg-open ."},
    "терминал": {"Windows": "start cmd", "Darwin": "open -a Terminal", "Linux": "x-terminal-emulator"},
}


def _run(command: str):
    subprocess.Popen(command, shell=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _cmd_time(text: str) -> str:
    now = datetime.datetime.now()
    return f"Сейчас {now.strftime('%H:%M')}."


def _cmd_date(text: str) -> str:
    months = ["января", "февраля", "марта", "апреля", "мая", "июня",
              "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    days = ["понедельник", "вторник", "среда", "четверг",
            "пятница", "суббота", "воскресенье"]
    now = datetime.datetime.now()
    return f"Сегодня {days[now.weekday()]}, {now.day} {months[now.month - 1]} {now.year} года."


def _cmd_open(text: str) -> str | None:
    for key, url in SITES.items():
        if key in text:
            webbrowser.open(url)
            return "Открываю."
    for key, per_os in APPS.items():
        if key in text:
            command = per_os.get(SYSTEM)
            if command is None:
                return "На этой системе я не знаю, как это открыть."
            _run(command)
            return "Открываю."
    if "браузер" in text:
        webbrowser.open("https://www.google.com")
        return "Открываю браузер."
    return None


def _cmd_search(text: str) -> str:
    query = re.sub(r"^.*?(найди|загугли|поищи)( в интернете| в гугле)?\s*", "", text).strip()
    if not query:
        return "Что именно найти?"
    webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
    return f"Ищу «{query}»."


def _cmd_screenshot(text: str) -> str:
    path = os.path.join(os.path.expanduser("~"),
                        datetime.datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png"))
    try:
        if SYSTEM == "Windows":
            import ctypes  # noqa: F401 — проверка, что мы действительно на Windows
            command = ("powershell -windowstyle hidden -command "
                       "\"Add-Type -AssemblyName System.Windows.Forms,System.Drawing; "
                       "$s=[Windows.Forms.Screen]::PrimaryScreen.Bounds; "
                       "$b=New-Object Drawing.Bitmap $s.Width,$s.Height; "
                       "$g=[Drawing.Graphics]::FromImage($b); "
                       "$g.CopyFromScreen($s.Location,[Drawing.Point]::Empty,$s.Size); "
                       f"$b.Save('{path}')\"")
        elif SYSTEM == "Darwin":
            command = f"screencapture '{path}'"
        else:
            command = f"import -window root '{path}' || gnome-screenshot -f '{path}'"
        subprocess.run(command, shell=True, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Скриншот сохранён: {path}"
    except Exception:
        return "Не получилось сделать скриншот."


def _cmd_timer(text: str, speak) -> str:
    match = re.search(r"(\d+)\s*(секунд\w*|минут\w*|час\w*)", text)
    if not match:
        return "Скажите, например: таймер на 5 минут."
    value = int(match.group(1))
    unit = match.group(2)
    seconds = value * {"с": 1, "м": 60, "ч": 3600}[unit[0]]

    def ring():
        speak(f"Таймер на {value} {unit} завершён!")

    threading.Timer(seconds, ring).start()
    return f"Таймер на {value} {unit} запущен."


def _cmd_shutdown(text: str, confirm) -> str:
    if not confirm("Точно выключить компьютер? Скажите «да» для подтверждения."):
        return "Отменяю."
    commands = {"Windows": "shutdown /s /t 5",
                "Darwin": "osascript -e 'tell app \"System Events\" to shut down'",
                "Linux": "systemctl poweroff"}
    _run(commands[SYSTEM])
    return "Выключаю компьютер. До встречи."


SMALL_TALK = [
    # (шаблон, варианты мгновенных ответов — как в фильме, без задержки на нейросеть)
    (r"^(привет|привіт|здравствуй|добрый (день|вечер)|доброе утро)\b",
     ["К вашим услугам, сэр.", "Приветствую, сэр. Все системы в норме.",
      "Здравствуйте, сэр. Рад вас слышать."]),
    (r"как (дела|ты|поживаешь|настроение)",
     ["Все системы функционируют штатно, сэр.",
      "Превосходно, сэр. Готов к работе.",
      "Лучше не бывает — особенно когда вы рядом, сэр."]),
    (r"(кто ты|ты кто|представься|как тебя зовут)",
     ["Я Джарвис, ваш персональный ассистент. Просто скажите, что нужно, сэр."]),
    (r"(спасибо|благодарю)",
     ["Всегда пожалуйста, сэр.", "Рад стараться, сэр.", "Не стоит благодарности, сэр."]),
    (r"(что ты умеешь|твои возможности|чем можешь помочь)",
     ["Могу открывать сайты и программы, искать в интернете, делать скриншоты, "
      "ставить таймеры, сообщать время и отвечать на любые вопросы, сэр."]),
    (r"ты (тут|здесь|на месте|меня слышишь)",
     ["Всегда на месте, сэр.", "Слышу вас отлично, сэр."]),
]


def _cmd_small_talk(text: str) -> str | None:
    for pattern, replies in SMALL_TALK:
        if re.search(pattern, text):
            return random.choice(replies)
    return None


def handle(text: str, speak, confirm) -> str | None:
    """Возвращает ответ на встроенную команду или None, если команда не распознана.

    speak(text) — озвучить фразу (нужно таймеру),
    confirm(question) -> bool — переспросить пользователя (нужно выключению).
    """
    t = text.lower().strip()

    small_talk = _cmd_small_talk(t)
    if small_talk is not None:
        return small_talk
    if re.search(r"котор\w+ час|сколько времени|время\b", t):
        return _cmd_time(t)
    if re.search(r"какое сегодня число|какая.*дата|сегодняшн\w+ дат", t):
        return _cmd_date(t)
    if re.search(r"\b(найди|загугли|поищи)\b", t):
        return _cmd_search(t)
    if re.search(r"\bскриншот\b|сними экран", t):
        return _cmd_screenshot(t)
    if re.search(r"\bтаймер\b|засеки", t):
        return _cmd_timer(t, speak)
    if re.search(r"выключи (компьютер|пк|комп)", t):
        return _cmd_shutdown(t, confirm)
    if re.search(r"\b(открой|запусти|включи)\b", t):
        return _cmd_open(t)
    return None
