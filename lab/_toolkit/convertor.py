"""
File: convertor.py
Project: open-agent-memory
Created: 2025-11-01 10:24:26
Author: Victor Cheng
Email: your_email@example.com
Description: 通用格式转换器
"""

import os
import sys
import argparse
from utils import *


def main():
    parser = argparse.ArgumentParser(
        description="批量转换文件格式（支持图片、音频、视频）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--source", "-s", help="源文件夹路径")
    parser.add_argument(
        "--output",
        "-o",
        help="输出文件夹路径（默认：PATH_DOWNLOADS/Converted）",
    )
    parser.add_argument("--format", "-f", help="目标格式（如：mp3, jpg, webp）")

    args = parser.parse_args()

    SRC_FOLDER = get_param_value(args, "source", prompt_text="源文件夹路径")

    if not os.path.exists(SRC_FOLDER):
        print(f"错误：源路径不存在: {SRC_FOLDER}")
        sys.exit(1)

    default_output = os.path.join(PATH_DOWNLOADS, "Converted")
    DST_FOLDER = get_param_value(args, "output", script_default=default_output)

    if not os.path.exists(DST_FOLDER):
        os.makedirs(DST_FOLDER)

    DST_FORMAT = get_param_value(args, "format", prompt_text="目标格式")

    for root, dirs, files in os.walk(SRC_FOLDER):
        for filename in files:
            if filename.startswith("."):
                continue
            src_path = os.path.join(root, filename)
            dst_name = os.path.splitext(filename)[0] + "." + DST_FORMAT
            dst_path = os.path.join(DST_FOLDER, dst_name)
            convert_format(src_path, dst_path, DST_FORMAT)


if __name__ == "__main__":
    main()
