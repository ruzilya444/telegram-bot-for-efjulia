import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup)
import aiosqlite
import asyncio

# Создаем объекты бота и диспетчера
bot = Bot(token="7691424169:AAF5w-dIzNgZruh0qiGA3HBnMEOKoz8Wvb0")
dp = Dispatcher()

# Этот хэндлер будет срабатывать на команду "/start" и добавлять клавиатуру
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text='Что вы хотите сделать? Нажмите на одну из кнопок',
        reply_markup=keyboard
    )

# Создаем объекты кнопок
button_1 = KeyboardButton(text='камень')
button_2 = KeyboardButton(text='ножницы')
button_3 = KeyboardButton(text='бумага')
button_5 = KeyboardButton(text='отмена')
button_6 = KeyboardButton(text='все планы')
button_7 = KeyboardButton(text='планы на 2 дня')
button_8 = KeyboardButton(text='добавить мероприятие')
button_9 = KeyboardButton(text='поиграть в камень-ножницы-бумага')

# Создаем объект клавиатуры, добавляя в него кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[[button_6, button_7],
              [button_8, button_9],
              [button_5]],
    resize_keyboard=True
)

url_button_1 = InlineKeyboardButton(
    text='вк автора',
    url='https://vk.com/urmanchee'
)

tg_name = 'urmanchee'
url_button_2 = InlineKeyboardButton(
    text='телеграмм автора',
    url=f'https://t.me/{tg_name}'
)

keyboard2 = InlineKeyboardMarkup(
    inline_keyboard=[[url_button_1],
                     [url_button_2]]
)

# Создаем объект клавиатуры, добавляя в него кнопки
keyboard3 = ReplyKeyboardMarkup(
    keyboard=[[button_1, button_2, button_3, button_5]],
    resize_keyboard=True
)

# Подключение к базе данных
DB_NAME = "schedule.db"

async def setup_database():
    """Создает таблицу, если её нет."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            title TEXT
        )
        """)
        await db.commit()


async def remove_expired_events():
    """Удаляет мероприятия, которые уже прошли."""
    current_date = datetime.now().date()
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        DELETE FROM events WHERE date < ?
        """, (current_date.isoformat(),))
        await db.commit()
#

# Этот хэндлер будет срабатывать на ответ "камень-ножницы-бумага" и добавлять другую клавиатуру клавиатуру
@dp.message(F.text == 'поиграть в камень-ножницы-бумага')
async def process_dog_answer(message: Message):
    rez = winner(message.text.lower())
    await message.answer(
        text='Выбирите либо камень, либо ножницы, либо бумагу',
        reply_markup=keyboard3
    )

# Этот хэндлер будет срабатывать на ответ "камень" и удалять клавиатуру
@dp.message(F.text == 'камень')
async def process_dog_answer(message: Message):
    rez = winner(message.text.lower())
    await message.answer(
        text=rez,
        reply_markup=ReplyKeyboardRemove()
    )

# Этот хэндлер будет срабатывать на ответ "ножницы" и удалять клавиатуру
@dp.message(F.text == 'ножницы')
async def process_dog_answer(message: Message):
    rez = winner(message.text.lower())
    await message.answer(
        text=rez,
        reply_markup=ReplyKeyboardRemove()
    )

# Этот хэндлер будет срабатывать на ответ "бумага" и удалять клавиатуру
@dp.message(F.text == 'бумага')
async def process_dog_answer(message: Message):
    rez = winner(message.text.lower())
    await message.answer(
        text=rez,
        reply_markup=ReplyKeyboardRemove()
    )

# Этот хэндлер будет срабатывать на ответ "отмена" и возвращать на исходную клавиатуру
@dp.message(F.text == 'отмена')
async def process_cucumber_answer(message: Message):
    await message.answer(
        text="oк, можете продолжить пользоваться ботом через команду /start",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(lambda message: message.text == "добавить мероприятие")
async def add_event_prompt(message: Message):
    """Запрашивает у пользователя данные о мероприятии."""
    await message.answer("Введите данные о мероприятии в формате: дата (ГГГГ-ММ-ДД), время (ЧЧ:ММ), название.")

@dp.message(lambda message: message.text == "планы на 2 дня")
async def show_next_2_days(message: Message):
    """Показывает планы на ближайшие 2 дня."""
    today = datetime.now().date()
    two_days_later = today + timedelta(days=2)
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
        SELECT date, time, title FROM events WHERE date BETWEEN ? AND ?
        ORDER BY date, time
        """, (today.isoformat(), two_days_later.isoformat()))
        events = await cursor.fetchall()
    if events:
        response = "Ваши планы на 2 дня:\n" + "\n".join(
            [f"{date} {time} - {title}" for date, time, title in events]
        )
    else:
        response = "Нет мероприятий на ближайшие 2 дня."
    await message.answer(response)

