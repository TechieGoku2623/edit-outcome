"""A sharp training share is not treated as earned on later rows."""

from __future__ import annotations

import unittest

from edit_outcome import OutcomeError, calibrate
from edit_outcome.__main__ import ROWS


class CalibrateTests(unittest.TestCase):
    def test_held_out_high_bin_is_not_the_training_story(self) -> None:
        report = calibrate(ROWS, 2022)
        self.assertEqual(report["train_rows"], 3)
        self.assertEqual(report["test_rows"], 3)
        held = report["held_out"]
        assert isinstance(held, list)
        high = held[-1]
        assert isinstance(high, dict)
        self.assertEqual(high["n"], 2)
        self.assertEqual(high["observed_rate"], 0.0)

    def test_low_confidence_call_abstains(self) -> None:
        report = calibrate(ROWS, 2022)
        calls = report["calls"]
        assert isinstance(calls, list)
        faint = next(call for call in calls if call["id"] == "f")
        assert isinstance(faint, dict)
        self.assertEqual(faint["decision"], "abstain")

    def test_shares_that_do_not_sum_raise(self) -> None:
        bad = {
            "id": "z",
            "year": 2020,
            "observed": "intended",
            "predicted": {"intended": 0.5, "bystander": 0.5, "indel": 0.5, "unchanged": 0.5},
        }
        with self.assertRaises(OutcomeError):
            calibrate([bad, ROWS[0], ROWS[3]], 2022)

    def test_cut_with_no_future_raises(self) -> None:
        with self.assertRaises(OutcomeError):
            calibrate(ROWS, 2030)


if __name__ == "__main__":
    unittest.main()
