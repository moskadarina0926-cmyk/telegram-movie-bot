
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardRemove,
    URLInputFile,
)

from commands import (
    BOT_COMMANDS,
    FILM_CREATE_COMMAND,
    FILM_DELETE_COMMAND,
    FILM_EDIT_COMMAND,
    FILM_FILTER_COMMAND,
    FILM_RATE_COMMAND,
    FILM_RECOMMEND_COMMAND,
    FILM_SEARCH_COMMAND,
    FILMS_COMMAND,
)
from config import BOT_TOKEN
from data import (
    add_film,
    delete_film,
    edit_film,
    filter_films,
    find_films,
    get_films,
    get_recommendation,
    rate_film,
)
from external import async_log_function_call, log_user_message
from keyboards import FilmCallback, films_keyboard_markup, main_menu
from models import Film


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)

dp = Dispatcher()


class FilmForm(StatesGroup):
    """Стани для створення та керування фільмами."""

    name = State()
    description = State()
    rating = State()
    genre = State()
    year = State()
    actors = State()
    poster = State()
    search = State()
    filter = State()
    delete = State()
    edit = State()
    edit_description = State()
    rate = State()
    set_rating = State()


def film_text(film: dict) -> str:
    """Формує текст із детальною інформацією про фільм."""

    actors = ", ".join(film.get("actors", []))

    return (
        f"<b>{html.quote(film['name'])}</b>\n\n"
        f"{html.quote(film['description'])}\n\n"
        f"Рейтинг: {film['rating']}/10\n"
        f"Жанр: {html.quote(film['genre'])}\n"
        f"Рік: {film['year']}\n"
        f"Актори: {html.quote(actors)}"
    )


async def send_film(
    message: Message,
    film: dict,
) -> None:
    """Відправляє користувачу інформацію про фільм."""

    text = film_text(film)
    poster = film.get("poster", "").strip()

    if poster.startswith(("http://", "https://")):
        try:
            await message.answer_photo(
                photo=URLInputFile(poster),
                caption=text,
            )
            return
        except Exception:
            logger.warning(
                "Не вдалося завантажити постер: %s",
                poster,
            )

    await message.answer(text)


@dp.message(Command("start"))
@async_log_function_call
async def start(message: Message, state: FSMContext):
    await state.clear()
    log_user_message(message)

    name = html.quote(
        message.from_user.first_name or "користувач"
    )

    await message.answer(
        f"Вітаю, <b>{name}</b>!\n\n"
        "Це моя персональна бібліотека фільмів.\n"
        "Тут можна шукати, додавати, редагувати "
        "та оцінювати фільми.",
        reply_markup=main_menu,
    )


@dp.message(FILMS_COMMAND)
@dp.message(F.text == "Усі фільми")
@async_log_function_call
async def films(message: Message):
    log_user_message(message)

    films_list = get_films()

    if not films_list:
        await message.answer("Поки що бібліотека порожня.")
        return

    await message.answer(
        "Обери фільм зі списку:",
        reply_markup=films_keyboard_markup(films_list),
    )


@dp.callback_query(FilmCallback.filter())
async def show_film(
    callback: CallbackQuery,
    callback_data: FilmCallback,
):
    film = get_films(film_id=callback_data.id)

    await callback.answer()

    if not isinstance(film, dict):
        await callback.message.answer(
            "Не вдалося знайти цей фільм."
        )
        return

    await send_film(callback.message, film)


@dp.message(FILM_SEARCH_COMMAND)
@dp.message(F.text == "Знайти фільм")
@async_log_function_call
async def search_movie(
    message: Message,
    state: FSMContext,
):
    log_user_message(message)

    await state.set_state(FilmForm.search)

    await message.answer(
        "Введіть назву фільму або її частину:",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.search)
async def search_result(
    message: Message,
    state: FSMContext,
):
    results = find_films(message.text or "")
    await state.clear()

    if not results:
        await message.answer(
            "На жаль, такого фільму не знайдено.",
            reply_markup=main_menu,
        )
        return

    await message.answer(
        f"Знайдено фільмів: {len(results)}"
    )

    for film in results:
        await send_film(message, film)

    await message.answer(
        "Можеш продовжити роботу з меню.",
        reply_markup=main_menu,
    )


@dp.message(FILM_FILTER_COMMAND)
@dp.message(F.text == "Фільтрувати")
@async_log_function_call
async def filter_movie(
    message: Message,
    state: FSMContext,
):
    log_user_message(message)

    await state.set_state(FilmForm.filter)

    await message.answer(
        "Введіть жанр або рік випуску.\n\n"
        "Наприклад: <code>фантастика</code> "
        "або <code>2009</code>",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.filter)
