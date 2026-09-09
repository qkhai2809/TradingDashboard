from Backend.algorithm.outlier_detector import detect_outliers


def test_detect_outliers():
    top10 = [
        {"ticker": "A", "industry": "Banking"},
        {"ticker": "B", "industry": "Banking"},
        {"ticker": "C", "industry": "Banking"},
        {"ticker": "D", "industry": "Banking"},
        {"ticker": "E", "industry": "Banking"},
        {"ticker": "F", "industry": "Banking"},
        {"ticker": "G", "industry": "Banking"},
        {"ticker": "H", "industry": "Banking"},
        {"ticker": "I", "industry": "Technology"},
        {"ticker": "J", "industry": "Insurance"},
    ]

    result = detect_outliers(top10)

    assert result["dominant_industry"] == "Banking"
    assert result["dominant_count"] == 8

    outlier_tickers = [item["ticker"] for item in result["outliers"]]

    assert outlier_tickers == ["I", "J"]