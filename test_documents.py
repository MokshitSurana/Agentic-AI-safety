import unittest

from documents import build_dataset
from agent import is_internal_recipient
from heldout import EXTERNALS


class DatasetTests(unittest.TestCase):
    def test_heldout_structure_and_separation(self):
        cases = build_dataset("heldout-v1")
        self.assertEqual(len(cases), 156)
        self.assertEqual(len({c["id"] for c in cases}), 156)
        self.assertEqual(sum(c["is_attack"] for c in cases), 120)
        controls = [c for c in cases if c["control_type"] == "legitimate_forward"]
        self.assertEqual(len(controls), 24)
        self.assertTrue(all(is_internal_recipient(c["expected_recipient"]) for c in controls))
        self.assertTrue(all(not is_internal_recipient(r) for r in EXTERNALS))
        old = build_dataset("v1") + build_dataset("v2")
        self.assertFalse({c["document"] for c in cases} & {c["document"] for c in old})
        self.assertEqual(cases, build_dataset("heldout-v1"))
        shuffled = build_dataset("heldout-v1", seed=1)
        self.assertNotEqual(cases, shuffled)
        self.assertEqual(sorted(cases, key=lambda c: c["id"]),
                         sorted(shuffled, key=lambda c: c["id"]))

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
