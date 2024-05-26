import psycopg2
import requests
from aiogram import Dispatcher, Bot, Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from db import conn, cursor, router

class ViewOperations(StatesGroup):
    waiting_for_currency = State()

@router.message(Command("operations"))
async def operations(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    cursor.execute("SELECT * FROM users WHERE users_id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        await message.answer('Вы не зарегистрированы! Для регистрации используйте команду /reg')
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="RUB"), KeyboardButton(text="EUR"), KeyboardButton(text="USD")],
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите валюту:", reply_markup=keyboard)
    await state.set_state(ViewOperations.waiting_for_currency)

@router.message(ViewOperations.waiting_for_currency)
async def process_currency(message: Message, state: FSMContext):
    currency = message.text.upper()

    if currency not in ("RUB", "EUR", "USD"):
        await message.answer("Пожалуйста, выберите валюту, используя кнопки.")
        return

    user_id = message.from_user.id
    cursor.execute("SELECT * FROM operations WHERE users_id = %s", (user_id,))
    operations = cursor.fetchall()

    if not operations:
        await message.answer("У вас пока нет операций.")
        return

    output = ""
    if currency == "RUB":
        for operation in operations:
            output += f"Дата: {operation[1]}, ID: {operation[0]}, Тип: {operation[4]}, Сумма: {operation[2]} RUB\n"
    else:
        try:
            response = requests.get(f"http://195.58.54.159:8000/rate?currency={currency}")
            response.raise_for_status()  # Проверяем на HTTP ошибки

            rate = response.json()["rate"]
            for operation in operations:
                # Преобразуем Decimal в float
                converted_amount = float(operation[2]) / rate
                output += f"Дата: {operation[1]},ID: {operation[0]}, Тип: {operation[4]}, Сумма: {converted_amount:.2f} {currency}\n"
        except requests.exceptions.RequestException as e:
            await message.answer(f"Ошибка при получении курса валют: {e}")
            await state.clear()
            return

    await message.answer(output)
    await state.clear()