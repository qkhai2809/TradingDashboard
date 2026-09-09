"""
algorithm/industry.py

So sánh ngành của các công ty liên quan với
ngành của chính công ty ngoại lệ (outlier).

Logic:
    outlier
        ↓
    related companies
        ↓
    related.industry == outlier.industry
        ↓
    matching related companies
"""


from typing import List, Dict, Any


def find_matching_related_companies(
    outlier: Dict[str, Any],
    related_companies: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Tìm các công ty liên quan có cùng ngành với chính outlier.

    Args:
        outlier:
            Thông tin công ty ngoại lệ.
            Bắt buộc có key 'industry'.

        related_companies:
            Danh sách các công ty liên quan.
            Mỗi phần tử cần có key 'industry'.

    Returns:
        Danh sách các công ty liên quan cùng ngành với outlier.
    """

    if not outlier:
        return []

    if not related_companies:
        return []

    outlier_industry = outlier.get("industry")

    if not outlier_industry:
        return []

    matches = [
        company
        for company in related_companies
        if company.get("industry") == outlier_industry
    ]

    return matches