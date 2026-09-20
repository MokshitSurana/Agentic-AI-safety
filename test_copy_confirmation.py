import unittest
from prepare_copy_confirmation import fresh_cases
from copy_confirmation_stats import paired, wilson, holm
from migration_pilot import make_cases


class ConfirmationTests(unittest.TestCase):
    def test_new_cases_balanced_and_secret_absent(self):
        cases = fresh_cases()
        self.assertEqual(len(cases), 40)
        self.assertEqual(len({c["workflow_id"] for c in cases}), 20)
        self.assertEqual(len({c["family"] for c in cases}), 5)
        old = make_cases()
        self.assertFalse({c["ticket"] for c in cases} & {c["ticket"] for c in old})
        self.assertFalse({c["private_token"] for c in cases} & {c["private_token"] for c in old})
        for case in cases:
            self.assertNotIn(case["private_token"], case["ticket"])
        self.assertEqual(cases, fresh_cases())

    def test_paired_exact_known_discordance(self):
        result = paired([1]*13+[0]*2, [0]*13+[1]*2)
        self.assertAlmostEqual(result["mcnemar_exact_p"], 242/32768)
        self.assertAlmostEqual(result["risk_difference"], -11/15)

    def test_empty_and_constant(self):
        self.assertIsNone(paired([], [])["risk_difference"])
        self.assertTrue(paired([0]*20, [0]*20)["constant_differences"])
        self.assertIsNone(wilson(0, 0))
        self.assertGreater(wilson(0, 20)[1], 0)
        self.assertLess(wilson(20, 20)[0], 1)

    def test_holm_and_bad_counts(self):
        self.assertEqual(holm([0.01, 0.03]), [0.02, 0.03])
        with self.assertRaises(ValueError):
            wilson(2, 1)
        with self.assertRaises(ValueError):
            paired([1], [])


if __name__ == "__main__":
    unittest.main()
