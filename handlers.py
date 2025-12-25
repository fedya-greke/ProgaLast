# Импорт необходимых библиотек
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from api_client import HockeyAPIClient  # Наш клиент для работы с API хоккея
from keyboards import get_main_keyboard

# Создаем router для обработки сообщений
router = Router()

# Экземпляр клиента API
api_client = HockeyAPIClient()

# Каждое состояние соответствует ожиданию определенного ввода от пользователя
class SearchStates(StatesGroup):
    waiting_team_name = State()  # Ожидаем названия команды
    waiting_league_search = State()  # Ожидаем названия лиги
    waiting_league_for_standings = State()  # Ожидаем ID лиги для таблицы


# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = (
        "<b>Хоккейный бот</b>\n\n"
        "<b>Доступные функции:</b>\n"
        "1. Поиск команды по названию\n"
        "2. Поиск лиг\n"
        "3. Турнирная таблица лиги\n\n"
        "Выберите действие с помощью кнопок ниже"
    )
    # Отправляем сообщение с HTML-разметкой и главной клавиатурой
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")


# Поиск команды по названию
@router.message(F.text == "Поиск команды")  # Обработчик для кнопки "Поиск команды"
async def search_team_start(message: Message, state: FSMContext):
    pass

@router.message(SearchStates.waiting_team_name)  # Обработчик для состояния ожидания названия команды
async def process_team_name(message: Message, state: FSMContext):
    pass


# Поиск лиг
@router.message(F.text == "Поиск лиг")  # Обработчик для кнопки "Поиск лиг"
async def search_leagues_start(message: Message, state: FSMContext):
    pass


@router.message(SearchStates.waiting_league_search)  # Обработчик для сост ожидания
async def process_league_search(message: Message, state: FSMContext):
    pass


# Турнирная таблица лиги
@router.message(F.text == "Турнирная таблица")  # Обработчик для кнопки "Турнирная таблица"
async def league_standings_start(message: Message, state: FSMContext):
    pass


# Для неизвестных команд
@router.message()  # Обработчик для всех остальных сообщений
async def handle_unknown_message(message: Message):
    # Команда не распознана
    await message.answer(
        "Я не понял вашу команду.\n\n"
        "Пожалуйста, используйте кнопки меню или команду /start",
        reply_markup=get_main_keyboard()
    )