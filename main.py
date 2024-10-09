import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta
from aiopath import AsyncPath
from aiofile import AIOFile, Writer

# Клієнт для роботи з API ПриватБанку
class CurrencyAPIClient:
    def __init__(self):
        self.api_url = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

    async def get_exchange_rate(self, date: str):
        url = self.api_url + date
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to fetch data: {response.status}")
                    return await response.json()
        except Exception as e:
            print(f"Error occurred: {e}")
            return None

# Сервіс для обробки курсів валют
class CurrencyService:
    def __init__(self, client: CurrencyAPIClient):
        self.client = client

    async def get_rates(self, days: int, currencies: list):
        today = datetime.today()
        results = []
        for i in range(days):
            date = (today - timedelta(days=i)).strftime('%d.%m.%Y')
            data = await self.client.get_exchange_rate(date)
            if data:
                rates = {currency: self.extract_currency_data(data, currency) for currency in currencies}
                results.append({date: rates})
        return results

    def extract_currency_data(self, data, currency):
        for rate in data.get("exchangeRate", []):
            if rate.get("currency") == currency:
                return {
                    'sale': rate.get('saleRate', 'N/A'),
                    'purchase': rate.get('purchaseRate', 'N/A')
                }
        return {'sale': 'N/A', 'purchase': 'N/A'}

# Функція для логування команд
async def log_command(command):
    log_path = AsyncPath("exchange_log.txt")
    async with AIOFile(log_path, 'a') as afp:
        writer = Writer(afp)
        await writer(f"{datetime.now()}: Executed command: {command}\n")

# Основна функція для виконання програми
async def main():
    if len(sys.argv) < 2:
        print("Usage: main.py <number_of_days> [currencies...]")
        return

    # Отримання аргументів командного рядка
    days = int(sys.argv[1])
    if days > 10:
        print("You can only request rates for up to 10 days.")
        return

    currencies = sys.argv[2:] if len(sys.argv) > 2 else ['USD', 'EUR']

    # Ініціалізація клієнта та сервісу
    client = CurrencyAPIClient()
    service = CurrencyService(client)

    # Отримання та виведення курсів валют
    rates = await service.get_rates(days, currencies)
    print(rates)

    # Логування виконаної команди
    command = f"main.py {days} {' '.join(currencies)}"
    await log_command(command)

# Запуск програми
if __name__ == "__main__":
    asyncio.run(main())
