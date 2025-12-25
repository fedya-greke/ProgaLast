import aiohttp
from typing import Optional, Dict, Any, List
from config import API_KEY


class HockeyAPIClient:
    """Клиент для работы с Hockey API"""

    def __init__(self):
        # URL API
        self.base_url = 'https://v1.hockey.api-sports.io'
        # headers с API ключом
        self.headers = {'x-apisports-key': API_KEY}

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Базовый метод для выполнения гет-запросов к API"""
        # Полный URL запроса
        url = f"{self.base_url}/{endpoint}"

        try:
            # Создаем асинхронную HTTP сессию
            async with aiohttp.ClientSession() as session:
                # Выполняем гет запрос с параметрами и заголовками
                async with session.get(url, headers=self.headers, params=params, timeout=10) as response:

                    # Проверяем статус ответа - должен быть 200 OK
                    if response.status != 200:
                        # Убираем лишнюю вложенность
                        if response.status == 429:
                            raise Exception("Превышен лимит запросов")
                        elif response.status == 404:
                            raise Exception("Ресурс не найден")
                        else:
                            raise Exception(f"Ошибка сервера: {response.status}")

                    data = await response.json()

                    # Переводим ошибки API на русский
                    if 'errors' in data and data['errors']:
                        error_msg = list(data['errors'].values())[0] if isinstance(data['errors'], dict) else str(
                            data['errors'])

                        # Пользовательские сообщения для разных типов ошибок
                        if "must be at least 3 characters" in error_msg:
                            raise Exception("Запрос должен содержать минимум 3 символа")
                        elif "endpoint do not exist" in error_msg:
                            raise Exception("Эта функция временно недоступна")
                        elif "plan" in error_msg and "Free" in error_msg:
                            # Бесплатный тариф не поддерживает этот запрос((
                            raise Exception("Эта функция временно недоступна")
                        elif "season" in error_msg:
                            raise Exception("Сезон временно недоступен")
                        else:
                            raise Exception("Непредвиденная ошибка (название должно быть на английском)")

                    return data

        except aiohttp.ClientError as e:
            # Обработка сетевых ошибок
            raise Exception(f"Ошибка сети: {str(e)}")
        except Exception as e:
            # Обработка остальных ошибок
            raise Exception(f"{str(e)}")

    async def search_teams(self, name: str) -> List[Dict]:
        """Поиск команд по названию"""
        params = {'search': name}
        # Выполняем запрос к эндпоинту teams
        data = await self._make_request('teams', params)
        return data.get('response', [])

    async def search_leagues(self, search_query: str) -> List[Dict]:
        """Поиск лиг по названию"""
        params = {'search': search_query}
        # Эндпоинт - leagues
        data = await self._make_request('leagues', params)
        return data.get('response', [])

    async def get_league_standings(self, league_id: str = "1", season: str = "2023") -> List[Dict]:
        """Получить турнирную таблицу лиги"""
        # Параметры - ID лиги и сезон
        params = {'league': league_id, 'season': season}
        # Эндпоинт - standings
        data = await self._make_request('standings', params)
        return data.get('response', [])