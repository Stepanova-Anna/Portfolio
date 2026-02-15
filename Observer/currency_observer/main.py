import asyncio
import tornado
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.options import define, options
from typing import Dict, Any, Optional
import os
import json


from observer import CurrencySubject, WebSocketObserver
from currency_service import CurrencyService

define("port", default=8888, help="Порт для запуска сервера", type=int)
define("debug", default=True, help="Режим отладки", type=bool)


class MainHandler(RequestHandler):
    """Главная страница"""

    def get(self) -> None:

        with open('templates/index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        self.write(html_content)


class CurrencyWebSocketHandler(WebSocketHandler):
    """WebSocket обработчик для отслеживания курсов валют"""

    def initialize(self, currency_subject: CurrencySubject) -> None:
        self.currency_subject = currency_subject
        self.observer: Optional[WebSocketObserver] = None

    def open(self) -> None:
        """Вызывается при открытии WebSocket соединения"""
        print("Новое WebSocket соединение")
        self.observer = WebSocketObserver(self)
        self.currency_subject.attach(self.observer)


        welcome_msg = {
            'type': 'connection_established',
            'observer_id': self.observer.observer_id,
            'message': f'Вы подключены как наблюдатель {self.observer.observer_id}'
        }
        self.write_message(welcome_msg)

    def on_close(self) -> None:
        """Вызывается при закрытии соединения"""
        if self.observer:
            self.currency_subject.detach(self.observer)
            print(f"WebSocket соединение закрыто: {self.observer.observer_id}")

    def on_message(self, message: str) -> None:
        """Обработка входящих сообщений"""
        try:
            data = json.loads(message)
            print(f"Получено сообщение от {self.observer.observer_id}: {data}")
        except:
            print(f"Получено сообщение: {message}")


async def currency_updater(currency_subject: CurrencySubject, currency_service: CurrencyService) -> None:
    """Фоновая задача для обновления курсов валют"""
    print("Запуск фоновой задачи обновления курсов валют...")

    while True:
        try:

            new_rates = await currency_service.get_updated_rates()

            if new_rates:

                currency_subject.set_currency_data(new_rates)


                await currency_subject.notify()
            else:
                print("Не удалось получить курсы валют")


            await asyncio.sleep(currency_service.update_interval)

        except Exception as e:
            print(f"Ошибка в фоновой задаче: {e}")
            await asyncio.sleep(60)


def make_app() -> tornado.web.Application:
    """Создание приложения Tornado"""


    currency_subject = CurrencySubject()
    currency_service = CurrencyService(update_interval=30)


    asyncio.create_task(currency_updater(currency_subject, currency_service))

    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/ws", CurrencyWebSocketHandler, {"currency_subject": currency_subject}),
        ],
        debug=options.debug,
    )


async def main() -> None:
    """Основная функция"""
    tornado.options.parse_command_line()

    app = make_app()
    app.listen(options.port)

    print(f"Сервер запущен на http://localhost:{options.port}")
    print("Подключитесь к странице для отслеживания курсов валют")
    print(f"Интервал обновления: 30 секунд")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())