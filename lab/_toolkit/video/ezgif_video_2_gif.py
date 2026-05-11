"""
File: ezgif_video_2_gif.py
Project: routine
Created: 2026-02-24 03:22:57
Author: Victor Cheng
Email: hi@victor42.work
Description: 批量将视频转换为GIF并优化 (复用 ezgif.com 在线服务)
"""

import os
import sys
import asyncio
import subprocess
import argparse
import re
from pathlib import Path
from typing import Optional

current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(current_dir))

from utils.browser_auto import (
    WebBrowserContext, wait_for_element, click_element,
    get_element_attribute, execute_javascript,
)
from utils.basic import get_param_value
from utils.path import PATH_DOWNLOADS

# 配置常量
EZGIF_URL = "https://ezgif.com/video-to-gif"
RESIZE_URL_TEMPLATE = "https://ezgif.com/resize/{}"
SIZE_OPTION = "Original (up to 800px)"
OPTIMIZE_METHOD = "Lossy GIF"
OPTIMIZE_LEVEL = 30

# Resize 选择器
RESIZE_PERCENTAGE_SELECTOR = 'input[name="percentage"]'
RESIZE_BUTTON_SELECTOR = 'input[value="Resize image!"]'


def download_via_curl(url: str, path: str) -> bool:
    """使用 curl 下载文件"""
    return subprocess.run(["curl", "-s", "-o", path, url]).returncode == 0


async def resize_gif(page, gif_url: str, percentage: int, timeout: int = 120) -> Optional[str]:
    """
    使用 ezgif.com 调整 GIF 尺寸

    Args:
        page: Playwright 页面对象
        gif_url: 当前 GIF 的 URL
        percentage: 缩放百分比 (1-100)
        timeout: 超时时间（秒）

    Returns:
        Resize 后的 GIF 文件名（如 /ezgif-xxx.gif），失败返回 None
    """
    try:
        # 1. 提取文件名并构建 resize URL
        match = re.search(r"/ezgif-[^/]+\.gif", gif_url)
        if not match:
            return None

        gif_filename = match.group(0)  # 如 /ezgif-8dc2df508aedd0af.gif
        resize_url = RESIZE_URL_TEMPLATE.format(gif_filename)

        # 2. 导航到 resize 页面
        await page.goto(resize_url, wait_until="domcontentloaded")

        # 3. 等待并填写 percentage
        if not await wait_for_element(page, RESIZE_PERCENTAGE_SELECTOR, timeout=30):
            return None

        await page.fill(RESIZE_PERCENTAGE_SELECTOR, str(percentage))

        # 4. 点击 Resize 按钮
        await click_element(page, RESIZE_BUTTON_SELECTOR, "Resize按钮")

        # 5. 等待结果生成
        if not await wait_for_element(
            page, 'div#output img[src*="ezgif-"][src$=".gif"]', timeout=timeout
        ):
            return None

        # 6. 获取新的 GIF 文件名
        new_gif_url = await get_element_attribute(
            page, 'div#output img[src*="ezgif-"][src$=".gif"]', "src"
        )

        new_match = re.search(r"/ezgif-[^/]+\.gif", new_gif_url or "")
        return new_match.group(0) if new_match else None

    except Exception as e:
        return None


