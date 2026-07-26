# -*- coding: utf-8 -*-
"""«Мозг» Джарвиса: свободные вопросы уходят в Claude API.

Нужен ключ в переменной окружения ANTHROPIC_API_KEY и пакет `anthropic`.
Без ключа Джарвис работает только со встроенными командами.
"""

from __future__ import annotations

import os

SYSTEM_PROMPT = (
    "Ты — Джарвис, голосовой ассистент на компьютере пользователя, "
    "в духе Джарвиса из фильмов про Железного человека: вежливый, "
    "остроумный, невозмутимый, обращаешься к пользователю «сэр». "
    "Отвечай по-русски, кратко и по делу (1–3 предложения): "
    "ответ будет озвучен вслух. Без markdown, списков и кода, "
    "если пользователь прямо не попросил."
)


class Brain:
    def __init__(self, model: str = "claude-sonnet-5"):
        self.model = model
        self.client = None
        self.history: list[dict] = []

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            print("[!] Пакет anthropic не установлен: pip install anthropic")

    @property
    def available(self) -> bool:
        return self.client is not None

    def ask(self, question: str) -> str:
        if not self.available:
            return ("Эту команду я не знаю, а для свободных вопросов нужен ключ "
                    "ANTHROPIC_API_KEY. Подробности в README.")

        self.history.append({"role": "user", "content": question})
        # держим только последние 20 реплик, чтобы не раздувать контекст
        self.history = self.history[-20:]
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=400,
                system=SYSTEM_PROMPT,
                messages=self.history,
            )
            answer = response.content[0].text.strip()
            self.history.append({"role": "assistant", "content": answer})
            return answer
        except Exception as e:
            self.history.pop()
            return f"Не получилось спросить нейросеть: {e}"
