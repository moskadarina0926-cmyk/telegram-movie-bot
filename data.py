import json
from pathlib import Path


DATA_FILE = Path(__file__).parent / "data.json"


def _load_films(file_path: str | Path = DATA_FILE) -> list[dict]:
    """Завантажує список фільмів із JSON."""

    path = Path(file_path)

    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def _save_films(
    films: list[dict],
    file_path: str | Path = DATA_FILE,
) -> None:
    """Зберігає список фільмів у JSON."""

    with Path(file_path).open("w", encoding="utf-8") as file:
        json.dump(
            films,
            file,
            ensure_ascii=False,
            indent=4,
        )


def get_films(
    file_path: str | Path = DATA_FILE,
    film_id: int | None = None,
) -> list[dict] | dict | None:
    """Повертає всі фільми або один фільм за індексом."""

    films = _load_films(file_path)

    if film_id is None:
        return films

    if 0 <= film_id < len(films):
        return films[film_id]

    return None


def find_films(
    query: str,
    file_path: str | Path = DATA_FILE,
) -> list[dict]:
    """Шукає фільми за частиною назви."""

    query = query.strip().casefold()

    if not query:
        return []

    films = _load_films(file_path)

    return [
        film
        for film in films
        if query in film.get("name", "").casefold()
    ]


def filter_films(
    criteria: str,
    file_path: str | Path = DATA_FILE,
) -> list[dict]:
    """Фільтрує фільми за жанром або роком."""

    criteria = criteria.strip().casefold()

    if not criteria:
        return []

    films = _load_films(file_path)

    return [
        film
        for film in films
        if (
            criteria in film.get("genre", "").casefold()
            or str(film.get("year", "")) == criteria
        )
    ]


def add_film(
    film: dict,
    file_path: str | Path = DATA_FILE,
) -> None:
    """Додає новий фільм."""

    films = _load_films(file_path)
    films.append(film)

    _save_films(films, file_path)


def delete_film(
    name: str,
    file_path: str | Path = DATA_FILE,
) -> bool:
    """Видаляє фільм за точною назвою."""

    films = _load_films(file_path)
    target = name.strip().casefold()

    for index, film in enumerate(films):
        if film.get("name", "").casefold() == target:
            films.pop(index)
            _save_films(films, file_path)
            return True

    return False


def edit_film(
    name: str,
    new_description: str,
    file_path: str | Path = DATA_FILE,
) -> bool:
    """Змінює опис фільму."""

    films = _load_films(file_path)
    target = name.strip().casefold()

    for film in films:
        if film.get("name", "").casefold() == target:
            film["description"] = new_description.strip()
            _save_films(films, file_path)
            return True

    return False


def rate_film(
    name: str,
    rating: float,
    file_path: str | Path = DATA_FILE,
) -> bool:
    """Оновлює рейтинг фільму."""

    films = _load_films(file_path)
    target = name.strip().casefold()

    for film in films:
        if film.get("name", "").casefold() == target:
            film["rating"] = rating
            _save_films(films, file_path)
            return True

    return False


def get_recommendation(
    file_path: str | Path = DATA_FILE,
) -> dict | None:
    """Повертає фільм із найвищим рейтингом."""

    films = _load_films(file_path)

    if not films:
        return None

    return max(
        films,
        key=lambda film: float(film.get("rating", 0)),
    )