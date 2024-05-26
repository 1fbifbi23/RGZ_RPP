import psycopg2
from aiogram import Dispatcher, Bot, Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from db import conn, cursor, router

class AddCategory(StatesGroup):
    waiting_for_category_name = State()

@router.message(Command("add_category"))
async def add_category(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    cursor.execute("SELECT * FROM users WHERE users_id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        await message.answer('Вы не зарегистрированы! Для регистрации используйте команду /reg')
        return

    await message.answer("Введите название категории:")
    await state.set_state(AddCategory.waiting_for_category_name)

@router.message(AddCategory.waiting_for_category_name)
async def process_category_name(message: Message, state: FSMContext):
    category_name = message.text
    user_id = message.from_user.id

    # Проверяем, существует ли категория с таким названием
    cursor.execute("SELECT * FROM categories WHERE name = %s AND chat_id = %s", (category_name, user_id))
    category = cursor.fetchone()

    if category:
        await message.answer("Категория с таким названием уже существует!")
        return

    # Сохраняем категорию в БД
    cursor.execute("INSERT INTO categories (name, chat_id) VALUES (%s, %s)", (category_name, user_id))
    conn.commit()

    await message.answer(f"Категория '{category_name}' успешно добавлена!")
    await state.clear()

