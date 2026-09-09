# Số lượng cổ phiếu lấy từ mỗi bảng
TOP_N = 10
# Tiêu chí xác định "Ngành chiếm ưu thế" (Dominant Industry)
# Ví dụ: Ngành đó phải có ít nhất 4 mã trong Top 10
MIN_DOMINANT_COUNT = 4
# Hoặc tính theo tỷ lệ: Ngành đó phải chiếm tối thiểu 40% trong danh sách
MIN_DOMINANT_RATIO = 0.40
# Mục tiêu chốt lời mặc định (+30%)
TARGET_RETURN = 0.30
#số ngày mặc định để tính "đột biến" sau này
VOLUME_SMA_DAYS = 20