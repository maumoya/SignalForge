"""The published numbers must match the measured results file, digit for digit."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = sorted((ROOT / "docs").glob("real-benchmark-*.json"))[-1]


def n(x):
    return f"{round(x):,}"


class PublishedResultsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(RESULTS.read_text(encoding="utf-8"))

    def test_results_come_from_real_public_metadata(self):
        r = self.r
        self.assertEqual(r["benchmark_type"], "real-public-metadata")
        self.assertGreaterEqual(r["videos_collected"], 1000)
        self.assertGreaterEqual(r["channels_with_videos"], 10)
        self.assertEqual(sum(c["videos"] for c in r["per_channel"]), r["videos_collected"])

    def test_ratio_is_the_arithmetic_of_the_measured_times(self):
        r = self.r
        total = r["collect_seconds"] + r["analyze_median_seconds"] + r["rules_seconds"]
        self.assertAlmostEqual(total, r["skill_total_seconds"], delta=0.2)
        ratio = r["watch_hours_once_each"] * 3600 / r["skill_total_seconds"]
        self.assertAlmostEqual(ratio / r["watch_time_over_skill_time"], 1.0, delta=0.002)

    def test_readme_and_cards_show_the_measured_numbers(self):
        r = self.r
        wanted = [n(r["videos_collected"]), n(r["watch_hours_once_each"]), n(r["skill_total_seconds"]), n(r["watch_time_over_skill_time"])]
        for name in ("README.md", "assets/demo.svg", "assets/bench-card.svg"):
            text = (ROOT / name).read_text(encoding="utf-8")
            for value in wanted:
                self.assertIn(value, text, f"{name} does not show {value}")

    def test_no_raw_records_are_published(self):
        self.assertNotIn("items", self.r)
        self.assertFalse(any((ROOT / "benchmarks").glob("*.jsonl")))


if __name__ == "__main__":
    unittest.main()
