from Backend.algorithm.candidate import (
    generate_candidates
)


def test_generate_candidates():

    outlier = {
        "ticker": "TECH02",
        "industry": "Technology",
    }

    industry_matches = [
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
    ]

    candidates = generate_candidates(
        outlier,
        industry_matches,
        "Trading Volume",
    )

    assert len(candidates) == 2

    assert candidates[0] == {
        "ticker": "TECH02A",
        "industry": "Technology",
        "detected_from": "Trading Volume",
        "reason": "Related to TECH02",
        "status": "Potential candidate",
    }

    assert candidates[1] == {
        "ticker": "TECH02B",
        "industry": "Technology",
        "detected_from": "Trading Volume",
        "reason": "Related to TECH02",
        "status": "Potential candidate",
    }