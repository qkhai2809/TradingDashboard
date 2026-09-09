from Backend.algorithm.industry import (
    find_matching_related_companies
)


def test_find_matching_related_companies():

    outlier = {
        "ticker": "TECH02",
        "industry": "Technology",
    }

    related = [
        {
            "ticker": "TECH02A",
            "name": "Tech Two AI",
            "industry": "Technology",
        },
        {
            "ticker": "TECH02B",
            "name": "Tech Two Cloud",
            "industry": "Technology",
        },
        {
            "ticker": "TECH02C",
            "name": "Tech Two Software",
            "industry": "Technology",
        },
        {
            "ticker": "TECH02D",
            "name": "Tech Two Hardware",
            "industry": "Technology",
        },
        {
            "ticker": "TECH02E",
            "name": "Tech Two Bank",
            "industry": "Banking",
        },
    ]

    matches = find_matching_related_companies(
        outlier,
        related,
    )

    tickers = [
        company["ticker"]
        for company in matches
    ]

    assert tickers == [
        "TECH02A",
        "TECH02B",
        "TECH02C",
        "TECH02D",
    ]

    assert "TECH02E" not in tickers