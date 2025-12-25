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
    await message.answer(
        "Введите название команды (например: Boston, Toronto, CSKA, Spartak,"
        " Dinamo, Bruins, Maple Leafs, Red Wings):",
        reply_markup=ReplyKeyboardRemove()  # Убираем клавиатуру для чистого ввода
    )
    # Устанавливаем состояние ожидания названия команды
    await state.set_state(SearchStates.waiting_team_name)


@router.message(SearchStates.waiting_team_name)  # Обработчик для состояния ожидания названия команды
async def process_team_name(message: Message, state: FSMContext):
    # Получаем и очищаем введенное название команды
    team_name = message.text.strip()
    # Проверяем, что пользователь ввел то что не уберёт .strip()
    if not team_name:
        await message.answer("Пожалуйста, введите название команды.")
        return
    if len(team_name) < 3:
        await message.answer("Название должно содержать минимум 3 символа.")
        return

    await message.answer(f"Поиск команды '{team_name}'...")

    try:
        teams = await api_client.search_teams(team_name)
        # Проверяем, найдены ли команды
        if teams:
            response_text = "<b>Найдены команды:</b>\n\n"

            # Вывод до 5 команд
            for i, team_data in enumerate(teams[:5], 1):
                team_name_value = team_data.get('name', 'Не указано')
                country_info = team_data.get('country', {})
                country_name = country_info.get('name', 'Не указана') if isinstance(country_info,
                                                                                    dict) else 'Не указана'
                founded_year = team_data.get('founded')
                logo_url = team_data.get('logo', '')

                # Информация о стадионе
                venue_info = team_data.get('venue', {})
                venue_name = venue_info.get('name', 'Не указано')
                venue_city = venue_info.get('city', '')

                response_text += (
                    f"{i}. <b>{team_name_value}</b>\n"
                    f"   Страна: {country_name}\n"
                )
                # Год основания
                if founded_year:
                    response_text += f"   Основана: {founded_year} г.\n"
                # Стадион
                if venue_name and venue_name != 'Не указано':
                    if venue_city:
                        response_text += f"   Стадион: {venue_name} ({venue_city})\n"
                    else:
                        response_text += f"   Стадион: {venue_name}\n"
                # Логотип
                if logo_url:
                    response_text += f"   Логотип: {logo_url}\n"

            await message.answer(response_text, parse_mode="HTML")
        else:
            await message.answer("По вашему запросу ничего не найдено.")
            return

    except Exception as e:
        # Обработка ошибок при запросе к API
        error_msg = str(e)
        await message.answer(f"Ошибка: {error_msg}")
        return

    await state.clear()
    await message.answer("Выберите следующее действие:", reply_markup=get_main_keyboard())


# Поиск лиг
@router.message(F.text == "Поиск лиг")  # Обработчик для кнопки "Поиск лиг"
async def search_leagues_start(message: Message, state: FSMContext):
    await message.answer(
        "Введите название лиги (например: KHL, NHL, SHL, Liiga, Extraleague, VHL, MHL, NLA):",
        reply_markup=ReplyKeyboardRemove()
    )
    # Устанавливаем состояние ожидания названия лиги
    await state.set_state(SearchStates.waiting_league_search)


@router.message(SearchStates.waiting_league_search)  # Обработчик для сост ожидания
async def process_league_search(message: Message, state: FSMContext):
    # Получаем и очищаем поисковый запрос
    search_query = message.text.strip()

    if not search_query:
        await message.answer("Пожалуйста, введите название лиги.")
        return

    await message.answer(f"Поиск лиги '{search_query}'...")

    try:
        # API для поиска лиг
        leagues = await api_client.search_leagues(search_query)

        # Проверяем, найдены ли лиги
        if leagues:
            response_text = "<b>Найдены лиги:</b>\n\n"

            # Ограничиваем вывод до 5 лиг
            for i, league_data in enumerate(leagues[:5], 1):
                # Извлекаем данные о лиге
                league_name = league_data.get('name', 'Не указано')
                league_type = league_data.get('type', 'Не указано')
                country_info = league_data.get('country', {})
                country_name = country_info.get('name', 'Не указана') if isinstance(country_info,
                                                                                    dict) else 'Не указана'
                league_id = league_data.get('id', 'Не указан')

                # Получаем логотип лиги
                logo_url = league_data.get('logo', '')

                # Форматируем информацию о лиге
                response_text += (
                    f"{i}. <b>{league_name}</b>\n"
                    f"   Страна: {country_name}\n"
                    f"   Тип: {league_type}\n"
                    f"   ID: {league_id}\n"
                )
                # Добавляем ссылку на логотип, если он есть
                if logo_url:
                    response_text += f"   Лого: {logo_url}\n"

            # Отправляем результат пользователю
            await message.answer(response_text, parse_mode="HTML")
        else:
            # Если лиги не найдены
            await message.answer("Лиги не найдены. Попробуйте ещё раз")
            return

    except Exception as e:
        # Обработка ошибок при запросе к API
        error_msg = str(e)
        await message.answer(f"Ошибка: {error_msg}")
        return
    await state.clear()
    await message.answer("Выберите следующее действие:", reply_markup=get_main_keyboard())


