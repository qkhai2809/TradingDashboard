"""
data/fetcher.py

Data adapter cho Phase 1.
Nhận DataFrame chứa dữ liệu thị trường,
trả về Top 10 theo vốn hóa và khối lượng.

Không chứa logic phân tích hay quyết định.
"""

import pandas as pd
from typing import List, Dict, Any


def get_top_by_market_cap(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Lấy Top 10 cổ phiếu có vốn hóa lớn nhất.

    Chuẩn hóa output về format mà frontend sử dụng:
    rank, ticker, company, industry, value
    """

    top10 = (
        df.sort_values("market_cap", ascending=False)
        .head(10)
        .copy()
    )

    top10 = top10.rename(
        columns={
            "name": "company",
            "market_cap": "value",
        }
    )

    return top10[
        ["rank", "ticker", "company", "industry", "value"]
    ].to_dict("records")


def get_top_by_volume(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Lấy Top 10 cổ phiếu có khối lượng giao dịch lớn nhất.

    Chuẩn hóa output về format mà frontend sử dụng:
    rank, ticker, company, industry, value
    """

    top10 = (
        df.sort_values("volume", ascending=False)
        .head(10)
        .copy()
    )

    top10 = top10.rename(
        columns={
            "name": "company",
            "volume": "value",
        }
    )

    return top10[
        ["rank", "ticker", "company", "industry", "value"]
    ].to_dict("records")