async def filter_result(
    message: Message,
    state: FSMContext,
):
    results = filter_films(message.text or "")
    await state.clear()

    if not results:
        await message.answer(
            "Фільмів за цим критерієм не знайдено.",
            reply_markup=main_menu,
        )
        return

    await message.answer(
        f"Знайдено: {len(results)}"
    )

    for film in results:
        await send_film(message, film)

    await message.answer(
        "Готово. Обери наступну дію:",
        reply_markup=main_menu,
    )


@dp.message(FILM_CREATE_COMMAND)
@dp.message(F.text == "Додати фільм")
@async_log_function_call
async def film_create(
    message: Message,
    state: FSMContext,
):
    log_user_message(message)

    await state.set_state(FilmForm.name)

    await message.answer(
        "Введіть назву фільму:",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.name)
async def film_name(
    message: Message,
    state: FSMContext,
):
    name = (message.text or "").strip()

    if not name:
        await message.answer(
            "Назва не може бути порожньою. Спробуйте ще раз."
        )
        return

    await state.update_data(name=name)
    await state.set_state(FilmForm.description)

    await message.answer(
        "Введіть короткий опис фільму:"
    )


@dp.message(FilmForm.description)
async def film_description(
    message: Message,
    state: FSMContext,
):
    description = (message.text or "").strip()

    if not description:
        await message.answer(
            "Опис не може бути порожнім."
        )
        return

    await state.update_data(description=description)
    await state.set_state(FilmForm.rating)

    await message.answer(
        "Вкажіть рейтинг від 0 до 10:"
    )


@dp.message(FilmForm.rating)
async def film_rating(
    message: Message,
    state: FSMContext,
):
    try:
        rating = float(message.text.replace(",", "."))
    except (ValueError, AttributeError):
        await message.answer(
            "Рейтинг має бути числом від 0 до 10."
        )
        return

    if not 0 <= rating <= 10:
        await message.answer(
            "Рейтинг повинен бути від 0 до 10."
        )
        return

    await state.update_data(rating=rating)
    await state.set_state(FilmForm.genre)

    await message.answer(
        "Введіть жанр фільму:"
    )


@dp.message(FilmForm.genre)
async def film_genre(
    message: Message,
    state: FSMContext,
):
    genre = (message.text or "").strip()

    if not genre:
        await message.answer(
            "Жанр не може бути порожнім."
        )
        return

    await state.update_data(genre=genre)
    await state.set_state(FilmForm.year)

    await message.answer(
        "Введіть рік виходу фільму:"
    )


@dp.message(FilmForm.year)
async def film_year(
    message: Message,
    state: FSMContext,
):
    try:
        year = int(message.text)
    except (ValueError, TypeError):
        await message.answer(
            "Рік повинен бути цілим числом."
        )
        return

    if not 1888 <= year <= 2100:
        await message.answer(
            "Введіть реальний рік від 1888 до 2100."
        )
        return

    await state.update_data(year=year)
    await state.set_state(FilmForm.actors)

    await message.answer(
        "Введіть акторів через кому.\n"
        "Наприклад: Сем Вортінгтон, Зої Салдана"
    )


@dp.message(FilmForm.actors)
async def film_actors(
    message: Message,
    state: FSMContext,
):
    actors = [
        actor.strip()
        for actor in (message.text or "").split(",")
        if actor.strip()
    ]

    if not actors:
        await message.answer(
            "Потрібно вказати хоча б одного актора."
        )
        return

    await state.update_data(actors=actors)
    await state.set_state(FilmForm.poster)

    await message.answer(
        "Введіть пряме посилання на постер:"
    )


@dp.message(FilmForm.poster)
async def film_poster(
    message: Message,
    state: FSMContext,
):
    poster = (message.text or "").strip()

    if not poster.startswith(("http://", "https://")):
        await message.answer(
            "Посилання повинно починатися з "
            "http:// або https://"
        )
        return

    await state.update_data(poster=poster)
    data = await state.get_data()

    try:
        film = Film(**data)
    except Exception as error:
        logger.error(
            "Помилка створення фільму: %s",
            error,
        )

        await message.answer(
            "Не вдалося створити фільм. "
            "Перевірте введені дані."
        )
        return

    add_film(film.model_dump())
    await state.clear()

    await message.answer(
        f"Фільм <b>{html.quote(film.name)}</b> додано!",
        reply_markup=main_menu,
    )


@dp.message(FILM_DELETE_COMMAND)
@dp.message(F.text == "Видалити фільм")
@async_log_function_call
async def delete_movie(
    message: Message,
    state: FSMContext,
):
    log_user_message(message)

    await state.set_state(FilmForm.delete)

    await message.answer(
        "Введіть точну назву фільму, який потрібно видалити:",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.delete)
