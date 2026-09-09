import pandas as pd

from Backend.algorithm.pipeline import (
    run_pipeline
)


def test_pipeline():

    market_cap_df = pd.DataFrame([
        {
            "rank": 1,
            "ticker": "BANK01",
            "name": "Bank One",
            "industry": "Banking",
            "market_cap": 1000,
        },
        {
            "rank": 2,
            "ticker": "BANK02",
            "name": "Bank Two",
            "industry": "Banking",
            "market_cap": 900,
        },
        {
            "rank": 3,
            "ticker": "BANK03",
            "name": "Bank Three",
            "industry": "Banking",
            "market_cap": 800,
        },
        {
            "rank": 4,
            "ticker": "BANK04",
            "name": "Bank Four",
            "industry": "Banking",
            "market_cap": 700,
        },
        {
            "rank": 5,
            "ticker": "BANK05",
            "name": "Bank Five",
            "industry": "Banking",
            "market_cap": 600,
        },
        {
            "rank": 6,
            "ticker": "BANK06",
            "name": "Bank Six",
            "industry": "Banking",
            "market_cap": 500,
        },
        {
            "rank": 7,
            "ticker": "BANK07",
            "name": "Bank Seven",
            "industry": "Banking",
            "market_cap": 400,
        },
        {
            "rank": 8,
            "ticker": "BANK08",
            "name": "Bank Eight",
            "industry": "Banking",
            "market_cap": 300,
        },
        {
            "rank": 9,
            "ticker": "TECH02",
            "name": "Tech Two",
            "industry": "Technology",
            "market_cap": 200,
        },
        {
            "rank": 10,
            "ticker": "TECH03",
            "name": "Tech Three",
            "industry": "Technology",
            "market_cap": 100,
        },
    ])

    volume_df = pd.DataFrame([
        {
            "rank": 1,
            "ticker": "BANK01",
            "name": "Bank One",
            "industry": "Banking",
            "volume": 1000,
        },
        {
            "rank": 2,
            "ticker": "BANK02",
            "name": "Bank Two",
            "industry": "Banking",
            "volume": 900,
        },
        {
            "rank": 3,
            "ticker": "BANK03",
            "name": "Bank Three",
            "industry": "Banking",
            "volume": 800,
        },
        {
            "rank": 4,
            "ticker": "BANK04",
            "name": "Bank Four",
            "industry": "Banking",
            "volume": 700,
        },
        {
            "rank": 5,
            "ticker": "BANK05",
            "name": "Bank Five",
            "industry": "Banking",
            "volume": 600,
        },
        {
            "rank": 6,
            "ticker": "BANK06",
            "name": "Bank Six",
            "industry": "Banking",
            "volume": 500,
        },
        {
            "rank": 7,
            "ticker": "BANK07",
            "name": "Bank Seven",
            "industry": "Banking",
            "volume": 400,
        },
        {
            "rank": 8,
            "ticker": "BANK08",
            "name": "Bank Eight",
            "industry": "Banking",
            "volume": 300,
        },
        {
            "rank": 9,
            "ticker": "BANK09",
            "name": "Bank Nine",
            "industry": "Banking",
            "volume": 200,
        },
        {
            "rank": 10,
            "ticker": "TECH02",
            "name": "Tech Two",
            "industry": "Technology",
            "volume": 100,
        },
    ])

    result = run_pipeline(
        market_cap_df,
        volume_df,
    )

    assert "market_cap" in result
    assert "trading_volume" in result
    assert "candidates" in result
    assert "positions" in result

    assert result["market_cap"]["dominantIndustry"] == "Banking"
    assert result["trading_volume"]["dominantIndustry"] == "Banking"

    assert result["trading_volume"]["outliers"][0]["ticker"] == "TECH02"

    assert len(result["trading_volume"]["industry_comparison"]["TECH02"]["matches"]) == 2

    match_tickers = {
        item["ticker"]
        for item in result["trading_volume"]["industry_comparison"]["TECH02"]["matches"]
    }

    assert match_tickers == {
        "TECH02B",
        "TECH02C",
    }