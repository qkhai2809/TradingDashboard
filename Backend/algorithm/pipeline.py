"""
algorithm/pipeline.py

Orchestrator cho toàn bộ Phase 1.

Hai nguồn dữ liệu:
    - Market Cap
    - Trading Volume

Hai nguồn được phân tích độc lập.

Logic:
    1. Lấy Top 10
    2. Phát hiện dominant industry
    3. Phát hiện outlier
    4. Lấy related companies của outlier
    5. So sánh industry của related company
       với industry của chính outlier
    6. Tạo candidate
    7. Merge candidate giữa các nguồn
"""


from typing import Dict, Any, List

import pandas as pd

from ..data.fetcher import (
    get_top_by_market_cap,
    get_top_by_volume,
)

from ..data.corporate import (
    get_related_companies,
)

from ..algorithm.outlier_detector import (
    detect_outliers,
)

from ..algorithm.industry import (
    find_matching_related_companies,
)

from ..algorithm.candidate import (
    generate_candidates,
)


def _merge_candidates(
    candidates_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Gộp candidate trùng ticker từ nhiều nguồn.

    Nếu candidate xuất hiện ở cả Market Cap
    và Trading Volume:

        detected_from:
            Market Cap + Trading Volume

        reason:
            gộp các lý do.

    Status giữ nguyên:
        Potential candidate
    """

    merged = {}

    for candidate in candidates_list:

        ticker = candidate["ticker"]

        if ticker not in merged:
            merged[ticker] = candidate.copy()
            continue

        old_sources = merged[ticker]["detected_from"]
        new_source = candidate["detected_from"]

        if (
            old_sources != new_source
            and new_source not in old_sources
        ):
            merged[ticker]["detected_from"] = (
                f"{old_sources} + {new_source}"
            )

        old_reason = merged[ticker]["reason"]
        new_reason = candidate["reason"]

        if (
            old_reason != new_reason
            and new_reason not in old_reason
        ):
            merged[ticker]["reason"] = (
                f"{old_reason}; {new_reason}"
            )

    return list(merged.values())


def _build_industry_comparison(
    outliers: List[Dict[str, Any]],
    candidates_map: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Dict[str, Any]]:
    """
    Tạo kết quả industry_comparison cho frontend.

    Chỉ lấy những company đã match ngành
    và đã trở thành candidate.
    """

    industry_comparison = {}

    for outlier in outliers:

        ticker = outlier["ticker"]

        candidates = candidates_map.get(
            ticker,
            []
        )

        matches = [
            {
                "ticker": candidate["ticker"],
                "industry": candidate["industry"],
                "status": candidate["status"],
            }
            for candidate in candidates
        ]

        industry_comparison[ticker] = {
            "matches": matches
        }

    return industry_comparison


def _analyze_market_cap(
    market_cap_df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Phân tích độc lập nguồn Market Cap.
    """

    top_cap = get_top_by_market_cap(
        market_cap_df
    )

    cap_result = detect_outliers(
        top_cap
    )

    cap_dominant = cap_result[
        "dominant_industry"
    ]

    cap_dominant_count = cap_result[
        "dominant_count"
    ]

    cap_outliers = cap_result[
        "outliers"
    ]

    cap_related = {}

    cap_candidates = []

    cap_candidates_map = {}

    for outlier in cap_outliers:

        ticker = outlier["ticker"]

        # --------------------------------------
        # 1. Lấy công ty liên quan của OUTLIER
        # --------------------------------------

        related = get_related_companies(
            ticker
        )

        cap_related[ticker] = related

        # --------------------------------------
        # 2. So sánh industry với CHÍNH OUTLIER
        # --------------------------------------

        matches = find_matching_related_companies(
            outlier,
            related,
        )

        # --------------------------------------
        # 3. Tạo candidate
        # --------------------------------------

        candidates = generate_candidates(
            outlier,
            matches,
            "Market Cap",
        )

        cap_candidates.extend(
            candidates
        )

        cap_candidates_map[ticker] = (
            candidates
        )

    cap_industry_comparison = (
        _build_industry_comparison(
            cap_outliers,
            cap_candidates_map,
        )
    )

    return {
        "label": "VỐN HÓA",

        "unit": "Vốn hóa (tỷ VND)",

        "top10": top_cap,

        "dominantIndustry": (
            cap_dominant
            if cap_dominant
            else ""
        ),

        "dominantCount": (
            cap_dominant_count
        ),

        "outliers": cap_outliers,

        "related": cap_related,

        "industry_comparison":
            cap_industry_comparison,

        "candidates": cap_candidates,
    }


def _analyze_trading_volume(
    volume_df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Phân tích độc lập nguồn Trading Volume.
    """

    top_volume = get_top_by_volume(
        volume_df
    )

    volume_result = detect_outliers(
        top_volume
    )

    volume_dominant = volume_result[
        "dominant_industry"
    ]

    volume_dominant_count = volume_result[
        "dominant_count"
    ]

    volume_outliers = volume_result[
        "outliers"
    ]

    volume_related = {}

    volume_candidates = []

    volume_candidates_map = {}

    for outlier in volume_outliers:

        ticker = outlier["ticker"]

        # --------------------------------------
        # 1. Lấy công ty liên quan của OUTLIER
        # --------------------------------------

        related = get_related_companies(
            ticker
        )

        volume_related[ticker] = related

        # --------------------------------------
        # 2. So sánh industry với CHÍNH OUTLIER
        # --------------------------------------

        matches = find_matching_related_companies(
            outlier,
            related,
        )

        # --------------------------------------
        # 3. Tạo candidate
        # --------------------------------------

        candidates = generate_candidates(
            outlier,
            matches,
            "Trading Volume",
        )

        volume_candidates.extend(
            candidates
        )

        volume_candidates_map[ticker] = (
            candidates
        )

    volume_industry_comparison = (
        _build_industry_comparison(
            volume_outliers,
            volume_candidates_map,
        )
    )

    return {
        "label": "KHỐI LƯỢNG GIAO DỊCH",

        "unit": "Khối lượng (triệu CP)",

        "top10": top_volume,

        "dominantIndustry": (
            volume_dominant
            if volume_dominant
            else ""
        ),

        "dominantCount": (
            volume_dominant_count
        ),

        "outliers": volume_outliers,

        "related": volume_related,

        "industry_comparison":
            volume_industry_comparison,

        "candidates": volume_candidates,
    }


def run_pipeline(
    market_cap_df: pd.DataFrame,
    volume_df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Chạy toàn bộ Phase 1.

    Market Cap và Trading Volume
    được phân tích độc lập.

    Candidate chỉ được merge
    ở bước cuối.
    """

    # ==========================================
    # 1. MARKET CAP
    # ==========================================

    market_cap_result = _analyze_market_cap(
        market_cap_df
    )

    # ==========================================
    # 2. TRADING VOLUME
    # ==========================================

    volume_result = _analyze_trading_volume(
        volume_df
    )

    # ==========================================
    # 3. MERGE CANDIDATES
    # ==========================================

    all_candidates = (
        market_cap_result["candidates"]
        + volume_result["candidates"]
    )

    merged_candidates = _merge_candidates(
        all_candidates
    )

    # ==========================================
    # 4. POSITIONS
    # ==========================================

    positions = [
        {
            "ticker": "TPB",
            "entry": 20.0,
            "target": 26.0,
            "current": 24.5,
        },
        {
            "ticker": "BVB",
            "entry": 15.0,
            "target": 19.5,
            "current": 19.8,
        },
    ]

    # ==========================================
    # 5. FINAL RESULT
    # ==========================================

    return {
        "market_cap": {
            key: value
            for key, value
            in market_cap_result.items()
            if key != "candidates"
        },

        "trading_volume": {
            key: value
            for key, value
            in volume_result.items()
            if key != "candidates"
        },

        "candidates": merged_candidates,

        "positions": positions,
    }