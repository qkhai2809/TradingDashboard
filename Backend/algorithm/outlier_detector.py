"""
algorithm/outlier_detector.py

Phát hiện outlier trong Top N dựa trên phân phối ngành.
"""

from typing import List, Dict, Any
from collections import Counter

# Import cấu hình từ config (đường dẫn tương đối)
from ..config.settings import MIN_DOMINANT_COUNT, MIN_DOMINANT_RATIO


def detect_outliers(top_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Xác định ngành chiếm ưu thế và outlier trong danh sách Top N.

    Args:
        top_list (List[Dict]): Danh sách các cổ phiếu trong Top N.
            Mỗi phần tử phải là dict chứa ít nhất key 'industry'.

    Returns:
        Dict: {
            'dominant_industry': str | None,
            'dominant_count': int,
            'outliers': List[Dict]
        }
    """
    if not top_list:
        return {
            'dominant_industry': None,
            'dominant_count': 0,
            'outliers': []
        }

    # 1. Đếm số lượng cổ phiếu theo ngành
    industry_counts = Counter(item['industry'] for item in top_list)
    total = len(top_list)

    # 2. Tìm ngành xuất hiện nhiều nhất
    most_common = industry_counts.most_common(1)
    if not most_common:
        # Trường hợp không có ngành nào (ít xảy ra)
        return {
            'dominant_industry': None,
            'dominant_count': 0,
            'outliers': top_list
        }

    dominant_industry, dominant_count = most_common[0]
    ratio = dominant_count / total

    # 3. Kiểm tra ngành chiếm ưu thế dựa trên ngưỡng cấu hình
    is_dominant = (dominant_count >= MIN_DOMINANT_COUNT) or (ratio >= MIN_DOMINANT_RATIO)

    if not is_dominant:
        # Không có dominant industry hợp lệ -> không có outlier
        return {
            'dominant_industry': None,
            'dominant_count': 0,
            'outliers': []
        }

    # 4. Lọc outlier: cổ phiếu có ngành khác với dominant và thêm lý do
    outliers = []
    for item in top_list:
        if item['industry'] != dominant_industry:
            # Tạo bản sao để không làm biến đổi data gốc
            outlier_item = item.copy() 
            outlier_item['reason'] = "Khác ngành với nhóm chiếm ưu thế"
            outliers.append(outlier_item)

    return {
        'dominant_industry': dominant_industry,
        'dominant_count': dominant_count,
        'outliers': outliers
    }