@dp.message(lambda message: message.text == "все планы")
async def show_all_events(message: Message):
    """Показывает все планы."""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
        SELECT date, time, title FROM events ORDER BY date, time
        """)
        events = await cursor.fetchall()
    if events:
        response = "Ваши планы:\n" + "\n".join(
            [f"{date} {time} - {title}" for date, time, title in events]
        )
    else:
        response = "Расписание пусто."
    await message.answer(response)

# игра камень ножницы бумага
def winner(pl):
    com = random.randint(1, 3)
    if pl == 'камень':
        if com == 1:
            return 'Компьютер выбрал Камень, ничья'
        if com == 2:
            return 'Компьютер выбрал ножницы. Камень бьёт ножницы, игрок победил!'
        if com == 3:
            return ' Компьютер выбрал бумагу. Бумага кроет камень, компьютер победил!'
    if pl == 'ножницы':
        if com == 2:
            return 'Компьютер выбрал ножницы. Ничья'
        if com == 1:
            return 'Компьютер выбрал Камень,Камень бьёт ножницы, компьютер победил!'
        if com == 3:
            return 'Компьютер выбрал бумага.Ножницы режут бумагу, игрок победил!'
    if pl == 'бумага':
        if com == 3:
            return 'Компьютер выбрал бумага. Ничья'
        if com == 1:
            return 'Компьютер выбрал Камень. Бумага кроет камень, игрок победил!'
        if com == 2:
            return 'Компьютер выбрал ножницы.Ножницы режет бумагу, компьютер победил!'

# Этот хэндлер будет срабатывать на команду "help" и добавлять другую клавиатуру
@dp.message(F.text == '/help')
async def process_dog_answer(message: Message):
    await message.answer(
        text=''' в боте есть функции: 
/start
/help
/about
/contacts
/payments
'''
    )

# Этот хэндлер будет срабатывать на команду "about" и добавлять другую клавиатуру
@dp.message(F.text == '/about')
async def process_dog_answer(message: Message):
    await message.answer(
        text='''Если вы забываете о том, что вам куда-то нужно - расписание, то, что действительно вам нужно!'''
    )

# Этот хэндлер будет срабатывать на команду "contacts" и добавлять другую клавиатуру
@dp.message(F.text == '/contacts')
async def process_dog_answer(message: Message):
    await message.answer(
        text='''Если возникли вопросы по работе бота - пишите на почту urmancheeva08@inbox.ru, или в телеграмм @urmanchee''',
        reply_markup = keyboard2
    )

# Этот хэндлер будет срабатывать на команду "payments" и добавлять другую клавиатуру
@dp.message(F.text == '/payments')
async def process_dog_answer(message: Message):
    await message.answer(
        text='''Поддержать проект можно денюжками, по номеру +7 917 939 6923 - Ефимова Юлия Викторовна'''
    )

@dp.message()
async def handle_event_input(message: Message):
    """Обрабатывает ввод данных о мероприятии."""
    try:
        date_str, time_str, title = message.text.split(", ")
        event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        event_time = datetime.strptime(time_str, "%H:%M").time()

        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("""
            INSERT INTO events (date, time, title) VALUES (?, ?, ?)
            """, (event_date.isoformat(), event_time.strftime("%H:%M"), title))
            await db.commit()

        await message.answer(f"Мероприятие добавлено: {event_date} {event_time} - {title}", reply_markup=keyboard)
    except ValueError:
        await message.answer(
            "Неверный формат. Пожалуйста, введите данные в формате: дата (ГГГГ-ММ-ДД), время (ЧЧ:ММ), название.")

#Создаем асинхронною функцию
async def set_main_menu(bot: Bot):
    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/start', description='Начать работу с ботом'),
        BotCommand(command='/help', description='Справка'),
        BotCommand(command='/about',  description='О программе'),
        BotCommand(command='/contacts', description='Проблемки с ботом'),
        BotCommand(command='/payments', description='Донаты Ю.В.')
    ]
    await bot.set_my_commands(main_menu_commands)

# Главная функция
async def main():
    print("Бот запущен...")
    await setup_database()  # Настройка базы данных
    await remove_expired_events()  # Удаление устаревших событий
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
