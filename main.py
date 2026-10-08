#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PCB defect detection system: desktop GUI app."""

import os
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QCheckBox,
    QGroupBox,
    QTextEdit,
    QScrollArea,
    QMessageBox,
    QProgressBar,
    QStatusBar,
    QSpinBox,
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.detector import PCBDefectDetector
from src.utils import load_image, save_image, draw_results, get_image_files
from src import config


class DetectionWorker:
    def __init__(self, image, detector, detect_types):
        self.image = image
        self.detector = detector
        self.detect_types = detect_types
        self.result = None
        self.stats = {}

    def run(self):
        self.result = self.detector.detect(self.image, self.detect_types)
        self.stats = self.detector.get_statistics()
        return self.result, self.stats


class PCBDetectorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image = None
        self.result_image = None
        self.defects = []
        self.stats = {}
        self.current_path = ""
        self.setWindowTitle("PCB 瑕疵檢測系統 - 桌面版")
        self.resize(1200, 820)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        left = QGroupBox("控制面板")
        left_layout = QVBoxLayout(left)

        load_btn = QPushButton("開啟 PCB 圖片")
        load_btn.clicked.connect(self.load_image)
        left_layout.addWidget(load_btn)

        batch_btn = QPushButton("批量處理資料夾")
        batch_btn.clicked.connect(self.batch_process)
        left_layout.addWidget(batch_btn)

        save_btn = QPushButton("儲存結果")
        save_btn.clicked.connect(self.save_result)
        left_layout.addWidget(save_btn)

        detect_box = QGroupBox("檢測類型")
        detect_layout = QVBoxLayout(detect_box)
        self.chk_short = QCheckBox("短路")
        self.chk_short.setChecked(True)
        self.chk_open = QCheckBox("斷線")
        self.chk_open.setChecked(True)
        self.chk_foreign = QCheckBox("異物")
        self.chk_foreign.setChecked(True)
        self.chk_void = QCheckBox("孔洞")
        self.chk_void.setChecked(True)
        detect_layout.addWidget(self.chk_short)
        detect_layout.addWidget(self.chk_open)
        detect_layout.addWidget(self.chk_foreign)
        detect_layout.addWidget(self.chk_void)
        left_layout.addWidget(detect_box)

        param_box = QGroupBox("參數")
        param_layout = QVBoxLayout(param_box)
        self.spin_canny1 = QSpinBox()
        self.spin_canny1.setRange(0, 255)
        self.spin_canny1.setValue(config.CANNY_THRESHOLD1)
        self.spin_canny2 = QSpinBox()
        self.spin_canny2.setRange(0, 255)
        self.spin_canny2.setValue(config.CANNY_THRESHOLD2)
        self.spin_min_area = QSpinBox()
        self.spin_min_area.setRange(1, 20000)
        self.spin_min_area.setValue(config.MIN_CONTOUR_AREA)
        param_layout.addWidget(QLabel("Canny 閾值 1"))
        param_layout.addWidget(self.spin_canny1)
        param_layout.addWidget(QLabel("Canny 閾值 2"))
        param_layout.addWidget(self.spin_canny2)
        param_layout.addWidget(QLabel("最小輪廓面積"))
        param_layout.addWidget(self.spin_min_area)
        left_layout.addWidget(param_box)

        detect_btn = QPushButton("開始檢測")
        detect_btn.setStyleSheet("background: #2E7D32; color: white; font-weight: bold;")
        detect_btn.clicked.connect(self.start_detection)
        left_layout.addWidget(detect_btn)

        left_layout.addStretch()
        main_layout.addWidget(left, 1)

        right = QWidget()
        right_layout = QVBoxLayout(right)

        self.image_label = QLabel("尚未載入圖像")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #aaa; background: #f5f5f5; min-height: 500px;")
        scroll = QScrollArea()
        scroll.setWidget(self.image_label)
        scroll.setWidgetResizable(True)
        right_layout.addWidget(scroll)

        self.info_box = QTextEdit()
        self.info_box.setReadOnly(True)
        self.info_box.setPlaceholderText("檢測結果會顯示在這裡")
        right_layout.addWidget(self.info_box)

        main_layout.addWidget(right, 2)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.statusBar = QStatusBar()
        self.statusBar.addPermanentWidget(self.progress)
        self.setStatusBar(self.statusBar)

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "選擇 PCB 圖像", "", "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)")
        if not path:
            return
        self.current_path = path
        image = load_image(path)
        if image is None:
            QMessageBox.critical(self, "錯誤", "圖片讀取失敗")
            return
        self.image = image
        self.result_image = None
        self.display_image(image)
        self.statusBar.showMessage(f"已載入: {os.path.basename(path)}")

    def display_image(self, image):
        if image is None:
            return
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = image_rgb.shape
        max_size = 900
        scale = min(max_size / w, max_size / h, 1.0)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        resized = cv2.resize(image_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)

        qimg = QImage(resized.data, new_w, new_h, new_w * ch, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.image_label.setPixmap(pixmap)

    def get_detect_types(self):
        types = []
        if self.chk_short.isChecked():
            types.append("short_circuit")
        if self.chk_open.isChecked():
            types.append("open_circuit")
        if self.chk_foreign.isChecked():
            types.append("foreign_object")
        if self.chk_void.isChecked():
            types.append("void")
        return types

    def start_detection(self):
        if self.image is None:
            QMessageBox.warning(self, "警告", "請先載入圖像")
            return

        detect_types = self.get_detect_types()
        if not detect_types:
            QMessageBox.warning(self, "警告", "請至少選擇一種檢測類型")
            return

        config.CANNY_THRESHOLD1 = self.spin_canny1.value()
        config.CANNY_THRESHOLD2 = self.spin_canny2.value()
        config.MIN_CONTOUR_AREA = self.spin_min_area.value()

        self.progress.setVisible(True)
        self.progress.setValue(10)
        self.statusBar.showMessage("正在檢測中...")

        detector = PCBDefectDetector()
        defects = detector.detect(self.image, detect_types)
        self.progress.setValue(100)

        self.defects = defects
        self.stats = detector.get_statistics()
        self.result_image = draw_results(self.image, self.defects)
        self.display_image(self.result_image)

        summary = ["[PCB 瑕疵檢測結果]", f"總缺陷數: {self.stats.get('total_defects', 0)}", f"平均置信度: {self.stats.get('avg_confidence', 0):.2%}"]
        for key, value in self.stats.get('defect_types', {}).items():
            summary.append(f"{key}: {value} 個")
        self.info_box.setText("\n".join(summary))
        self.progress.setVisible(False)
        self.statusBar.showMessage(f"檢測完成：找到 {len(self.defects)} 個缺陷")

    def save_result(self):
        if self.result_image is None:
            QMessageBox.warning(self, "警告", "目前沒有可儲存的結果")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "儲存檢測結果", "pcb_result.png", "PNG (*.png);;JPEG (*.jpg)")
        if not file_path:
            return

        success = save_image(self.result_image, file_path)
        if success:
            QMessageBox.information(self, "成功", f"結果已儲存到：\n{file_path}")
        else:
            QMessageBox.critical(self, "錯誤", "儲存失敗")

    def batch_process(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇資料夾")
        if not folder:
            return

        files = get_image_files(folder)
        if not files:
            QMessageBox.warning(self, "警告", "資料夾中沒有影像檔案")
            return

        output_dir = os.path.join(folder, "detected_results")
        os.makedirs(output_dir, exist_ok=True)

        for image_path in files:
            image = load_image(image_path)
            if image is None:
                continue
            detector = PCBDefectDetector()
            defects = detector.detect(image, self.get_detect_types())
            result = draw_results(image, defects)
            save_path = os.path.join(output_dir, os.path.splitext(os.path.basename(image_path))[0] + "_detected.png")
            save_image(result, save_path)

        QMessageBox.information(self, "完成", f"批量處理完成！\n共處理 {len(files)} 張圖像\n結果位於：{output_dir}")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = PCBDetectorWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