async def process_single_video(
    page, video_path: Path, output_dir: str, progress_str: str, resize_percentage: Optional[int] = None
) -> bool:
    """处理单个视频文件转换流程

    Args:
        page: Playwright 页面对象
        video_path: 视频文件路径
        output_dir: 输出目录
        progress_str: 进度显示字符串
        resize_percentage: 可选的缩放百分比（1-100），不设置则跳过

    Returns:
        bool: 处理成功返回 True，否则返回 False
    """
    output_path = os.path.join(output_dir, f"{video_path.stem}.gif")
    if os.path.exists(output_path):
        return True

    print(f"{progress_str} 正在处理: {video_path.name}")
    try:
        # 1. 导航
        try:
            await page.goto(EZGIF_URL, wait_until="domcontentloaded")
        except Exception as e:
            print(f"    [错误] 页面加载失败: {e}")
            return False

        # 2. 上传
        file_input_selector = "input#new-image"
        if not await wait_for_element(page, file_input_selector, timeout=20):
            print(f"    [错误] 找不到上传控件")
            return False

        await page.set_input_files(file_input_selector, str(video_path))

        # 触发上传
        upload_btn = 'input[value="Upload video!"], input[name="upload"]'
        await page.click(upload_btn, timeout=10000)
        await page.keyboard.press("Enter")

        # 3. 等待转换页面
        convert_btn = 'input[value="Convert to GIF!"]'
        for _ in range(3):
            if await wait_for_element(page, convert_btn, timeout=60):
                break
            try:
                await page.click(upload_btn, timeout=2000)
            except:
                pass
        else:
            print(f"    [错误] 上传超时")
            return False

        # 4. 执行转换
        await page.select_option('select[name="size"]', label=SIZE_OPTION)
        await click_element(page, convert_btn, "转换按钮")

        # 5. 等待转换结果
        if not await wait_for_element(
            page, 'div#output:has(a:has-text("Save"))', timeout=300
        ):
            print(f"    [错误] 转换结果未生成")
            return False

        gif_url = await get_element_attribute(
            page, 'div#output img[src*="ezgif-"][src$=".gif"]', "src"
        )
        match = re.search(r"/ezgif-[^/]+\.gif", gif_url or "")
        if not match:
            return False

        gif_filename = match.group(0)

        # 6. (可选) Resize 步骤
        if resize_percentage is not None:
            print(f"    [Resize] 缩放至 {resize_percentage}%")
            new_gif_filename = await resize_gif(page, gif_url, resize_percentage)
            if not new_gif_filename:
                print(f"    [跳过] Resize 失败，继续优化流程")
            else:
                gif_filename = new_gif_filename

        # 7. 跳转优化
        await page.goto(
            f"https://ezgif.com/optimize{gif_filename}", wait_until="domcontentloaded"
        )

        # 8. 设置优化
        if not await wait_for_element(page, 'select[name="method"]', timeout=30):
            return False
        await page.select_option('select[name="method"]', value=OPTIMIZE_METHOD)

        if await wait_for_element(page, 'input[name="level"]', timeout=10):
            await page.fill('input[name="level"]', str(OPTIMIZE_LEVEL))

        await click_element(page, 'input[value="Optimize GIF!"]', "优化按钮")

        # 9. 等待并下载
        if not await wait_for_element(
            page, 'h2:has-text("Optimized image")', timeout=300
        ):
            print(f"    [错误] 优化超时")
            return False

        await asyncio.sleep(3)  # 结果生成的缓冲

        get_link_script = """
        () => {
            const h2 = Array.from(document.querySelectorAll('h2')).find(el => el.textContent.includes('Optimized image'));
            if (!h2) return null;
            const container = h2.parentElement;
            const save = Array.from(container.querySelectorAll('a')).find(a => a.textContent.trim() === 'Save');
            return save ? save.href : null;
        }
        """
        download_url = await execute_javascript(page, get_link_script)

        if download_url and download_via_curl(download_url, output_path):
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1024:
                size_mb = os.path.getsize(output_path) / 1024 / 1024
                # 在库日志后强制换行并打印成功信息
                print(
                    f"\n    [成功] 已保存: {os.path.basename(output_path)} ({size_mb:.2f} MB)\n"
                )
                return True

        print(f"\n    [失败] 下载文件损坏或未找到")
        return False

    except Exception as e:
        print(f"\n    [跳过] 运行时异常: {e}")
        return False


async def process_videos(source_dir: str, output_dir: str, resize_percentage: Optional[int] = None):
    """批量处理视频文件工作流

    Args:
        source_dir: 源视频目录
        output_dir: 输出目录
        resize_percentage: 可选的缩放百分比（1-100），不设置则跳过
    """
    video_files = (
        sorted(Path(source_dir).glob("*.mp4")) if os.path.exists(source_dir) else []
    )
    if not video_files:
        print(f"错误：在 {source_dir} 中未找到 mp4 文件")
        return

    print(f"\n{'=' * 60}")
    print(f"批量视频转GIF工具")
    print(f"{'=' * 60}")
    print(f"源目录: {source_dir}")
    print(f"输出目录: {output_dir}")
    print(f"待处理视频: {len(video_files)} 个")
    print(f"{'=' * 60}\n")

    success_count = 0
    async with WebBrowserContext(headless=False) as page:
        for i, video_file in enumerate(video_files, 1):
            progress = f"[{i}/{len(video_files)}]"
            if await process_single_video(page, video_file, output_dir, progress, resize_percentage):
                success_count += 1

    print(f"{'=' * 60}")
    print(f"任务完成!")
    print(f"成功: {success_count} / 失败: {len(video_files) - success_count}")
    print(f"输出目录: {output_dir}")
    print(f"{'=' * 60}\n")


def main():
    """入口函数"""
    parser = argparse.ArgumentParser(description="批量将视频转换为GIF并优化")
    parser.add_argument("--source", "-s", help="源视频目录")
    parser.add_argument("--output", "-o", help="输出目录")
    parser.add_argument("--resize-percentage", "-rp", type=int,
                       help="Resize GIF by percentage (1-100), e.g. 50 = 50%%")
    args = parser.parse_args()

    source = get_param_value(args, "source", prompt_text="请输入源视频目录")

    # 默认输出到下载目录下的 Gif 文件夹
    default_output = os.path.join(PATH_DOWNLOADS, "Gif")
    output = get_param_value(args, "output", script_default=default_output)

    # 可选参数：resize percentage
    resize_percentage = get_param_value(args, "resize_percentage", script_default=75)

    # 验证范围
    if resize_percentage is not None and not (1 <= resize_percentage <= 100) and resize_percentage != 0:
        print("错误：resize-percentage 必须在 1-100 之间，或者使用0表示不缩放")
        return

    # 如果resize_percentage为0，则将其设置为None以跳过缩放
    if resize_percentage == 0:
        resize_percentage = None

    if source and os.path.exists(source):
        os.makedirs(output, exist_ok=True)
        asyncio.run(process_videos(source, output, resize_percentage))
    else:
        print(f"错误：源目录不存在: {source}")


if __name__ == "__main__":
    main()