async def delete_movie_result(
    message: Message,
    state: FSMContext,
):
    name = (message.text or "").strip()

    if delete_film(name):
        answer = "Фільм успішно видалено."
    else:
        answer = "Фільм з такою назвою не знайдено."

    await state.clear()

    await message.answer(
        answer,
        reply_markup=main_menu,
    )


@dp.message(FILM_EDIT_COMMAND)
@dp.message(F.text == "Редагувати фільм")
@async_log_function_call
async def edit_movie(
    message: Message,
    state: FSMContext,
):
    log_user_message(message)

    await state.set_state(FilmForm.edit)

    await message.answer(
        "Введіть назву фільму, опис якого потрібно змінити:",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.edit)
async def edit_movie_result(
    message: Message,
    state: FSMContext,
):
    name = (message.text or "").strip()
    films_list = get_films()

    film_exists = any(
        film["name"].casefold() == name.casefold()
        for film in films_list
    )

    if not film_exists:
        await state.clear()

        await message.answer(
            "Фільм не знайдено.",
            reply_markup=main_menu,
        )
        return

    await state.update_data(edit_name=name)
    await state.set_state(FilmForm.edit_description)

    await message.answer(
        "Введіть новий опис фільму:"
    )


@dp.message(FilmForm.edit_description)
async def update_description(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()
    name = data.get("edit_name")
    description = (message.text or "").strip()

    if not description:
        await message.answer(
            "Опис не може бути порожнім."
        )
        return

    changed = edit_film(
        name=name,
        new_description=description,
    )

    await state.clear()

    if changed:
        await message.answer(
            "Опис фільму успішно оновлено.",
            reply_markup=main_menu,
        )
    else:
        await message.answer(
            "Не вдалося змінити опис.",
            reply_markup=main_menu,
        )


@dp.message(FILM_RATE_COMMAND)
@dp.message(F.text == "Оцінити фільм")
@async_log_function_call
async def rate_movie(
    message: Message,
    state: FSMContext,
):
    log_user_message(message)

    await state.set_state(FilmForm.rate)

    await message.answer(
        "Введіть назву фільму, який хочете оцінити:",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.rate)
async def rate_movie_name(
    message: Message,
    state: FSMContext,
):
    name = (message.text or "").strip()
    films_list = get_films()

    film_exists = any(
        film["name"].casefold() == name.casefold()
        for film in films_list
    )

    if not film_exists:
        await state.clear()

        await message.answer(
            "Фільм не знайдено.",
            reply_markup=main_menu,
        )
        return

    await state.update_data(rate_name=name)
    await state.set_state(FilmForm.set_rating)

    await message.answer(
        "Введіть новий рейтинг від 0 до 10:"
    )


@dp.message(FilmForm.set_rating)
async def set_rating(
    message: Message,
    state: FSMContext,
):
    try:
        rating = float(message.text.replace(",", "."))
    except (ValueError, AttributeError):
        await message.answer(
            "Введіть число від 0 до 10."
        )
        return

    if not 0 <= rating <= 10:
        await message.answer(
            "Рейтинг повинен бути від 0 до 10."
        )
        return

    data = await state.get_data()

    changed = rate_film(
        name=data["rate_name"],
        rating=rating,
    )

    await state.clear()

    if changed:
        await message.answer(
            f"Рейтинг оновлено: {rating}/10",
            reply_markup=main_menu,
        )
    else:
        await message.answer(
            "Не вдалося оновити рейтинг.",
            reply_markup=main_menu,
        )


@dp.message(FILM_RECOMMEND_COMMAND)
@dp.message(F.text == "Рекомендація")
@async_log_function_call
async def recommend_movie(message: Message):
    log_user_message(message)

    film = get_recommendation()

    if film is None:
        await message.answer(
            "У бібліотеці поки немає фільмів.",
            reply_markup=main_menu,
        )
        return

    await message.answer("Моя рекомендація:")
    await send_film(message, film)


@dp.message(Command("cancel"))
async def cancel_action(
    message: Message,
    state: FSMContext,
):
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            "Зараз немає активної операції.",
            reply_markup=main_menu,
        )
        return

    await state.clear()

    await message.answer(
        "Операцію скасовано.",
        reply_markup=main_menu,
    )


@dp.message()
async def unknown_message(message: Message):
    log_user_message(message)

    await message.answer(
        "Я не зовсім зрозумів запит.\n"
        "Скористайся кнопками меню або командою /start.",
        reply_markup=main_menu,
    )


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        ),
    )

    await bot.set_my_commands(BOT_COMMANDS)

    logger.info("Бот запускається...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())