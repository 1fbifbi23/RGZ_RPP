import psycopg2
import requests
from aiogram import Dispatcher, Bot, Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from db import conn, cursor, router

class Registration(StatesGroup):
    waiting_for_login = State()

@router.message(Command("reg"))
async def reg(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    cursor.execute("SELECT * FROM users WHERE users_id = %s", (user_id,))
    user = cursor.fetchone()

    if user:
        await message.answer('Вы уже зарегистрированы!')
        return

    await message.answer('Введите логин:')
    await state.set_state(Registration.waiting_for_login)

@router.message(Registration.waiting_for_login)
async def process_login(message: Message, state: FSMContext):
    login = message.text
    user_id = message.from_user.id

    try:
        # Сохраняем логин и user_id в таблицу users
        cursor.execute("INSERT INTO users (users_id, login) VALUES (%s, %s)", (user_id, login))
        conn.commit()
        await message.answer('Вы успешно зарегистрированы!')
    except psycopg2.errors.UniqueViolation:
        await message.answer('Этот логин уже занят. Попробуйте другой.')
    finally:
        await state.clear()