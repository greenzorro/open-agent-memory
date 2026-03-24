"""
File: resizer.py
Project: open-agent-memory
Created: 2024-11-05 06:39:43
Author: Victor Cheng
Email: your_email@example.com
Description: 将图片调整为指定宽高，支持裁剪和留白模式
"""

import os
import argparse
import sys

current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(current_dir))

from utils import *


def main():
    parser = argparse.ArgumentParser(
        description="将图片调整为指定宽高，支持裁剪和留白模式"
    )
    parser.add_argument("--source", "-s", help="源文件夹路径（必填）")
    parser.add_argument(
        "--output", "-o", help="输出文件夹路径（可选，默认：Img_resized）"
    )
    parser.add_argument("--width", "-w", type=int, help="目标宽度（必填）")
    parser.add_argument("--height", "-H", type=int, help="目标高度（必填）")
    parser.add_argument(
        "--mode",
        "-m",
        choices=["crop", "pad"],
        help="模式：crop-裁剪，pad-留白（必填）",
    )
    parser.add_argument(
        "--bg-color",
        help="pad模式背景色（默认：white），支持颜色名称或十六进制（如 #FF0000）",
    )
    args = parser.parse_args()

    SRC_FOLDER = get_param_value(args, "source", prompt_text="源文件夹路径")

    default_output = os.path.join(PATH_DOWNLOADS, "Img_resized")

    DST_FOLDER = get_param_value(args, "output", script_default=default_output)

    target_width = int(get_param_value(args, "width", prompt_text="目标宽度"))
    target_height = int(get_param_value(args, "height", prompt_text="目标高度"))
    mode = get_param_value(args, "mode", prompt_text="模式（crop/pad）")
    bg_color = get_param_value(args, "bg_color", script_default="white")

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

            resize_image(
                src_path, dst_path, target_width, target_height, mode, bg_color
            )

            if os.path.exists(dst_path):
                print(f"{src_path} resized")
            else:
                print(f"Failed to resize {src_path}")


if __name__ == "__main__":
    main()
