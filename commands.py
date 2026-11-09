from aiogram.filters import Command
from aiogram.types import BotCommand


FILMS_COMMAND = Command("films")
START_COMMAND = Command("start")
FILM_CREATE_COMMAND = Command("create_film")
FILM_SEARCH_COMMAND = Command("search_movie")
FILM_FILTER_COMMAND = Command("filter_movies")
FILM_DELETE_COMMAND = Command("delete_movie")
FILM_EDIT_COMMAND = Command("edit_movie")
FILM_RATE_COMMAND = Command("rate_movie")
FILM_RECOMMEND_COMMAND = Command("recommend_movie")


BOT_COMMANDS = [
    BotCommand(
        command="start",
        description="Почати роботу з ботом",
    ),
    BotCommand(
        command="films",
        description="Переглянути фільми",
    ),
    BotCommand(
        command="create_film",
        description="Додати фільм",
    ),
    BotCommand(
        command="search_movie",
        description="Знайти фільм",
    ),
    BotCommand(
        command="filter_movies",
        description="Фільтрувати фільми",
    ),
    BotCommand(
        command="delete_movie",
        description="Видалити фільм",
    ),
    BotCommand(
        command="edit_movie",
        description="Редагувати фільм",
    ),
    BotCommand(
        command="rate_movie",
        description="Оцінити фільм",
    ),
    BotCommand(
        command="recommend_movie",
        description="Отримати рекомендацію",
    ),
]