# Турнирная таблица лиги
@router.message(F.text == "Турнирная таблица")  # Обработчик для кнопки "Турнирная таблица"
async def league_standings_start(message: Message, state: FSMContext):
    # Запрашиваем у пользователя ID лиги
    await message.answer(
        "Введите ID лиги для просмотра таблицы:\n\n"
        "<b>Примеры ID лиг:</b>\n"
        "• 35 - KHL - Континентальная хоккейная лига\n"
        "• 1 - Extraleague - Беларусь\n"
        "• 32 - PHL - Польша\n"
        "• 3 - OXL - Канада\n"
        "• 28 - Dutch Cup - Нидерланды\n\n"
        "ID можно узнать через поиск лиг",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    # Устанавливаем состояние ожидания ID лиги
    await state.set_state(SearchStates.waiting_league_for_standings)


@router.message(SearchStates.waiting_league_for_standings)  # Обработчик для сост ожидания
async def process_league_standings(message: Message, state: FSMContext):
    league_id = message.text.strip()
    # Проверяем, что введено число
    if not league_id or not league_id.isdigit():
        await message.answer("Пожалуйста, введите ID лиги.")
        return

    await message.answer(f"Загружаю таблицу лиги ID {league_id}...")

    try:
        # API для таблицы лиги
        standings_data = await api_client.get_league_standings(league_id, "2023")
        # Проверяем, получены ли данные
        if standings_data and len(standings_data) > 0:
            # standings_data[0] - список команд
            teams_list = standings_data[0]

            # Проверяем структуру данных
            if isinstance(teams_list, list) and len(teams_list) > 0:
                # Получаем информацию о лиге из первой команды
                league_name = teams_list[0].get('league', {}).get('name', f"Лига {league_id}")
                country_name = teams_list[0].get('country', {}).get('name', 'Неизвестно')

                # Формируем заголовок таблицы
                response_text = (
                    f"<b>{league_name}</b>\n"
                    f"Страна: {country_name}\n"
                    f"Сезон: 2023\n\n"
                    f"<b>Турнирная таблица (топ-10):</b>\n\n"
                )

                # Выводим топ-10 команд
                for team_info in teams_list[:10]:
                    # Извлекаем данные о команде
                    position = team_info.get('position', '?')
                    team_name = team_info.get('team', {}).get('name', 'Неизвестно')
                    points = team_info.get('points', 0)

                    # Получаем статистику игр
                    games_info = team_info.get('games', {})
                    games_played = games_info.get('played', 0)

                    # Форматируем позицию
                    if position in [1, 2, 3]:
                        position_str = f"{position}. "
                    else:
                        position_str = f"{position}. "

                    response_text += (
                        f"{position_str}<b>{team_name}</b>\n"
                        f"   Очки: {points}\n"
                        f"   Игр: {games_played}\n"
                    )
                # Если команд больше 10
                if len(teams_list) > 10:
                    response_text += f"\n... и ещё {len(teams_list) - 10} команд"

                await message.answer(response_text, parse_mode="HTML")

            else:
                await message.answer("Таблица пуста.")

        else:
            await message.answer(f"Не удалось загрузить таблицу для лиги ID {league_id}.")
            return

    except Exception as e:
        # Обработка ошибок при запросе к API
        error_msg = str(e)
        await message.answer(f"Ошибка при загрузке таблицы: {error_msg}")
        return
    await state.clear()
    await message.answer("Выберите следующее действие:", reply_markup=get_main_keyboard())


# Для неизвестных команд
@router.message()  # Обработчик для всех остальных сообщений
async def handle_unknown_message(message: Message):
    # Команда не распознана
    await message.answer(
        "Я не понял вашу команду.\n\n"
        "Пожалуйста, используйте кнопки меню или команду /start",
        reply_markup=get_main_keyboard()
    )