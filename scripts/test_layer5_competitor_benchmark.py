#!/usr/bin/env python3
"""
Regression tests for the --seed-urls `like_count: None` ranking bug fix
(2026-08-03). Pure unit tests over select_top_candidates() -- no Playwright,
no network, no browser session required.

Run: python scripts/test_layer5_competitor_benchmark.py
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from layer5_competitor_benchmark import select_top_candidates


def searched(href, likes):
    return {"href": href, "like_count": likes, "source": "search"}


def seeded(href, likes):
    return {"href": href, "like_count": likes, "source": "seed"}


class SelectTopCandidatesTests(unittest.TestCase):

    def test_seed_with_unavailable_like_count_is_never_excluded(self):
        """The original bug: a seed with like_count=None used to sort as 0
        and lose to every real search result once there were >= target of
        them, dropping known-good competitors from the Top-N entirely."""
        candidates = [seeded("/@good/video/1", None)] + [
            searched(f"/@x{i}/video/{i}", 1000 + i) for i in range(5)
        ]
        top = select_top_candidates(candidates, target=5)
        hrefs = [c["href"] for c in top]
        self.assertIn("/@good/video/1", hrefs)

    def test_seed_with_real_high_like_count_is_retained_and_recorded(self):
        candidates = [seeded("/@yeuunnt.22/video/1", 78300)] + [
            searched(f"/@x{i}/video/{i}", 100) for i in range(4)
        ]
        top = select_top_candidates(candidates, target=5)
        seed = next(c for c in top if c["href"] == "/@yeuunnt.22/video/1")
        self.assertEqual(seed["like_count"], 78300)

    def test_missing_like_count_never_silently_becomes_zero(self):
        """A None must not compare/sort as equal to a genuine 0 -- it must
        never be the reason a seed loses out to a real 0-like competitor,
        and it must be preserved as None (not coerced to 0) in the result."""
        candidates = [seeded("/@good/video/1", None), searched("/@zero/video/2", 0)]
        top = select_top_candidates(candidates, target=1)
        hrefs = [c["href"] for c in top]
        self.assertIn("/@good/video/1", hrefs)
        seed = next(c for c in top if c["href"] == "/@good/video/1")
        self.assertIsNone(seed["like_count"])

    def test_searched_candidates_still_rank_by_like_count_desc(self):
        candidates = [searched("/@a/video/1", 10), searched("/@b/video/2", 500), searched("/@c/video/3", 50)]
        top = select_top_candidates(candidates, target=3)
        self.assertEqual([c["href"] for c in top], ["/@b/video/2", "/@c/video/3", "/@a/video/1"])

    def test_top_n_selection_fills_remaining_slots_from_search_after_seeds(self):
        candidates = [seeded("/@seed1/video/1", 78300), seeded("/@seed2/video/2", None)] + [
            searched(f"/@x{i}/video/{i}", 1000 - i) for i in range(5)
        ]
        top = select_top_candidates(candidates, target=3)
        self.assertEqual(len(top), 3)
        hrefs = [c["href"] for c in top]
        self.assertIn("/@seed1/video/1", hrefs)
        self.assertIn("/@seed2/video/2", hrefs)
        self.assertIn("/@x0/video/0", hrefs)  # best-ranked search result fills the 1 remaining slot

    def test_seeds_beyond_target_are_all_kept_not_truncated(self):
        candidates = [seeded(f"/@seed{i}/video/{i}", 1000 + i) for i in range(3)]
        top = select_top_candidates(candidates, target=2)
        self.assertEqual(len(top), 3)

    def test_dedup_prefers_known_like_count_over_unavailable_for_same_href(self):
        candidates = [seeded("/@x/video/1", None), searched("/@x/video/1", 4200)]
        top = select_top_candidates(candidates, target=1)
        self.assertEqual(len(top), 1)
        self.assertEqual(top[0]["like_count"], 4200)
        self.assertEqual(top[0]["source"], "seed")  # dedup must preserve the seed exemption too

    def test_dedup_keeps_higher_known_value_between_duplicates(self):
        candidates = [searched("/@x/video/1", 100), searched("/@x/video/1", 900)]
        top = select_top_candidates(candidates, target=1)
        self.assertEqual(top[0]["like_count"], 900)

    def test_real_2026_07_02_incident_regression(self):
        """Mirrors the actual session-15 incident: @yeuunnt.22 (78.3K likes)
        and @goussve.km, passed as seeds with an unmeasured like_count, must
        survive a Top-5 selection against 6 search results that all report
        a real (smaller) like_count."""
        candidates = [
            seeded("/@yeuunnt.22/video/1", None),
            seeded("/@goussve.km/video/2", None),
        ] + [searched(f"/@comp{i}/video/{i}", 200 + i * 10) for i in range(6)]
        top = select_top_candidates(candidates, target=5)
        hrefs = [c["href"] for c in top]
        self.assertIn("/@yeuunnt.22/video/1", hrefs)
        self.assertIn("/@goussve.km/video/2", hrefs)


if __name__ == "__main__":
    unittest.main()
