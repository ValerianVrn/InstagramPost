import unittest

from scripts import post


class PostCountryHistoryTests(unittest.TestCase):
    def test_get_visited_countries_deduplicates_and_keeps_current(self):
        state = {
            "country": "France",
            "visited": ["Portugal", "Spain", "Portugal"],
        }

        visited = post.get_visited_countries(state, current_country="France")

        self.assertEqual(visited, ["Portugal", "Spain", "France"])


if __name__ == "__main__":
    unittest.main()
