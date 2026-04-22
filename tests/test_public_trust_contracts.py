import sys
from pathlib import Path
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.correlation import compute_correlation_result, rank_correlation_results
from country_registry import get_country_config


ROOT = Path(__file__).resolve().parents[1]


class PublicTrustContractTests(unittest.TestCase):
    def test_correlation_correctness_on_synthetic_dataset(self):
        frame = pd.DataFrame(
            {
                "share": [100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
                "metric": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            }
        )
        result = compute_correlation_result(frame, factor="Synthetic", party="P", year=2022, mode="test")
        self.assertTrue(result["valid"])
        self.assertEqual(result["n"], 10)
        self.assertEqual(result["r"], -1.0)

    def test_ranking_uses_absolute_correlation_strength(self):
        ranked = rank_correlation_results(
            [
                {"label": "weak positive", "r": 0.31},
                {"label": "strong negative", "r": -0.72},
                {"label": "moderate positive", "r": 0.55},
            ]
        )
        self.assertEqual([item["label"] for item in ranked], ["strong negative", "moderate positive", "weak positive"])

    def test_public_factor_scope_matches_files_and_excludes_internal_candidates(self):
        config = get_country_config("sweden")
        catalog = {item["key"]: item for item in config.factor_catalog()}
        self.assertEqual(set(config.supported_factors), set(catalog))
        for item in catalog.values():
            self.assertTrue((config.factor_dir / item["filename"]).exists(), item["filename"])
        self.assertNotIn("welfare", config.supported_factors)
        self.assertNotIn("commute", config.supported_factors)

    def test_public_contract_docs_keep_guardrails_visible(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        methodology = (ROOT / "METHODOLOGY.md").read_text(encoding="utf-8")
        guide = (ROOT / "HOW_TO_READ_RESULTS.md").read_text(encoding="utf-8")
        self.assertIn("Correlation is not causation", readme)
        self.assertIn("Riksdag-only", readme)
        self.assertIn("ecological fallacy", methodology)
        self.assertIn("pattern -> check -> context -> cautious sentence", guide)


if __name__ == "__main__":
    unittest.main()
