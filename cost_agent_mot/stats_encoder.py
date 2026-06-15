"""Build image-free sequence cards from original and HRTI detector statistics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .io_utils import read_csv_rows, to_float, to_int, write_csv_rows, write_jsonl
from .schemas import SEQUENCE_CARD_FIELDS


def _index_rows(path: str | Path, seq_col: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in read_csv_rows(path):
        seq = row[seq_col]
        rec: dict[str, Any] = {"sequence": seq}
        for key, value in row.items():
            if key == seq_col:
                continue
            rec[key] = value if key == "split" else to_float(value)
        indexed[seq] = rec
    return indexed


def _normalize(cards: list[dict[str, Any]], key: str) -> None:
    vals = [to_float(card.get(key)) for card in cards]
    if not vals:
        return
    lo, hi = min(vals), max(vals)
    out_key = key + "_norm"
    for card in cards:
        card[out_key] = 0.0 if hi == lo else (to_float(card.get(key)) - lo) / (hi - lo)


def build_sequence_cards(
    original_stats: str | Path,
    enhanced_stats: str | Path,
    *,
    original_seq_col: str = "seq",
    enhanced_seq_col: str = "sequence",
) -> list[dict[str, Any]]:
    """Return one structured sequence card per sequence.

    The card contains detector-statistics cues only. It contains no images,
    image crops, tensors, ground-truth labels, or tracking metrics.
    """
    orig = _index_rows(original_stats, original_seq_col)
    hrti = _index_rows(enhanced_stats, enhanced_seq_col)
    seqs = sorted(set(orig) & set(hrti))
    cards: list[dict[str, Any]] = []

    for seq in seqs:
        o = orig[seq]
        h = hrti[seq]
        frames = to_int(o.get("frames"), 0)
        orig_count = to_float(o.get("det_count"))
        hrti_count = to_float(h.get("det_count"))
        orig_mean = to_float(o.get("mean_det_per_frame"))
        hrti_mean = to_float(h.get("mean_det_per_frame"))
        orig_low = to_float(o.get("score_lt_020_frac"))
        hrti_low = to_float(h.get("score_lt_020_frac"))
        det_ratio = hrti_count / max(orig_count, 1.0)
        det_delta_frac = (hrti_count - orig_count) / max(orig_count, 1.0)
        volatility = to_float(o.get("std_det_per_frame")) / max(orig_mean, 1.0)
        class_mix = 1.0 - to_float(o.get("class_dominance"), 1.0)
        density_extreme = 1.0 if orig_mean >= 35.0 else (0.75 if orig_mean < 5.5 else 0.25)
        stream_disagreement = abs(det_delta_frac) + abs(hrti_low - orig_low)

        base_card_score = (
            2.0 * max(det_delta_frac, 0.0)
            + 1.2 * stream_disagreement
            + 0.9 * orig_low
            + 0.6 * volatility
            + 0.4 * class_mix
            + 0.5 * density_extreme
        )
        uncertainty_score = 1.2 * orig_low + 0.8 * volatility + 0.5 * class_mix + 0.2 * density_extreme

        cards.append(
            {
                "sequence": seq,
                "frames": frames,
                "orig": o,
                "hrti": h,
                "orig_det_count": orig_count,
                "hrti_det_count": hrti_count,
                "orig_mean_det_per_frame": orig_mean,
                "hrti_mean_det_per_frame": hrti_mean,
                "orig_mean_score": to_float(o.get("mean_score")),
                "hrti_mean_score": to_float(h.get("mean_score")),
                "orig_low_score_frac": orig_low,
                "hrti_low_score_frac": hrti_low,
                "det_ratio": det_ratio,
                "det_delta_frac": det_delta_frac,
                "low_score_delta": hrti_low - orig_low,
                "volatility": volatility,
                "class_mix": class_mix,
                "density_extreme": density_extreme,
                "density_score": orig_mean,
                "uncertainty_score": uncertainty_score,
                "delta_score": det_delta_frac,
                "base_card_score": base_card_score,
                "split": str(o.get("split", "")),
            }
        )

    for key in ["density_score", "uncertainty_score", "delta_score", "base_card_score"]:
        _normalize(cards, key)
    for card in cards:
        card["cost_agent_score"] = (
            0.72 * card["density_score_norm"]
            + 0.16 * card["uncertainty_score_norm"]
            + 0.08 * card["delta_score_norm"]
            + 0.04 * card["base_card_score_norm"]
        )
    return cards


def flatten_card(card: dict[str, Any]) -> dict[str, Any]:
    return {field: card.get(field, "") for field in SEQUENCE_CARD_FIELDS}


def write_sequence_cards(
    cards: list[dict[str, Any]],
    csv_path: str | Path,
    jsonl_path: str | Path | None = None,
) -> None:
    write_csv_rows(csv_path, [flatten_card(card) for card in cards], SEQUENCE_CARD_FIELDS)
    if jsonl_path is not None:
        trace_rows = []
        for card in cards:
            row = flatten_card(card)
            row["orig"] = card.get("orig", {})
            row["hrti"] = card.get("hrti", {})
            trace_rows.append(row)
        write_jsonl(jsonl_path, trace_rows)

