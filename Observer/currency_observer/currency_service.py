import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json


class CurrencyService:
    """Сервис для получения курсов валют с API ЦБ РФ"""

    API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

    def __init__(self, update_interval: int = 300) -> None:
        self.update_interval = update_interval
        self.last_update: Optional[datetime] = None
        self.currencies: Dict[str, float] = {}

    async def fetch_currency_rates(self) -> Dict[str, float]:
        """Получить курсы валют с API"""
        try:
            async with aiohttp.ClientSession() as session:

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                async with session.get(self.API_URL, headers=headers, timeout=10) as response:
                    if response.status == 200:

                        data = await response.json(content_type=None)
                        return self._parse_currency_data(data)
                    else:
                        print(f"Ошибка API: {response.status}")
                        return {}
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return {}

    def _parse_currency_data(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Парсинг данных о валютах"""
        currencies = {}


        target_currencies = ['USD', 'EUR', 'GBP', 'CNY', 'JPY']

        if 'Valute' in data:
            for currency_code, currency_info in data['Valute'].items():
                if currency_code in target_currencies:
                    currencies[currency_code] = currency_info['Value']


        currencies['RUB'] = 1.0

        return currencies

    def should_update(self) -> bool:
        """Проверка, нужно ли обновлять данные"""
        if not self.last_update:
            return True

        time_since_update = datetime.now() - self.last_update
        return time_since_update.total_seconds() >= self.update_interval

    async def get_updated_rates(self) -> Dict[str, float]:
        """Получить обновленные курсы валют"""
        if self.should_update():
            new_rates = await self.fetch_currency_rates()
            if new_rates:
                self.currencies = new_rates
                self.last_update = datetime.now()
                print(f"Курсы обновлены: {datetime.now().strftime('%H:%M:%S')}")
                for currency, rate in self.currencies.items():
                    if currency != 'RUB':
                        print(f"  {currency}: {rate:.2f} RUB")
            else:
                print("Не удалось получить новые курсы валют")

        return self.currencies

    def set_update_interval(self, interval: int) -> None:
        """Установить интервал обновления (в секундах)"""
        self.update_interval = interval
        print(f"Интервал обновления установлен: {interval} секунд")