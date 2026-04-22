import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from country_registry import get_country_config, list_exposed_countries, list_exposed_public_countries


class PublicSurfaceContractTests(unittest.TestCase):
    def test_single_country_registry(self):
        countries = list_exposed_countries(["sweden"], allow_internal=False)
        self.assertEqual(len(countries), 1)
        self.assertEqual(countries[0].country_id, "sweden")

    def test_public_visibility_flag(self):
        countries = list_exposed_public_countries()
        self.assertEqual(len(countries), 1)

    def test_country_config_matches_public_surface(self):
        config = get_country_config("sweden")
        self.assertEqual(config.display_name, "Sweden")
        self.assertEqual(config.adjective, "Swedish")
        self.assertEqual(len(config.supported_factors), 9)
        self.assertEqual(bool(config.national_vote_path), True)

    def test_public_wrapper_defaults(self):
        wrapper = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")
        self.assertIn('WPD_APP_TITLE", "Swedish Politics Data"', wrapper)
        self.assertIn('WPD_EXPOSE_COUNTRIES", "sweden"', wrapper)

    def test_runtime_helper_modules_exist(self):
        root = Path(__file__).resolve().parents[1]
        for filename in ("app_data_variants.py", "app_failure_states.py"):
            path = root / filename
            self.assertTrue(path.exists(), filename)
            compile(path.read_text(encoding="utf-8"), str(path), "exec")


if __name__ == "__main__":
    unittest.main()
