"""A predicted share is checked on rows strictly after a cut year.

Rows at or after the cut never enter the same bin as the rows used to
admire the prediction. A call whose largest share is below 0.5 abstains.
"""

from __future__ import annotations

from typing import Mapping

OUTCOMES = ("intended", "bystander", "indel", "unchanged")
BINS = ((0.0, 0.4), (0.4, 0.7), (0.7, 1.01))
ABSTAIN_BELOW = 0.5


class OutcomeError(ValueError):
    """A row is not a distribution, or the cut leaves nothing to score."""


def calibrate(rows: list[Mapping[str, object]], cut_year: int) -> dict[str, object]:
    parsed = [_row(row) for row in rows]
    test = [row for row in parsed if row["year"] >= cut_year]
    train = [row for row in parsed if row["year"] < cut_year]
    if not test or not train:
        raise OutcomeError("the cut must leave both a train side and a test side")
    return {
        "cut_year": cut_year,
        "train_rows": len(train),
        "test_rows": len(test),
        "held_out": _bins(test),
        "leaky_all_rows": _bins(parsed),
        "calls": [
            {
                "id": row["id"],
                "year": row["year"],
                "decision": _decision(row["predicted"]),
                "observed": row["observed"],
            }
            for row in test
        ],
    }


def format_report(report: dict[str, object]) -> str:
    lines = [
        "edit-outcome",
        "",
        f"cut year: {report['cut_year']}",
        f"train rows: {report['train_rows']}",
        f"test rows: {report['test_rows']}",
        "",
        "held-out calibration, predicted intended vs observed:",
    ]
    held = report["held_out"]
    assert isinstance(held, list)
    for bin_row in held:
        assert isinstance(bin_row, dict)
        rate = "n/a" if bin_row["observed_rate"] is None else bin_row["observed_rate"]
        lines.append(f"  {bin_row['bin']}  n={bin_row['n']}  observed {rate}")
    lines.append("")
    lines.append("test calls:")
    calls = report["calls"]
    assert isinstance(calls, list)
    for call in calls:
        assert isinstance(call, dict)
        lines.append(
            f"  {call['id']}  {call['year']}  decision {call['decision']}  observed {call['observed']}"
        )
    lines.append("")
    lines.append("designed rows, not a trained editor")
    return "\n".join(lines)


def _row(row: Mapping[str, object]) -> dict[str, object]:
    year = row.get("year")
    observed = str(row.get("observed", ""))
    predicted = row.get("predicted")
    if isinstance(year, bool) or not isinstance(year, int):
        raise OutcomeError("year must be an integer")
    if observed not in OUTCOMES:
        raise OutcomeError("observed outcome is not one of the four")
    if not isinstance(predicted, dict):
        raise OutcomeError("predicted shares are required")
    shares = {name: float(predicted[name]) for name in OUTCOMES}
    if any(value < 0 for value in shares.values()):
        raise OutcomeError("a share cannot be negative")
    if abs(sum(shares.values()) - 1.0) > 1e-6:
        raise OutcomeError("shares must sum to 1")
    return {
        "id": str(row.get("id", year)),
        "year": year,
        "observed": observed,
        "predicted": shares,
    }


def _bins(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: list[dict[str, object]] = []
    for low, high in BINS:
        chosen = []
        for row in rows:
            predicted = row["predicted"]
            assert isinstance(predicted, dict)
            share = float(predicted["intended"])
            if low <= share < high:
                chosen.append(row["observed"] == "intended")
        rate = None if not chosen else round(sum(chosen) / len(chosen), 3)
        label = f"{low:.1f}-{min(high, 1.0):.1f}"
        grouped.append({"bin": label, "n": len(chosen), "observed_rate": rate})
    return grouped


def _decision(predicted: Mapping[str, float]) -> str:
    top = max(predicted, key=predicted.get)
    if predicted[top] < ABSTAIN_BELOW:
        return "abstain"
    return top
