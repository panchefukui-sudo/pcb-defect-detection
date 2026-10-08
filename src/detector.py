# PCB 瑕疵檢測器核心模塊

import cv2
import numpy as np
import logging
from . import config
from .utils import enhance_image, save_image

logger = logging.getLogger(__name__)


class PCBDefectDetector:
    """PCB 瑕疵檢測器主類"""
    
    def __init__(self, config_dict=None):
        """
        初始化檢測器
        
        Args:
            config_dict: 配置參數字典
        """
        self.config = config_dict or config
        self.defects = []
        self.image = None
        self.processed_image = None
        logger.info("PCB 瑕疵檢測器已初始化")
    
    def detect(self, image, detect_types=None):
        """
        檢測圖像中的瑕疵
        
        Args:
            image: 輸入圖像
            detect_types: 檢測類型列表 (可選)
            
        Returns:
            檢測到的缺陷列表
        """
        self.image = image.copy()
        self.defects = []
        
        if detect_types is None:
            detect_types = ['short_circuit', 'open_circuit', 'foreign_object', 'void']
        
        logger.info(f"開始檢測，檢測類型: {detect_types}")
        
        # 圖像預處理
        preprocessed = self._preprocess(image)
        self.processed_image = preprocessed
        
        # 根據檢測類型調用相應的檢測函數
        if 'short_circuit' in detect_types:
            self._detect_short_circuit(preprocessed)
        
        if 'open_circuit' in detect_types:
            self._detect_open_circuit(preprocessed)
        
        if 'foreign_object' in detect_types:
            self._detect_foreign_object(preprocessed)
        
        if 'void' in detect_types:
            self._detect_void(preprocessed)
        
        logger.info(f"檢測完成，找到 {len(self.defects)} 個缺陷")
        return self.defects
    
    def _preprocess(self, image):
        """
        圖像預處理
        
        Args:
            image: 原始圖像
            
        Returns:
            預處理後的圖像
        """
        # 轉灰度圖
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 增強對比度
        enhanced = enhance_image(image)
        
        # 高斯模糊降噪
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        return blurred
    
    def _detect_short_circuit(self, image):
        """
        檢測短路缺陷
        使用邊界檢測和連通區域分析
        """
        logger.info("執行短路檢測...")
        
        # Canny 邊界檢測
        edges = cv2.Canny(
            image,
            self.config.CANNY_THRESHOLD1,
            self.config.CANNY_THRESHOLD2
        )
        
        # 膨脹操作連接斷開的邊界
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            self.config.MORPH_KERNEL_SIZE
        )
        dilated = cv2.dilate(edges, kernel, iterations=self.config.DILATION_ITERATIONS)
        
        # 查找輪廓
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 分析輪廓
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # 過濾掉太小或太大的輪廓
            if area < self.config.MIN_CONTOUR_AREA or area > self.config.MAX_CONTOUR_AREA:
                continue
            
            # 計算邊界框
            x, y, w, h = cv2.boundingRect(contour)
            
            # 計算短路置信度
            perimeter = cv2.arcLength(contour, True)
            circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
            confidence = min(1.0, 1.0 - circularity)
            
            if confidence > self.config.SHORT_CIRCUIT_THRESHOLD:
                defect = {
                    'type': '短路',
                    'bbox': (x, y, w, h),
                    'area': area,
                    'confidence': confidence,
                    'contour': contour
                }
                self.defects.append(defect)
                logger.debug(f"檢測到短路: {defect}")
    
    def _detect_open_circuit(self, image):
        """
        檢測斷線缺陷
        使用形態學骨架化和缺口檢測
        """
        logger.info("執行斷線檢測...")
        
        # Sobel 邊界檢測
        sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=self.config.SOBEL_KERNEL_SIZE)
        sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=self.config.SOBEL_KERNEL_SIZE)
        edges = np.sqrt(sobelx**2 + sobely**2).astype(np.uint8)
        
        # 二值化
        _, binary = cv2.threshold(edges, 50, 255, cv2.THRESH_BINARY)
        
        # 腐蝕操作分離連接的線
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        eroded = cv2.erode(binary, kernel, iterations=1)
        
        # 查找輪廓
        contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            
            if area < self.config.MIN_CONTOUR_AREA or perimeter < self.config.MIN_CONTOUR_PERIMETER:
                continue
            
            # 計算細長度（斷線通常較細長）
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h if h > 0 else 0
            
            if aspect_ratio > 2 or aspect_ratio < 0.5:  # 細長特徵
                confidence = min(1.0, abs(1 - aspect_ratio / 5))
                
                if confidence > self.config.OPEN_CIRCUIT_THRESHOLD:
                    defect = {
                        'type': '斷線',
                        'bbox': (x, y, w, h),
                        'area': area,
                        'confidence': confidence,
                        'contour': contour
                    }
                    self.defects.append(defect)
                    logger.debug(f"檢測到斷線: {defect}")
    
    def _detect_foreign_object(self, image):
        """
        檢測異物缺陷
        基於顏色和質地分析
        """
        logger.info("執行異物檢測...")
        
        # 轉為 HSV 色彩空間
        if len(image.shape) == 2:
            bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            bgr = image
        
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        
        # 檢測黑色異物
        mask_black = cv2.inRange(
            hsv,
            np.array(self.config.BLACK_LOWER),
            np.array(self.config.BLACK_UPPER)
        )
        
        # 檢測棕色銹蝕
        mask_brown = cv2.inRange(
            hsv,
            np.array(self.config.BROWN_LOWER),
            np.array(self.config.BROWN_UPPER)
        )
        
        # 合併掩膜
        mask = cv2.bitwise_or(mask_black, mask_brown)
        
        # 形態學操作
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, self.config.MORPH_KERNEL_SIZE)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # 查找輪廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if area < self.config.MIN_CONTOUR_AREA:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            
            # 計算置信度（基於面積和緊湊性）
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter ** 2)
            else:
                circularity = 0
            
            confidence = min(1.0, circularity)
            
            if confidence > self.config.FOREIGN_OBJECT_THRESHOLD:
                defect = {
                    'type': '異物',
                    'bbox': (x, y, w, h),
                    'area': area,
                    'confidence': confidence,
                    'contour': contour
                }
                self.defects.append(defect)
                logger.debug(f"檢測到異物: {defect}")
    
    def _detect_void(self, image):
        """
        檢測孔洞缺陷
        基於暗區域檢測
        """
        logger.info("執行孔洞檢測...")
        
        # 二值化（檢測暗區）
        _, binary = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY_INV)
        
        # 腐蝕和膨脹
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, self.config.MORPH_KERNEL_SIZE)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # 查找輪廓
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if area < self.config.MIN_CONTOUR_AREA:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            perimeter = cv2.arcLength(contour, True)
            
            # 計算圓度（孔洞通常較圓）
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter ** 2)
            else:
                circularity = 0
            
            # 孔洞通常圓度較高
            confidence = min(1.0, circularity)
            
            if confidence > self.config.VOID_THRESHOLD:
                defect = {
                    'type': '孔洞',
                    'bbox': (x, y, w, h),
                    'area': area,
                    'confidence': confidence,
                    'contour': contour
                }
                self.defects.append(defect)
                logger.debug(f"檢測到孔洞: {defect}")
    
    def get_statistics(self):
        """
        獲取檢測統計信息
        
        Returns:
            統計信息字典
        """
        if not self.defects:
            return {
                'total_defects': 0,
                'defect_types': {},
                'avg_confidence': 0
            }
        
        stats = {
            'total_defects': len(self.defects),
            'defect_types': {},
            'avg_confidence': np.mean([d['confidence'] for d in self.defects])
        }
        
        # 按類型統計
        for defect in self.defects:
            defect_type = defect['type']
            if defect_type not in stats['defect_types']:
                stats['defect_types'][defect_type] = 0
            stats['defect_types'][defect_type] += 1
        
        return stats
    
    def save_debug_image(self, output_path):
        """
        保存調試圖像
        
        Args:
            output_path: 輸出路徑
        """
        if self.processed_image is None:
            logger.warning("沒有已處理圖像，無法保存")
            return
        
        save_image(self.processed_image, output_path)
        logger.info(f"調試圖像已保存: {output_path}")


if __name__ == "__main__":
    print("PCB 瑕疵檢測核心模塊")
