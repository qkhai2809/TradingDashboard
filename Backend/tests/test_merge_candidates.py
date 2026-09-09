"""
tests/test_merge_candidates.py

Test merge candidate trùng ticker
được phát hiện từ nhiều nguồn.
"""

from Backend.algorithm.pipeline import _merge_candidates


def test_merge_candidates_from_multiple_sources():
    candidates = [
        {
            "ticker": "TECH02A",
            "industry": "Banking",
            "detected_from": "Market Cap",
            "reason": "Related to TECH05",
            "status": "Potential candidate",
        },
        {
            "ticker": "TECH02A",
            "industry": "Banking",
            "detected_from": "Trading Volume",
            "reason": "Related to TECH02",
            "status": "Potential candidate",
        },
    ]

    result = _merge_candidates(candidates)

    assert result == [
        {
            "ticker": "TECH02A",
            "industry": "Banking",
            "detected_from": "Market Cap + Trading Volume",
            "reason": "Related to TECH05; Related to TECH02",
            "status": "Potential candidate",
        }
    ]