from pathlib import Path

import pandas as pd

from Backend.algorithm.pipeline import run_pipeline


def test_pipeline_candidate_from_trading_volume():

    base_dir = Path(__file__).resolve().parents[2]

    market_cap_path = (
        base_dir
        / "sample_data"
        / "market_cap"
        / "2026-01-01.csv"
    )

    volume_path = (
        base_dir
        / "sample_data"
        / "trading_volume"
        / "2026-01-01.csv"
    )

    market_cap_df = pd.read_csv(
        market_cap_path
    )

    volume_df = pd.read_csv(
        volume_path
    )

    result = run_pipeline(
        market_cap_df,
        volume_df,
    )

    matches = (
        result["trading_volume"]
        ["industry_comparison"]
        ["TECH02"]
        ["matches"]
    )

    match_tickers = {
        item["ticker"]
        for item in matches
    }

    assert match_tickers == {
        "TECH02B",
        "TECH02C",
    }

    candidates = result["candidates"]

    candidate_tickers = {
        candidate["ticker"]
        for candidate in candidates
    }

    assert {
        "TECH02B",
        "TECH02C",
    }.issubset(candidate_tickers)

    for candidate in candidates:

        if candidate["ticker"] in {
            "TECH02B",
            "TECH02C",
        }:

            assert candidate["industry"] == "Technology"

            assert candidate["detected_from"] == (
                "Trading Volume"
            )

            assert candidate["reason"] == (
                "Related to TECH02"
            )

            assert candidate["status"] == (
                "Potential candidate"
            )