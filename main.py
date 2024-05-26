import asyncio
import logging
import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeDefault
from aiogram import Dispatcher, Bot, Router, types, F

from register import Registration
from add_operation import AddOperation
from operations import ViewOperations
from db import conn, cursor, router
from categories import AddCategory

async def main():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    bot = Bot(token=bot_token)

    dp = Dispatcher()

    await bot.set_my_commands([
        BotCommand(command='reg', description='Регистрация'),
        BotCommand(command='add_category', description='Добавить категорию'),
        BotCommand(command='add_operation', description='Добавить операцию'),
        BotCommand(command='operations', description='Просмотреть опериции')
    ], scope=BotCommandScopeDefault())

    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

cursor.close()
conn.close()
