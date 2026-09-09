"""
algorithm/candidate.py

Tạo danh sách ứng viên từ các công ty liên quan
có cùng ngành với chính outlier.
"""


from typing import List, Dict, Any


def generate_candidates(
    outlier: Dict[str, Any],
    industry_matches: List[Dict[str, Any]],
    detected_from: str
) -> List[Dict[str, Any]]:
    """
    Tạo candidate từ các công ty liên quan đã được xác nhận
    cùng ngành với outlier.

    Industry matching đã được xử lý bởi industry.py.

    Args:
        outlier:
            Công ty ngoại lệ.

        industry_matches:
            Các công ty liên quan đã match industry với outlier.

        detected_from:
            Nguồn phát hiện:
            "Market Cap" hoặc "Trading Volume".

    Returns:
        Danh sách candidate.
    """

    if not outlier:
        return []

    if not industry_matches:
        return []

    outlier_ticker = outlier["ticker"]

    candidates = []

    for company in industry_matches:

        candidate = {
            "ticker": company["ticker"],
            "industry": company["industry"],
            "detected_from": detected_from,
            "reason": f"Related to {outlier_ticker}",
            "status": "Potential candidate",
        }

        candidates.append(candidate)

    return candidates