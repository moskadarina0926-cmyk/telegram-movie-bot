from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class FilmCallback(CallbackData, prefix="film", sep=";"):
    """Дані для кнопки конкретного фільму."""

    id: int


def films_keyboard_markup(
    films_list: list[dict],
):
    """Створює клавіатуру зі списком фільмів."""

    builder = InlineKeyboardBuilder()

    for index, film in enumerate(films_list):
        builder.button(
            text=f"{film['name']}",
            callback_data=FilmCallback(id=index),
        )

    builder.adjust(1)

    return builder.as_markup()


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Усі фільми"),
            KeyboardButton(text="Знайти фільм"),
        ],
        [
            KeyboardButton(text="Додати фільм"),
            KeyboardButton(text="Фільтрувати"),
        ],
        [
            KeyboardButton(text="Видалити фільм"),
            KeyboardButton(text="Редагувати фільм"),
        ],
        [
            KeyboardButton(text="Оцінити фільм"),
            KeyboardButton(text="Рекомендація"),
        ],
    ],
    resize_keyboard=True,
)