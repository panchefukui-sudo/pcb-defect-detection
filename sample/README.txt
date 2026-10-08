#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Launch the PCB defect detection desktop GUI."""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    print("PCB 環境檢測中...")
    subprocess.run([sys.executable, os.path.join(ROOT, "gui_app.py")], cwd=ROOT)
