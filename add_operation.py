from datetime import datetime

import psycopg2
import requests
from aiogram import Dispatcher, Bot, Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from db import conn, cursor, router

class AddOperation(StatesGroup):
    waiting_for_operation_type = State()
    waiting_for_amount = State()
    waiting_for_date = State()
    waiting_for_category = State()  # Новое состояние для ввода категории

@router.message(Command("add_operation"))
async def add_operation(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    cursor.execute("SELECT * FROM users WHERE users_id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        await message.answer('Вы не зарегистрированы! Для регистрации используйте команду /reg')
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="РАСХОД"), KeyboardButton(text="ДОХОД")],
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите тип операции:", reply_markup=keyboard)
    await state.set_state(AddOperation.waiting_for_operation_type)

@router.message(AddOperation.waiting_for_operation_type)
async def process_operation_type(message: Message, state: FSMContext):
    operation_type = message.text

    if operation_type not in ("РАСХОД", "ДОХОД"):
        await message.answer("Пожалуйста, выберите тип операции, используя кнопки.")
        return

    await state.update_data(operation_type=operation_type)
    await message.answer("Введите сумму операции в рублях:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddOperation.waiting_for_amount)

@router.message(AddOperation.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму.")
        return

    await state.update_data(amount=amount)
    await message.answer("Введите дату операции (ДД.ММ.ГГГГ):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddOperation.waiting_for_date)

@router.message(AddOperation.waiting_for_date)
async def process_date(message: Message, state: FSMContext):
    try:
        date = datetime.strptime(message.text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer("Пожалуйста, введите корректную дату в формате ДД.ММ.ГГГГ.")
        return

    await state.update_data(date=date)
    await message.answer("Введите название категории операции:")
    await state.set_state(AddOperation.waiting_for_category)

@router.message(AddOperation.waiting_for_category)
async def process_category(message: Message, state: FSMContext):
    category_name = message.text
    user_id = message.from_user.id

    # Проверяем, существует ли категория у пользователя
    cursor.execute("SELECT id FROM categories WHERE name = %s AND chat_id = %s", (category_name, user_id))
    category = cursor.fetchone()

    if not category:
        await message.answer(f"У вас нет категории '{category_name}'. Добавьте ее с помощью команды /add_category.")
        return

    data = await state.get_data()
    operation_type = data['operation_type']
    amount = data['amount']
    date = data['date']

    # Сохраняем операцию в БД
    cursor.execute("INSERT INTO operations (operation_date, amount, users_id, operation_type, category_id) VALUES (%s, %s, %s, %s, %s)",
                   (date, amount, user_id, operation_type, category[0]))
    conn.commit()

    await message.answer(f"Операция '{operation_type}' на сумму {amount} рублей добавлена в категорию '{category_name}'.")
    await state.finish()