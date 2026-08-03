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
from unittest.mock import patch

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))

from layer5_competitor_benchmark import (
    select_top_candidates,
    merge_search_candidates,
    shortlist_by_real_likes,
    passes_relevance_filter,
)


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


def viewed(href, views):
    return {"href": href, "view_count": views, "source": "search"}


class MergeSearchCandidatesTests(unittest.TestCase):

    def test_dedup_across_queries_keeps_first_seen(self):
        merged = merge_search_candidates([
            [viewed("/@a/video/1", 100)],
            [viewed("/@a/video/1", 999), viewed("/@b/video/2", 50)],
        ])
        hrefs = [c["href"] for c in merged]
        self.assertEqual(hrefs.count("/@a/video/1"), 1)
        a = next(c for c in merged if c["href"] == "/@a/video/1")
        self.assertEqual(a["view_count"], 100)  # first-seen (query 1's value), not overwritten

    def test_sorted_by_view_count_desc(self):
        merged = merge_search_candidates([[viewed("/@a/video/1", 10), viewed("/@b/video/2", 500)]])
        self.assertEqual([c["href"] for c in merged], ["/@b/video/2", "/@a/video/1"])

    def test_none_view_count_never_coerced_to_zero_and_sorts_last(self):
        merged = merge_search_candidates([[viewed("/@a/video/1", None), viewed("/@b/video/2", 0)]])
        self.assertEqual([c["href"] for c in merged], ["/@b/video/2", "/@a/video/1"])
        a = next(c for c in merged if c["href"] == "/@a/video/1")
        self.assertIsNone(a["view_count"])


class ShortlistByRealLikesTests(unittest.TestCase):
    """Mocks fetch_like_count_and_caption_for_url -- no Playwright/network
    needed. This is the fix for the 2026-08-03 finding that TikTok search
    cards expose a VIEW count, not a like count, in their DOM
    (data-e2e="video-views" is the only engagement number present) -- real
    like_count must come from each candidate's own video page instead."""

    def test_only_top_k_by_view_count_are_fetched(self):
        candidates = [viewed(f"/@x{i}/video/{i}", 100 - i) for i in range(10)]
        with patch("layer5_competitor_benchmark.fetch_like_count_and_caption_for_url",
                   return_value=(5, "some caption")) as mock_fetch:
            result = shortlist_by_real_likes(page=None, candidates=candidates, out_dir=Path("."), top_k=3)
        self.assertEqual(mock_fetch.call_count, 3)
        self.assertEqual(len(result), 3)
        self.assertEqual([c["href"] for c in result], ["/@x0/video/0", "/@x1/video/1", "/@x2/video/2"])

    def test_real_like_count_replaces_view_count_as_the_ranking_field(self):
        candidates = [viewed("/@a/video/1", 9999)]  # huge view count, tiny real like count
        with patch("layer5_competitor_benchmark.fetch_like_count_and_caption_for_url",
                   return_value=(3, "caption")):
            result = shortlist_by_real_likes(page=None, candidates=candidates, out_dir=Path("."), top_k=5)
        self.assertEqual(result[0]["like_count"], 3)
        self.assertEqual(result[0]["view_count_at_search"], 9999)

    def test_unavailable_real_like_count_preserved_as_none_not_zero(self):
        candidates = [viewed("/@a/video/1", 500)]
        with patch("layer5_competitor_benchmark.fetch_like_count_and_caption_for_url",
                   return_value=(None, "caption")):
            result = shortlist_by_real_likes(page=None, candidates=candidates, out_dir=Path("."), top_k=5)
        self.assertIsNone(result[0]["like_count"])

    def test_output_feeds_directly_into_select_top_candidates(self):
        """End-to-end of the two-stage fix: view-ranked candidates ->
        real-like-count shortlist -> final Top-N by real likes."""
        candidates = [viewed(f"/@x{i}/video/{i}", 1000 - i) for i in range(5)]
        real_likes = {"/@x0/video/0": 10, "/@x1/video/1": 900, "/@x2/video/2": 5,
                      "/@x3/video/3": 1, "/@x4/video/4": 2}
        with patch("layer5_competitor_benchmark.fetch_like_count_and_caption_for_url",
                   side_effect=lambda page, url, out_dir, label: (
                       next(v for href, v in real_likes.items() if href.split("/")[-1] in url), "caption")):
            shortlisted = shortlist_by_real_likes(page=None, candidates=candidates, out_dir=Path("."), top_k=5)
        top = select_top_candidates(shortlisted, target=3)
        # /@x1 has the highest REAL like count despite not having the highest view count
        self.assertEqual(top[0]["href"], "/@x1/video/1")

    def test_wrong_category_candidate_excluded_before_frame_extraction(self):
        """The actual 2026-08-03 incident: a seat-cushion video (view_count
        way ahead of the real seat-back-organizer competitors) must be
        dropped by caption BEFORE it could ever reach frame extraction."""
        candidates = [viewed("/@cushion/video/1", 50000), viewed("/@organizer/video/2", 100)]
        captions = {
            "/@cushion/video/1": (50000, "No more back pain no more butt pain #seatcushion #carseatcushion"),
            "/@organizer/video/2": (100, "מארגן גב מושב לרכב עם שולחן מתקפל"),
        }
        with patch("layer5_competitor_benchmark.fetch_like_count_and_caption_for_url",
                   side_effect=lambda page, url, out_dir, label: next(
                       v for href, v in captions.items() if href.split("/")[-1] in url)):
            result = shortlist_by_real_likes(
                page=None, candidates=candidates, out_dir=Path("."), top_k=5,
                include_keywords=["מארגן", "organizer"], exclude_keywords=["cushion", "כרית"],
            )
        hrefs = [c["href"] for c in result]
        self.assertNotIn("/@cushion/video/1", hrefs)
        self.assertIn("/@organizer/video/2", hrefs)


class PassesRelevanceFilterTests(unittest.TestCase):

    def test_no_filters_means_pass(self):
        self.assertTrue(passes_relevance_filter("anything at all", None, None))

    def test_include_keyword_required_when_given(self):
        self.assertTrue(passes_relevance_filter("מארגן לרכב", ["מארגן"], None))
        self.assertFalse(passes_relevance_filter("כרית נוחות", ["מארגן"], None))

    def test_exclude_keyword_overrides_include_match(self):
        # contains both the include keyword AND an exclude keyword -- must be excluded
        self.assertFalse(passes_relevance_filter(
            "seat organizer cushion combo", ["organizer"], ["cushion"]))

    def test_case_insensitive(self):
        self.assertTrue(passes_relevance_filter("ORGANIZER for your car", ["organizer"], None))
        self.assertFalse(passes_relevance_filter("Cozy CUSHION for car seats", None, ["cushion"]))


if __name__ == "__main__":
    unittest.main()
