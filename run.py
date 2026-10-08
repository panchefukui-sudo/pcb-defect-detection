#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.detector import PCBDefectDetector
from src.utils import load_image, draw_results, save_image, get_image_files


def process_image(image_path, output_dir):
    image = load_image(image_path)
    if image is None:
        print(f"[ERROR] 無法讀取圖片: {image_path}")
        return

    detector = PCBDefectDetector()
    defects = detector.detect(image, ["short_circuit", "open_circuit", "foreign_object", "void"])
    result = draw_results(image, defects)
    os.makedirs(output_dir, exist_ok=True)
    out_name = os.path.splitext(os.path.basename(image_path))[0] + "_detected.png"
    out_path = os.path.join(output_dir, out_name)
    save_image(result, out_path)
    print(f"[OK] 檢測完成: {out_path} | 缺陷數: {len(defects)}")


def main():
    parser = argparse.ArgumentParser(description="PCB 瑕疵檢測 CLI")
    parser.add_argument("--input", "-i", required=True, help="輸入圖像路徑或資料夾")
    parser.add_argument("--output", "-o", default="results", help="輸出資料夾")
    args = parser.parse_args()

    input_path = args.input
    output_dir = args.output

    if os.path.isfile(input_path):
        process_image(input_path, output_dir)
    elif os.path.isdir(input_path):
        files = get_image_files(input_path)
        if not files:
            print("[WARN] 資料夾中沒有有效影像檔案")
            return
        for file in files:
            process_image(file, output_dir)
    else:
        print(f"[ERROR] 路徑不存在: {input_path}")


if __name__ == "__main__":
    main()
