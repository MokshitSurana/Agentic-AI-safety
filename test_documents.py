import unittest

from documents import build_dataset


class DatasetTests(unittest.TestCase):
    def test_dataset_has_attack_benign_and_legitimate_forward_cases(self):
        dataset = build_dataset("v2")
        counts = {
            kind: sum(case["control_type"] == kind for case in dataset)
            for kind in ("attack", "benign", "legitimate_forward")
        }
        self.assertEqual(counts, {"attack": 40, "benign": 8, "legitimate_forward": 3})

    def test_legitimate_forward_controls_have_expected_recipients(self):
        controls = [
            case for case in build_dataset("v2")
            if case["control_type"] == "legitimate_forward"
        ]
        self.assertTrue(all(case["expected_recipient"] for case in controls))


if __name__ == "__main__":
    unittest.main()
