"""
data/corporate.py

Mock data cho quan hệ doanh nghiệp từ file CSV.
Load dữ liệu một lần khi import module.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

# Đường dẫn đến file CSV
CSV_PATH = (
    Path(__file__).parent.parent.parent
    / "sample_data"
    / "corporate"
    / "related_companies.csv"
)

# Kiểm tra file tồn tại
if not CSV_PATH.exists():
    raise FileNotFoundError(
        f"Không tìm thấy file dữ liệu corporate tại: {CSV_PATH}\n"
        "Hãy đảm bảo sample_data/corporate/related_companies.csv tồn tại."
    )

# Đọc CSV một lần khi import module
_df = pd.read_csv(CSV_PATH)

# Mapping từ parent_ticker → list các công ty liên quan
_RELATED: Dict[str, List[Dict[str, Any]]] = {}

for parent, group in _df.groupby("parent_ticker"):
    _RELATED[parent] = group[
        ["related_ticker", "related_name", "related_industry"]
    ].rename(
        columns={
            "related_ticker": "ticker",
            "related_name": "company",
            "related_industry": "industry",
        }
    ).to_dict("records")


def get_related_companies(ticker: str) -> List[Dict[str, Any]]:
    """
    Lấy danh sách công ty liên quan của một ticker.

    Returns:
        List[Dict]: Mỗi công ty có:
            - ticker
            - company
            - industry
    """

    return _RELATED.get(ticker, [])