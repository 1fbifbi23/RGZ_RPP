import psycopg2
from aiogram import Dispatcher, Bot, Router, types, F

# Подключение к базе данных
conn = psycopg2.connect(dbname="lari_bok", user="larionov_bokov12", password="123", host="127.0.0.1")
cursor = conn.cursor()

router = Router()
