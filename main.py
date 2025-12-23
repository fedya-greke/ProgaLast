import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import router

# Настройка логирования
logging.basicConfig(level=logging.INFO)


async def main():
    # Инициализируем бот и диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Подключаем router с обработчиками
    dp.include_router(router)

    # Запускаем поллинг (опрос серверов Telegram на наличие новых сообщений)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())