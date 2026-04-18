"""
File: gif_2_frames.py
Project: open-agent-memory
Created: 2024-11-05 06:39:43
Author: Victor Cheng
Email: your_email@example.com
Description: 将GIF转换为图片帧序列
"""

import os
import sys
import argparse

current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(current_dir))

from utils import *


def main():
    parser = argparse.ArgumentParser(
        description="将GIF转换为图片帧序列",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--source", "-s", help="源文件夹路径（必填，包含GIF文件）")
    parser.add_argument(
        "--output",
        "-o",
        help="输出文件夹路径（可选，默认：PATH_DOWNLOADS/Converted_frames）",
    )

    args = parser.parse_args()

    SRC_FOLDER = get_param_value(
        args, "source", prompt_text="源文件夹路径（包含GIF文件）"
    )

    default_output = os.path.join(PATH_DOWNLOADS, "Converted_frames")
    DST_FOLDER = get_param_value(args, "output", script_default=default_output)

    if not os.path.exists(SRC_FOLDER):
        print(f"错误：源文件夹不存在: {SRC_FOLDER}")
        sys.exit(1)

    if not os.path.exists(DST_FOLDER):
        os.makedirs(DST_FOLDER)

    gif_2_frames(SRC_FOLDER, DST_FOLDER)
    print(f"GIF帧已提取并保存到:\n{DST_FOLDER}")


if __name__ == "__main__":
    main()
