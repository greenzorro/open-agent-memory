"""
File: html_table_2_csv.py
Project: routine
Created: 2025-11-01 10:24:26
Author: Victor Cheng
Email: hi@victor42.work
Description: 批量将HTML文件中的表格转换为CSV格式
"""

import os
import csv
import sys
import argparse
from utils.basic import get_param_value, get_source_files, html_table_2_csv_content
from utils.path import platform_type, PATH_DOWNLOADS_FROM_WIN, PATH_DOWNLOADS


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="批量将HTML文件中的表格转换为CSV格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # 添加参数
    parser.add_argument("--source", "-s", help="源HTML文件或文件夹路径")
    parser.add_argument(
        "--output",
        "-o",
        help="输出文件夹路径（默认：PATH_DOWNLOADS/Csv_from_html）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="演练模式：读取并解析 HTML，但不创建目录或写入 CSV 文件",
    )

    # 解析参数
    args = parser.parse_args()

    # 获取源路径（必填参数，无默认值时询问用户）
    SRC_PATH = get_param_value(args, "source", prompt_text="源HTML文件或文件夹路径")

    # 验证源路径存在
    if not os.path.exists(SRC_PATH):
        print(f"错误：源路径不存在: {SRC_PATH}")
        sys.exit(1)

    # 获取目标文件夹路径（可选参数，有脚本默认值，不问用户）
    if platform_type == "wsl":
        default_output = os.path.join(PATH_DOWNLOADS_FROM_WIN, "Csv_from_html")
    else:
        default_output = os.path.join(PATH_DOWNLOADS, "Csv_from_html")
    DST_FOLDER = get_param_value(args, "output", script_default=default_output)

    if args.dry_run:
        print("当前为 dry-run 演练模式，不会创建目录或写入文件")
    elif not os.path.exists(DST_FOLDER):
        os.makedirs(DST_FOLDER)

    for src_path in get_source_files(SRC_PATH, allowed_extensions=["html"]):
        filename = os.path.basename(src_path)

        try:
            with open(src_path, "r", encoding="utf-8") as f:
                html_content = f.read()
        except Exception as e:
            print(f"错误：读取文件 {src_path} 失败: {e}")
            continue

        try:
            csv_content = html_table_2_csv_content(html_content)
        except Exception as e:
            print(f"错误：转换HTML内容失败 {src_path}: {e}")
            continue

        dst_path = os.path.join(DST_FOLDER, os.path.splitext(filename)[0] + ".csv")

        if args.dry_run:
            print(f"[dry-run] 将转换: {src_path} -> {dst_path} ({len(csv_content)} 行)")
            continue

        try:
            with open(dst_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(csv_content)

            if os.path.exists(dst_path):
                print(f"{src_path} converted to csv")
            else:
                print(f"Failed to convert {src_path}")
        except Exception as e:
            print(f"错误：写入CSV文件 {dst_path} 失败: {e}")


if __name__ == "__main__":
    main()
