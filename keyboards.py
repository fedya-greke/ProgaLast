from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    """Создает главную клавиатуру бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Поиск команды")],
            [KeyboardButton(text="Поиск лиг")],
            [KeyboardButton(text="Турнирная таблица")]
        ],
        resize_keyboard=True,  # Кнопки подстроятся под экран
        input_field_placeholder = "Выберите действие..." # Подсказка в поле ввода
    )
    return keyboard