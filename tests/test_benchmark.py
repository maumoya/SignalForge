import unittest
from scripts.benchmark import fixture, benchmark
class BenchmarkTests(unittest.TestCase):
    def test_generated_records_are_deterministic(self):
        data=fixture(60)
        self.assertEqual(len(data),60)
        self.assertEqual(data[0]["creator"],"generated-creator-0")
        self.assertEqual(data[59]["creator"],"generated-creator-1")
    def test_units_and_coverage(self):
        result=benchmark(60,60,3)
        self.assertEqual(result["hypothetical_total_playback_hours"],1)
        self.assertEqual(result["generated_records"],60)
        self.assertEqual(result["records_with_baseline"],60)
        self.assertIn("not hours of information understood",result["limitations"][1])
if __name__=="__main__":unittest.main()
