# PCB 瑕疵檢測系統配置文件

# ==================== 圖像處理參數 ====================

# 圖像縮放因子（加速處理）
RESIZE_FACTOR = 1.0  # 1.0 = 原始大小，0.5 = 縮小一半

# 對比度增強因子
CONTRAST_FACTOR = 1.2

# 亮度增強值
BRIGHTNESS_FACTOR = 10

# ==================== 邊界檢測參數 ====================

# Canny 邊界檢測閾值
CANNY_THRESHOLD1 = 50
CANNY_THRESHOLD2 = 150

# Sobel 邊界檢測核大小
SOBEL_KERNEL_SIZE = 3

# ==================== 輪廓檢測參數 ====================

# 輪廓面積範圍（像素²）
MIN_CONTOUR_AREA = 50
MAX_CONTOUR_AREA = 50000

# 輪廓周長範圍
MIN_CONTOUR_PERIMETER = 20
MAX_CONTOUR_PERIMETER = 5000

# 輪廓近似精度
CONTOUR_APPROX_EPSILON = 0.02

# ==================== 顏色空間閾值 ====================

# HSV 色彩空間範圍（用於銹蝕和異物檢測）
HSV_LOWER = (0, 0, 0)
HSV_UPPER = (180, 255, 255)

# 黑色異物檢測範圍
BLACK_LOWER = (0, 0, 0)
BLACK_UPPER = (180, 255, 50)

# 棕色銹蝕檢測範圍
BROWN_LOWER = (10, 100, 100)
BROWN_UPPER = (25, 255, 255)

# ==================== 形態學操作參數 ====================

# 腐蝕和膨脹操作的核大小
MORPH_KERNEL_SIZE = (5, 5)

# 腐蝕迭代次數
EROSION_ITERATIONS = 2

# 膨脹迭代次數
DILATION_ITERATIONS = 2

# ==================== 缺陷檢測閾值 ====================

# 短路檢測靈敏度（0-1，越小越靈敏）
SHORT_CIRCUIT_THRESHOLD = 0.3

# 斷線檢測靈敏度
OPEN_CIRCUIT_THRESHOLD = 0.4

# 異物檢測靈敏度
FOREIGN_OBJECT_THRESHOLD = 0.35

# 孔洞檢測靈敏度
VOID_THRESHOLD = 0.45

# ==================== 結果輸出參數 ====================

# 結果圖像中缺陷框的顏色 (B, G, R)
DEFECT_BOX_COLOR = (0, 0, 255)  # 紅色

# 缺陷框線寬
DEFECT_BOX_THICKNESS = 2

# 文字顏色
TEXT_COLOR = (0, 255, 255)  # 黃色

# 文字大小
TEXT_FONT_SCALE = 0.6

# 文字線寬
TEXT_THICKNESS = 2

# ==================== 性能參數 ====================

# 是否啟用多線程
USE_MULTITHREADING = True

# 最大線程數
MAX_THREADS = 4

# 批處理時的批次大小
BATCH_SIZE = 10

# ==================== 日誌參數 ====================

# 日誌級別：DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# 是否保存調試圖像
SAVE_DEBUG_IMAGES = False

# ==================== 模型參數（擴展用） ====================

# 深度學習模型路徑
MODEL_PATH = "models/pcb_detector.pth"

# YOLO 模型配置
YOLO_MODEL_SIZE = "small"  # nano, small, medium, large

# 置信度閾值
CONFIDENCE_THRESHOLD = 0.5

# NMS IOU 閾值
NMS_IOU_THRESHOLD = 0.45

# ==================== 缺陷類型定義 ====================

DEFECT_TYPES = {
    "short_circuit": "短路",
    "open_circuit": "斷線",
    "missing_component": "缺料",
    "foreign_object": "異物",
    "void": "孔洞",
    "corrosion": "銹蝕",
    "solder_bridge": "焊錫橋",
    "cold_joint": "冷焊點"
}

# ==================== 獲取配置函數 ====================

def get_config_dict():
    """獲取所有配置參數"""
    import inspect
    config = {}
    for name, obj in inspect.getmembers(inspect.currentframe()):
        if not name.startswith('_') and name.isupper():
            config[name] = obj
    return config

if __name__ == "__main__":
    print("PCB 瑕疵檢測系統配置參數")
    print("=" * 50)
    config = get_config_dict()
    for key, value in config.items():
        print(f"{key}: {value}")
