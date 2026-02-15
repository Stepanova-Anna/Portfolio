# Использование шаблона «Наблюдатель»

### Приложение реализует паттерн "Наблюдатель" для отслеживания курсов валют в реальном времени

**Сервер (Subject)**

- Отслеживает изменения курсов валют
- Управляет списком наблюдателей
- Уведомляет наблюдателей об изменениях
- Хранит текущие данные о курсах

**Сервис данных**

- Получает курсы валют с API ЦБ РФ 
- Парсит JSON-ответ от API
- Поддерживает основные валюты: USD, EUR, GBP, CNY, JPY, RUB
- Автоматически обновляет данные через заданные интервалы

**Клиенты (Observers)**

- Получают уведомления от субъекта
- Отправляют данные клиентам через WebSocket
- Каждому наблюдателю присваивается уникальный ID
- Отображают информацию на HTML-страницах

**Веб-сервер - Tornado**

- Обрабатывает HTTP запросы
- Поддерживает WebSocket соединения
- Обслуживает HTML-страницы
- Запускается на порту 8888

  
![Лабораторная работа 6](https://github.com/Stepanova-Anna/Programming-3/blob/main/LR6-5sem/1.png)

![Лабораторная работа 6](https://github.com/Stepanova-Anna/Programming-3/blob/main/LR6-5sem/2.png)

Паттерн "Наблюдатель"
- CurrencySubject - управляет наблюдателями и уведомляет их
  ```
  class CurrencySubject:
    def __init__(self) -> None:
        self._observers: List[Observer] = []
        self._currency_data: Dict[str, float] = {}
    
    def attach(self, observer: Observer) -> None: ...
    def detach(self, observer: Observer) -> None: ...
    async def notify(self) -> None: ...
  ```
- WebSocketObserver - отправляет данные через WebSocket
  ```
  class WebSocketObserver:
    def __init__(self, websocket) -> None:
        self.websocket = websocket
        self.observer_id = str(uuid.uuid4())[:8]
    
    async def update(self, currency_data: Dict[str, Any]) -> None:
        # Отправка данных через WebSocket
  ```
- Поддерживается множественное подключение наблюдателей

WebSocket коммуникация
- Real-time обновления без перезагрузки страницы
- Автоматическое переподключение при разрыве связи
- JSON формат сообщений для структурированных данных
