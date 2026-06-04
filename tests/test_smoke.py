import unittest

from run_all_smoke_tests import run_smoke_tests


class SmokeRunnerTests(unittest.TestCase):
    def test_smoke_tests_pass(self):
        results = run_smoke_tests()

        self.assertTrue(all(result["passed"] for result in results))


if __name__ == "__main__":
    unittest.main()
