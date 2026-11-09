import unittest

from data import filter_films, find_films, get_films
from models import Film


class TestMovies(unittest.TestCase):
    """Тести для перевірки роботи фільмів."""

    def test_films_are_loaded(self):
        """Перевіряє, що JSON повертає список."""

        films = get_films()

        self.assertIsInstance(films, list)

    def test_film_structure(self):
        """Перевіряє структуру фільму."""

        films = get_films()

        for film in films:
            movie = Film(**film)

            self.assertTrue(movie.name)
            self.assertTrue(movie.description)
            self.assertTrue(movie.genre)
            self.assertTrue(movie.actors)
            self.assertTrue(movie.poster)

    def test_poster_url(self):
        """Перевіряє посилання на постер."""

        films = get_films()

        for film in films:
            poster = film["poster"]

            self.assertTrue(
                poster.startswith(("http://", "https://"))
            )

    def test_search(self):
        """Перевіряє пошук за назвою."""

        results = find_films("аватар")

        self.assertGreaterEqual(len(results), 1)

    def test_filter_by_genre(self):
        """Перевіряє фільтрацію за жанром."""

        results = filter_films("фантастика")

        self.assertTrue(
            all(
                "фантастика" in film["genre"].casefold()
                for film in results
            )
        )

    def test_filter_by_year(self):
        """Перевіряє фільтрацію за роком."""

        results = filter_films("2009")

        self.assertTrue(
            all(film["year"] == 2009 for film in results)
        )


if __name__ == "__main__":
    unittest.main()