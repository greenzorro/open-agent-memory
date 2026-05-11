"""
File: resizer.py
Project: routine
Created: 2024-11-05 06:39:43
Author: Victor Cheng
Email: hi@victor42.work
Description: 将图片调整为指定宽高，支持裁剪和留白模式
"""

import os
import argparse
import sys

current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(current_dir))

from utils.image import resize_image
from utils.basic import get_param_value
from utils.path import get_platform, PATH_DOWNLOADS_FROM_WIN, PATH_DOWNLOADS


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

    platform_type = get_platform()
    if platform_type == "wsl":
        default_output = os.path.join(PATH_DOWNLOADS_FROM_WIN, "Img_resized")
    else:
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

    # 遍历输入文件夹中的图片
    for filename in os.listdir(SRC_FOLDER):
        # 忽略隐藏文件和文件夹
        if filename.startswith("."):
            continue
        src_format = (os.path.splitext(filename)[1])[1:]
        if src_format in ["jpg", "jpeg", "png", "bmp", "gif"]:
            # 打开图片并获取原始宽高
            src_path = os.path.join(SRC_FOLDER, filename)
            dst_path = os.path.join(DST_FOLDER, filename)

            # 处理图片
            resize_image(
                src_path, dst_path, target_width, target_height, mode, bg_color
            )

            # 打印输出结果
            if os.path.exists(dst_path):
                print(f"{src_path} resized")
            else:
                print(f"Failed to resize {src_path}")


if __name__ == "__main__":
    main()
