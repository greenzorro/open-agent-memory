"""
File: scaler.py
Project: open-agent-memory
Created: 2024-11-05 06:39:43
Author: Victor Cheng
Email: your_email@example.com
Description: 将图片限制在指定长边最大值内，并处理长图的最小宽度
"""

import os
import argparse
import sys

current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(current_dir))

from utils import *


def main():
    parser = argparse.ArgumentParser(
        description="将图片限制在指定最大值内，支持长边或短边缩放"
    )
    parser.add_argument("--source", "-s", help="源文件夹路径（必填）")
    parser.add_argument(
        "--output", "-o", help="输出文件夹路径（可选，默认：Img_scaled）"
    )
    parser.add_argument("--max-size", type=int, help="最大尺寸值（必填）")
    parser.add_argument(
        "--mode",
        "-m",
        choices=["long", "short"],
        help="模式：long-长边缩放到最大值，short-短边缩放到最大值（必填）",
    )
    parser.add_argument("--min-width", type=int, help="长图的最小宽度（必填）")
    args = parser.parse_args()

    SRC_FOLDER = get_param_value(args, "source", prompt_text="源文件夹路径")

    default_output = os.path.join(PATH_DOWNLOADS, "Img_scaled")

    DST_FOLDER = get_param_value(args, "output", script_default=default_output)

    max_size = int(get_param_value(args, "max_size", prompt_text="最大尺寸值"))
    mode = get_param_value(args, "mode", prompt_text="缩放模式（long/short）")
    min_width = int(get_param_value(args, "min_width", prompt_text="长图的最小宽度"))

    if not os.path.exists(SRC_FOLDER):
        print(f"错误：源文件夹不存在: {SRC_FOLDER}")
        sys.exit(1)

    if not os.path.exists(DST_FOLDER):
        os.makedirs(DST_FOLDER)

    for filename in os.listdir(SRC_FOLDER):
        if filename.startswith("."):
            continue
        src_format = (os.path.splitext(filename)[1])[1:]
        if src_format in ["jpg", "jpeg", "png", "bmp", "gif"]:
            src_path = os.path.join(SRC_FOLDER, filename)
            dst_path = os.path.join(DST_FOLDER, filename)

            scale_image(src_path, dst_path, max_size, min_width, mode=mode)

            if os.path.exists(dst_path):
                print(f"{src_path} scaled")
            else:
                print(f"Failed to scale {src_path}")


if __name__ == "__main__":
    main()
