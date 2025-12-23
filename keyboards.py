from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    """Создает главную клавиатуру бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Найти команду")],
            [KeyboardButton(text="Найти игрока")],
            [KeyboardButton(text="Ближайшие матчи команды")]
        ],
        resize_keyboard=True  # Кнопки подстроятся под экран
    )
    return keyboard