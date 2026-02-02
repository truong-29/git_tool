#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Assistant Tool
Một công cụ hỗ trợ Git workflows chuẩn cho người mới.
Được viết lại theo mô hình module hóa và hỗ trợ GUIvcfssd.
"""

import sys
import os
import argparse
import tkinter as tk

# Thêm thư mục hiện tại vào path để import package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    parser = argparse.ArgumentParser(description="Git Assistant Tool")
    parser.add_argument("--cli", action="store_true", help="Chạy chế độ dòng lệnh (CLI)")
    args = parser.parse_args()

    if args.cli:
        try:
            from git_assistant.ui import GitUI
            app = GitUI()
            app.run()
        except ImportError as e:
            print(f"Lỗi import: {e}")
    else:
        try:
            from git_assistant.gui import GitGuiApp
            root = tk.Tk()
            app = GitGuiApp(root)
            root.mainloop()
        except ImportError as e:
            print(f"Lỗi khởi động GUI: {e}")
            print("Đang thử chuyển sang chế độ CLI...")
            from git_assistant.ui import GitUI
            app = GitUI()
            app.run()

if __name__ == "__main__":
    main()
