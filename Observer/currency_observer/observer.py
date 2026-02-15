from typing import List, Dict, Any, Protocol, Optional
import json
import uuid
from datetime import datetime


class Observer(Protocol):
    """Протокол для наблюдателей"""
    observer_id: str

    async def update(self, currency_data: Dict[str, Any]) -> None:
        """Метод для обновления данных у наблюдателя"""
        pass


class CurrencySubject:
    """Субъект, который отслеживает изменения курсов валют"""

    def __init__(self) -> None:
        self._observers: List[Observer] = []
        self._currency_data: Dict[str, float] = {}

    def attach(self, observer: Observer) -> None:
        """Добавить наблюдателя"""
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"Наблюдатель {observer.observer_id} подключен")

    def detach(self, observer: Observer) -> None:
        """Удалить наблюдателя"""
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"Наблюдатель {observer.observer_id} отключен")

    async def notify(self) -> None:
        """Уведомить всех наблюдателей об изменениях"""
        data = {
            'currencies': self._currency_data,
            'timestamp': self._get_current_timestamp()
        }

        for observer in self._observers:
            try:
                await observer.update(data)
            except Exception as e:
                print(f"Ошибка при уведомлении наблюдателя {observer.observer_id}: {e}")

    def set_currency_data(self, new_data: Dict[str, float]) -> None:
        """Установить новые данные о курсах валют"""
        self._currency_data = new_data

    def _get_current_timestamp(self) -> str:
        """Получить текущее время в строковом формате"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def observer_count(self) -> int:
        """Количество активных наблюдателей"""
        return len(self._observers)


class WebSocketObserver:
    """Наблюдатель, реализующий WebSocket соединение"""

    def __init__(self, websocket) -> None:
        self.websocket = websocket
        self.observer_id = str(uuid.uuid4())[:8]

    async def update(self, currency_data: Dict[str, Any]) -> None:
        """Отправить обновление через WebSocket"""
        try:
            message = {
                'type': 'currency_update',
                'data': currency_data,
                'observer_id': self.observer_id
            }
            await self.websocket.write_message(json.dumps(message))
        except Exception as e:
            print(f"Ошибка отправки сообщения наблюдателю {self.observer_id}: {e}")