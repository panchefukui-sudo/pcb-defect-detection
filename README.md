# PCB 瑕疵檢測系統
# 本地桌面版 GUI，適合 PCB 圖像缺陷檢測

這個專案是一個基於 Python 的 PCB（印刷電路板）瑕疵檢測系統，目標是讓你能在本地電腦上直接開啟 GUI，載入 PCB 圖片後做缺陷檢測與結果標記。

功能重點：
- 本地執行，不依賴雲端
- 桌面 GUI 介面
- 支援短路、斷線、異物、孔洞檢測
- 可批量處理資料夾中的多張圖像
- 可儲存檢測結果圖像

快速開始：
1. 建立虛擬環境（可選）
   python -m venv .venv
   . .venv/bin/activate    # Linux/macOS
   .\.venv\Scripts\activate  # Windows

2. 安裝依賴
   pip install -r requirements.txt

3. 啟動桌面版應用
   python run.py

4. 或直接啟動 CLI
   python main.py --input sample/pcb_sample.jpg --output results/

專案結構：
- gui_app.py        桌面版 GUI 應用
- main.py           CLI 批次處理入口
- run.py            啟動腳本
- src/
  - __init__.py
  - config.py
  - detector.py
  - utils.py
- sample/           範例圖像目錄（可放 PCB 圖片）
- results/          檢測結果輸出

支援的檢測類型：
- 短路
- 斷線
- 異物
- 孔洞

如果你沒有 PCB 標準影像，可先用任意電路板照片進行測試。實際檢測效果會依賴圖像品質、光線、解析度與瑕疵明顯度。
