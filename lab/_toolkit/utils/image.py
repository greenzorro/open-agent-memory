"""
File: image.py
Project: routine
Created: 2024-11-05 03:29:57
Author: Victor Cheng
Email: your_email@example.com
Description:
"""

import os
import shutil
import re
import random
import json
import numpy as np
import imagehash
from PIL import Image
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from .basic import *


SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}


def validate_image_file(image_path: str) -> bool:
    """验证图片文件是否有效

    Args:
        image_path: 图片文件路径

    Returns:
        bool: 验证是否通过

    Raises:
        ValueError: 不支持的图片格式
        FileNotFoundError: 图片文件不存在
        IOError: 图片文件损坏或无法读取
    """
    # 检查文件扩展名
    ext = Path(image_path).suffix.lower()
    if ext not in SUPPORTED_IMAGE_FORMATS:
        raise ValueError(
            f"不支持的图片格式: {ext}。支持的格式: {SUPPORTED_IMAGE_FORMATS}"
        )

    # 检查文件是否存在
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")

    # 验证图片完整性
    try:
        with Image.open(image_path) as img:
            img.verify()
    except Exception as e:
        raise IOError(f"图片文件损坏或无法读取 {image_path}: {str(e)}")

    return True


def validate_images(image_files: List[str]):
    """验证所有图片文件

    Args:
        image_files: 图片文件路径列表

    Raises:
        ValueError: 图片验证失败或数量不足
    """
    print("正在验证图片文件...")

    if len(image_files) < 2:
        raise ValueError("至少需要2张图片才能创建过渡效果")

    for i, image_path in enumerate(image_files):
        print(f"正在验证图片 {i + 1}/{len(image_files)}: {Path(image_path).name}")
        validate_image_file(image_path)

    print("所有图片验证通过")


def get_sorted_image_files(
    images_folder: str, supported_formats: set = None
) -> List[str]:
    """获取图片文件夹中按数字排序的图片文件

    Args:
        images_folder: 图片文件夹路径
        supported_formats: 支持的图片格式集合，默认使用SUPPORTED_IMAGE_FORMATS

    Returns:
        List[str]: 排序后的图片文件路径列表

    Raises:
        ValueError: 没有找到支持的图片文件
    """
    if supported_formats is None:
        supported_formats = SUPPORTED_IMAGE_FORMATS

    print(f"正在扫描图片文件夹: {images_folder}")

    image_files = []
    for filename in os.listdir(images_folder):
        filepath = os.path.join(images_folder, filename)
        if os.path.isfile(filepath):
            ext = Path(filepath).suffix.lower()
            if ext in supported_formats:
                image_files.append(filepath)

    if not image_files:
        raise ValueError(
            f"图片文件夹中没有找到支持的图片文件。支持的格式: {supported_formats}"
        )

    # 按数字大小排序，确保1<2<11，数字相同的按文件名自然排序
    image_files.sort(
        key=lambda x: (extract_number_from_filename(Path(x).name), Path(x).name)
    )

    # 打印排序后的文件名
    print(f"找到 {len(image_files)} 张图片，按数字排序:")
    for i, filepath in enumerate(image_files):
        filename = Path(filepath).name
        number = extract_number_from_filename(filename)
        print(f"  {i + 1}. {filename} (数字: {number})")

    return image_files


def resize_image(
    src_path,
    dst_path,
    target_width,
    target_height,
    mode: str = "crop",
    background_color: str = "white",
):
    """把不同比例图片统一成特定尺寸

    :param str src_path: 源图片路径
    :param str dst_path: 目标图片路径
    :param int target_width: 目标宽度
    :param int target_height: 目标高度
    :param str mode: 模式，'crop'-裁剪，'pad'-留白
    :param str background_color: pad模式的背景色（默认："white"），支持颜色名称或十六进制
    """
    # 参数验证
    if target_width <= 0 or target_height <= 0:
        raise ValueError(
            f"目标宽度和高度必须大于0，当前值: width={target_width}, height={target_height}"
        )
    if mode not in ["crop", "pad"]:
        raise ValueError(f"模式必须是 'crop' 或 'pad'，当前值: {mode}")

    try:
        image = Image.open(src_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"源图片未找到: {src_path}")
    except Exception as e:
        raise IOError(f"打开图片时出错 {src_path}: {e}")

    # 检查是否为GIF动图
    is_animated_gif = False
    # 特殊处理MPO格式 - 强制作为静态图片处理
    if image.format != "MPO":
        try:
            is_animated_gif = hasattr(image, "n_frames") and image.n_frames > 1
        except Exception:
            pass

    # 如果是动画GIF，进行特殊处理
    if is_animated_gif:
        # 逐帧处理
        frames = []
        durations = []

        # 获取GIF的循环信息（如果有）
        loop_info = image.info.get("loop", 0)

        for i in range(image.n_frames):
            image.seek(i)
            frame = image.copy()
            width, height = frame.size

            # 计算原始和目标的长宽比
            ratio = width / height
            target_ratio = target_width / target_height

            # 根据不同的模式进行缩放和裁剪或留白
            if mode == "crop":
                # 裁剪模式
                if ratio > target_ratio:
                    # 原图过宽，先按照高度缩放，再裁剪左右两边多余部分
                    new_width = int(target_height * ratio)
                    new_frame = frame.resize((new_width, target_height))
                    left = (new_width - target_width) // 2
                    right = left + target_width
                    new_frame = new_frame.crop((left, 0, right, target_height))
                else:
                    # 原图过窄，先按照宽度缩放，再裁剪上下两边多余部分
                    new_height = int(target_width / ratio)
                    new_frame = frame.resize((target_width, new_height))
                    top = (new_height - target_height) // 2
                    bottom = top + target_height
                    new_frame = new_frame.crop((0, top, target_width, bottom))

            elif mode == "pad":
                # 留白模式
                if ratio > target_ratio:
                    # 原图过宽，先按照宽度缩放，再在上下两边填充背景
                    new_height = int(target_width / ratio)
                    new_frame = frame.resize((target_width, new_height))
                    bg_color = background_color
                    background = Image.new(
                        "RGB", (target_width, target_height), bg_color
                    )

                    # 将新图片粘贴到背景中间位置
                    top = (target_height - new_height) // 2
                    background.paste(new_frame, (0, top))
                    new_frame = background

                else:
                    # 原图过窄 ，先按照高度缩放 ，再在左右两边填充背景
                    new_width = int(target_height * ratio)
                    new_frame = frame.resize((new_width, target_height))
                    bg_color = background_color
                    background = Image.new(
                        "RGB", (target_width, target_height), bg_color
                    )

                    # 将新图片粘贴到背景中间位置
                    left = (target_width - new_width) // 2
                    background.paste(new_frame, (left, 0))
                    new_frame = background

            frames.append(new_frame)
            # 获取当前帧的持续时间
            durations.append(image.info.get("duration", 100))

        # 保存为GIF动画
        if frames:
            # 确保目标文件扩展名是.gif
            if not dst_path.lower().endswith(".gif"):
                dst_path = os.path.splitext(dst_path)[0] + ".gif"

            frames[0].save(
                dst_path,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=loop_info,
                optimize=False,
                disposal=2,
            )
            return

    width, height = image.size

    # 计算原始和目标的长宽比
    ratio = width / height
    target_ratio = target_width / target_height

    # 根据不同的模式进行缩放和裁剪或留白
    if mode == "crop":
        # 裁剪模式
        if ratio > target_ratio:
            # 原图过宽，先按照高度缩放，再裁剪左右两边多余部分
            new_width = int(target_height * ratio)
            new_image = image.resize((new_width, target_height))
            left = (new_width - target_width) // 2
            right = left + target_width
            new_image = new_image.crop((left, 0, right, target_height))
        else:
            # 原图过窄，先按照宽度缩放，再裁剪上下两边多余部分
            new_height = int(target_width / ratio)
            new_image = image.resize((target_width, new_height))
            top = (new_height - target_height) // 2
            bottom = top + target_height
            new_image = new_image.crop((0, top, target_width, bottom))

    elif mode == "pad":
        # 留白模式
        if ratio > target_ratio:
            # 原图过宽，先按照宽度缩放，再在上下两边填充背景
            new_height = int(target_width / ratio)
            new_image = image.resize((target_width, new_height))
            bg_color = background_color
            background = Image.new("RGB", (target_width, target_height), bg_color)

            # 将新图片粘贴到背景中间位置
            top = (target_height - new_height) // 2
            background.paste(new_image, (0, top))
            new_image = background

        else:
            # 原图过窄 ，先按照高度缩放 ，再在左右两边填充背景
            new_width = int(target_height * ratio)
            new_image = image.resize((new_width, target_height))
            bg_color = background_color
            background = Image.new("RGB", (target_width, target_height), bg_color)

            # 将新图片粘贴到背景中间位置
            left = (target_width - new_width) // 2
            background.paste(new_image, (left, 0))
            new_image = background

    # 输出文件
    new_image.save(dst_path)


def scale_image(src_path, dst_path, max_size, min_width, mode: str = "long"):
    """等比缩放图片，根据模式选择缩放长边或短边

    :param str src_path: 源图片路径
    :param str dst_path: 目标图片路径
    :param int max_size: 最大尺寸值
    :param int min_width: 长图的最小宽度（仅对纵向图片生效）
    :param str mode: 模式，'long'-长边缩放到最大值，'short'-短边缩放到最大值
    """
    # 参数验证
    if max_size <= 0:
        raise ValueError(f"最大尺寸必须大于0，当前值: {max_size}")
    if min_width < 0:
        raise ValueError(f"最小宽度不能小于0，当前值: {min_width}")
    if mode not in ["long", "short"]:
        raise ValueError(f"模式必须是 'long' 或 'short'，当前值: {mode}")

    try:
        image = Image.open(src_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"源图片未找到: {src_path}")
    except Exception as e:
        raise IOError(f"打开图片时出错 {src_path}: {e}")

    width, height = image.size

    # 特殊处理MPO格式 - 强制作为静态图片处理
    if image.format == "MPO":
        is_animated_gif = False
        # 防止除零错误
        if width <= 0 or height <= 0:
            raise ValueError(f"图片尺寸无效: width={width}, height={height}")

        # 确定长边和短边
        long_side = max(width, height)
        short_side = min(width, height)
    else:
        # 防止除零错误
        if width <= 0 or height <= 0:
            raise ValueError(f"图片尺寸无效: width={width}, height={height}")

        # 确定长边和短边
        long_side = max(width, height)
        short_side = min(width, height)

        # 检查是否为GIF动图
        is_animated_gif = False
        try:
            is_animated_gif = hasattr(image, "n_frames") and image.n_frames > 1
        except Exception:
            pass

    # 如果是动画GIF，检查是否需要处理
    if is_animated_gif:
        # 检查是否需要处理
        needs_processing = False

        # 模式long：只有长边大于max_size才需要处理
        if mode == "long":
            if long_side > max_size:
                needs_processing = True
            else:
                # 检查是否所有帧都不需要处理
                try:
                    for i in range(image.n_frames):
                        image.seek(i)
                        frame_width, frame_height = image.size
                        frame_long_side = max(frame_width, frame_height)
                        if frame_long_side > max_size:
                            needs_processing = True
                            break
                        # 检查是否需要调整最小宽度（仅对纵向图片）
                        if frame_height > frame_width and frame_width < min_width:
                            needs_processing = True
                            break
                except Exception:
                    needs_processing = True  # 如果检查失败，保守处理
        else:
            # 模式short：总是需要处理
            needs_processing = True

        if not needs_processing:
            # 直接复制原文件，避免不必要的重编码
            try:
                shutil.copy2(src_path, dst_path)
                # 验证文件是否成功复制
                if not os.path.exists(dst_path):
                    raise FileNotFoundError(f"复制文件失败: {dst_path}")
            except Exception as e:
                raise IOError(f"复制文件时出错 {src_path} -> {dst_path}: {e}")
            return

    # 如果是动画GIF，进行特殊处理
    if is_animated_gif:
        # 逐帧处理
        frames = []
        durations = []

        # 获取GIF的循环信息（如果有）
        loop_info = image.info.get("loop", 0)

        for i in range(image.n_frames):
            image.seek(i)
            frame = image.copy()
            width, height = frame.size

            # 防止除零错误
            if width <= 0 or height <= 0:
                raise ValueError(f"图片尺寸无效: width={width}, height={height}")

            # 确定长边和短边
            long_side = max(width, height)
            short_side = min(width, height)

            # 根据不同模式计算缩放比例
            if mode == "long":
                # 模式long：长边缩放到最大值
                if long_side > max_size:
                    ratio = max_size / long_side
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)

                    # 仅对纵向图片检查最小宽度
                    if height > width and new_width < min_width:
                        # 调整缩放后的宽度和高度（保持原比例）
                        new_width = min_width
                        new_height = int(min_width / width * height)

                    # 缩放图片
                    new_frame = frame.resize((new_width, new_height))
                else:
                    new_frame = frame

            elif mode == "short":
                # 模式short：短边缩放到最大值
                if short_side > max_size:
                    ratio = max_size / short_side
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                else:
                    # 如果短边小于最大值，则放大到最大值
                    ratio = max_size / short_side
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)

                # 仅对纵向图片检查最小宽度
                if height > width and new_width < min_width:
                    # 调整缩放后的宽度和高度（保持原比例）
                    new_width = min_width
                    new_height = int(min_width / width * height)

                # 缩放图片
                new_frame = frame.resize((new_width, new_height))
            else:
                new_frame = frame

            frames.append(new_frame)
            # 获取当前帧的持续时间
            durations.append(image.info.get("duration", 100))

        # 保存为GIF动画
        if frames:
            # 确保目标文件扩展名是.gif
            if not dst_path.lower().endswith(".gif"):
                dst_path = os.path.splitext(dst_path)[0] + ".gif"

            frames[0].save(
                dst_path,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=loop_info,
                optimize=False,
                disposal=2,
            )
            return

    # 静态图片处理逻辑
    # 检查是否需要处理（模式long且长边不超过最大值，且不违反最小宽度要求）
    if mode == "long" and long_side <= max_size:
        if not (height > width and width < min_width):
            # 不需要处理，直接复制原文件到目标路径
            try:
                shutil.copy2(src_path, dst_path)
                # 验证文件是否成功复制
                if not os.path.exists(dst_path):
                    raise FileNotFoundError(f"复制文件失败: {dst_path}")
            except Exception as e:
                raise IOError(f"复制文件时出错 {src_path} -> {dst_path}: {e}")
            return

    # 根据不同模式计算缩放比例
    if mode == "long":
        # 模式long：长边缩放到最大值
        if long_side > max_size:
            ratio = max_size / long_side
            new_width = int(width * ratio)
            new_height = int(height * ratio)

            # 仅对纵向图片检查最小宽度
            if height > width and new_width < min_width:
                # 调整缩放后的宽度和高度（保持原比例）
                new_width = min_width
                new_height = int(min_width / width * height)

            # 缩放图片
            image = image.resize((new_width, new_height))

    elif mode == "short":
        # 模式short：短边缩放到最大值
        if short_side > max_size:
            ratio = max_size / short_side
            new_width = int(width * ratio)
            new_height = int(height * ratio)
        else:
            # 如果短边小于最大值，则放大到最大值
            ratio = max_size / short_side
            new_width = int(width * ratio)
            new_height = int(height * ratio)

        # 仅对纵向图片检查最小宽度
        if height > width and new_width < min_width:
            # 调整缩放后的宽度和高度（保持原比例）
            new_width = min_width
            new_height = int(min_width / width * height)

        # 缩放图片
        image = image.resize((new_width, new_height))

    # 输出文件，明确指定格式
    file_ext = os.path.splitext(dst_path)[1].lower()

    try:
        # 确保图像转换为RGB模式（对于JPEG格式）
        if image.mode != "RGB":
            image = image.convert("RGB")

        if file_ext == ".jpg" or file_ext == ".jpeg":
            image.save(dst_path, format="JPEG", quality=95)
        elif file_ext == ".png":
            image.save(dst_path, format="PNG")
        elif file_ext == ".webp":
            image.save(dst_path, format="WEBP", quality=95)
        else:
            # 默认JPEG格式
            image.save(dst_path, format="JPEG", quality=95)

    except Exception as save_error:
        raise save_error


def calculate_tile_coordinates(
    src_path: str,
    tile_width: int,
    tile_height: int,
    x_tile_count: int,
    y_tile_count: int,
    x_tile_num: int,
    y_tile_num: int,
) -> tuple[int, int]:
    """
    计算在给定网格布局下，特定瓦片的左上角坐标。

    将源图片想象成一个大致的网格，由 x_tile_count * y_tile_count 个瓦片组成，
    每个瓦片的尺寸为 tile_width * tile_height。
    此函数计算第 (x_tile_num, y_tile_num) 个瓦片（基于1的索引）的左上角像素坐标 (x, y)。

    瓦片的分布是均匀的：
    - 第一个水平瓦片(x_tile_num=1)的左边缘与图像左边缘对齐 (x=0)。
    - 最后一个水平瓦片(x_tile_num=x_tile_count)的*左*边缘应使得其*右*边缘与图像右边缘对齐 (x=img_width-tile_width)。
    - 第一个垂直瓦片(y_tile_num=1)的上边缘与图像上边缘对齐 (y=0)。
    - 最后一个垂直瓦片(y_tile_num=y_tile_count)的*上*边缘应使得其*下*边缘与图像下边缘对齐 (y=img_height-tile_height)。
    中间瓦片的起始点均匀分布在这些边界之间。允许瓦片重叠或未覆盖整个图像。

    :param str src_path: 源图片路径。
    :param int tile_width: 每个瓦片的宽度。
    :param int tile_height: 每个瓦片的高度。
    :param int x_tile_count: 水平方向上的瓦片总数（必须 >= 2）。
    :param int y_tile_count: 垂直方向上的瓦片总数（必须 >= 2）。
    :param int x_tile_num: 所需瓦片的水平索引（1 到 x_tile_count）。
    :param int y_tile_num: 所需瓦片的垂直索引（1 到 y_tile_count）。
    :raises ValueError: 如果 tile_count < 2 或 tile_num 超出范围。
    :raises FileNotFoundError: 如果源图片未找到。
    :raises IOError: 如果打开图片时出错。
    :return: 一个包含计算出的 (x_coordinate, y_coordinate) 的元组。
    :rtype: tuple[int, int]
    """
    if x_tile_count < 2 or y_tile_count < 2:
        raise ValueError("x_tile_count 和 y_tile_count 必须大于等于 2")

    if not (1 <= x_tile_num <= x_tile_count):
        raise ValueError(f"x_tile_num ({x_tile_num}) 必须在 1 和 {x_tile_count} 之间")

    if not (1 <= y_tile_num <= y_tile_count):
        raise ValueError(f"y_tile_num ({y_tile_num}) 必须在 1 和 {y_tile_count} 之间")

    try:
        # 确保在使用 Image 对象后关闭它
        with Image.open(src_path) as image:
            img_width, img_height = image.size
    except FileNotFoundError:
        raise FileNotFoundError(f"源图片未找到: {src_path}")
    except Exception as e:
        raise IOError(f"打开图片时出错 {src_path}: {e}")

    # 如果图像尺寸小于瓦片尺寸，无法进行有效分布，或者计算会出错
    if img_width < tile_width or img_height < tile_height:
        raise ValueError(
            f"图像尺寸 ({img_width}x{img_height}) 小于瓦片尺寸 ({tile_width}x{tile_height})"
        )

    # 计算水平方向上相邻瓦片起点的间距
    # (img_width - tile_width) 是第一个瓦片起点(0)到最后一个瓦片起点(img_width - tile_width)的总距离
    # 这个总距离被 (x_tile_count - 1) 个间隔平分
    # 确保除数不为零 (虽然前面已检查 x_tile_count >= 2，这里更健壮)
    spacing_x = (img_width - tile_width) / (x_tile_count - 1) if x_tile_count > 1 else 0

    # 计算垂直方向上相邻瓦片起点的间距
    spacing_y = (
        (img_height - tile_height) / (y_tile_count - 1) if y_tile_count > 1 else 0
    )

    # 计算目标瓦片左上角的坐标 (使用基于0的索引进行计算，所以用 tile_num - 1)
    # 使用 round() 进行四舍五入，以获得更居中的分布感觉
    x_coordinate = round((x_tile_num - 1) * spacing_x)
    y_coordinate = round((y_tile_num - 1) * spacing_y)

    # 确保坐标不会因为浮点数精度问题或round导致最后一个瓦片稍微超出边界
    # 最后一个瓦片的起点不应超过 img_width - tile_width 或 img_height - tile_height
    if x_tile_num == x_tile_count:
        x_coordinate = img_width - tile_width
    if y_tile_num == y_tile_count:
        y_coordinate = img_height - tile_height

    # 同样确保第一个瓦片的起点正好是0
    if x_tile_num == 1:
        x_coordinate = 0
    if y_tile_num == 1:
        y_coordinate = 0

    return x_coordinate, y_coordinate


def crop_image_by_size(
    src_path, dst_path, crop_width, crop_height, x_coordinate, y_coordinate
):
    """从图片里裁剪出特定尺寸的一块

    :param str src_path: 源图片路径
    :param str dst_path: 目标图片路径
    :param int crop_width: 裁剪区域的宽度
    :param int crop_height: 裁剪区域的高度
    :param int x_coordinate: 裁剪区域左上角相对于原图的x坐标
    :param int y_coordinate: 裁剪区域左上角相对于原图的y坐标
    """
    # 打开源图片
    image = Image.open(src_path)
    width, height = image.size

    # 创建一个目标尺寸的白色背景画布
    # 如果源图片有alpha通道，则创建带alpha通道的透明背景
    if image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    ):
        background = Image.new("RGBA", (crop_width, crop_height), (0, 0, 0, 0))
    else:
        background = Image.new("RGB", (crop_width, crop_height), "white")

    # 计算实际需要从原图中裁剪的区域 (crop_box on source image)
    # 这个区域的坐标是相对于原图左上角的
    src_crop_left = max(0, x_coordinate)
    src_crop_top = max(0, y_coordinate)
    src_crop_right = min(width, x_coordinate + crop_width)
    src_crop_bottom = min(height, y_coordinate + crop_height)

    # 计算实际裁剪出的内容的尺寸
    actual_crop_width = src_crop_right - src_crop_left
    actual_crop_height = src_crop_bottom - src_crop_top

    # 如果实际裁剪区域有效（宽高都大于0）
    if actual_crop_width > 0 and actual_crop_height > 0:
        # 从原图中裁剪出这部分
        cropped_region = image.crop(
            (src_crop_left, src_crop_top, src_crop_right, src_crop_bottom)
        )

        # 计算这部分应该粘贴到背景画布的哪个位置
        # 如果指定的裁剪区域左上角在原图外部（负坐标），则粘贴位置需要调整
        paste_x = max(0, -x_coordinate)
        paste_y = max(0, -y_coordinate)

        # 将裁剪出的区域粘贴到背景画布上
        if (
            hasattr(cropped_region, "size")
            and cropped_region.size
            and hasattr(cropped_region, "paste")
        ):
            try:
                background.paste(cropped_region, (paste_x, paste_y))
            except ValueError:
                # 如果paste方法失败，尝试使用4-item box格式
                box = (
                    paste_x,
                    paste_y,
                    paste_x + cropped_region.size[0],
                    paste_y + cropped_region.size[1],
                )
                background.paste(cropped_region, box)

    # 输出文件
    background.save(dst_path)


def paste_image(
    src_path1: str, src_path2: str, dst_path: str, x_coordinate: int, y_coordinate: int
):
    """
    将一张图片 (src1) 粘贴到另一张图片 (src2) 的指定坐标上。

    如果 src1 超出 src2 的边界，超出部分将被裁剪。
    如果 src1 具有透明度，将使用 alpha 混合粘贴。

    :param str src_path1: 要粘贴的顶层图片路径。
    :param str src_path2: 背景图片路径。
    :param str dst_path: 保存结果图片的路径。
    :param int x_coordinate: src1 左上角在 src2 上的 x 坐标 (可以为负)。
    :param int y_coordinate: src1 左上角在 src2 上的 y 坐标 (可以为负)。
    :raises FileNotFoundError: 如果任一源文件未找到。
    :raises IOError: 如果打开或处理图片时出错。
    """
    try:
        # 使用 with 语句确保文件被正确关闭
        with Image.open(src_path1) as img1, Image.open(src_path2) as img2:
            # 确保图像对象有size属性
            if not hasattr(img1, "size") or not img1.size:
                raise ValueError(f"无法获取图像 '{src_path1}' 的尺寸信息")
            if not hasattr(img2, "size") or not img2.size:
                raise ValueError(f"无法获取图像 '{src_path2}' 的尺寸信息")

            w1, h1 = img1.size
            w2, h2 = img2.size
            mode1 = img1.mode

            # 检查顶层图片 img1 是否有 alpha 通道
            has_alpha1 = mode1 in ("RGBA", "LA") or (
                mode1 == "P" and "transparency" in img1.info
            )

            # 准备背景图片作为基础
            # 如果顶层图片有 alpha，确保基础图片是 RGBA 模式以进行混合
            if has_alpha1:
                result_image = (
                    img2.convert("RGBA") if img2.mode != "RGBA" else img2.copy()
                )
            else:
                # 如果顶层图片不透明，直接复制背景（Pillow 的 paste 可以处理模式）
                result_image = img2.copy()

            # --- 计算裁剪和粘贴区域 ---

            # 1. 计算 img1 需要被裁剪的区域 (crop box on img1)
            #    这部分的坐标是相对于 img1 左上角的 (0,0)
            crop_x_start = max(0, -x_coordinate)
            crop_y_start = max(0, -y_coordinate)
            #    结束坐标：考虑 img1 尺寸以及它在 img2 上的右/下边界
            crop_x_end = min(w1, w2 - x_coordinate)
            crop_y_end = min(h1, h2 - y_coordinate)

            # 2. 计算实际需要裁剪的宽度和高度
            crop_width = crop_x_end - crop_x_start
            crop_height = crop_y_end - crop_y_start

            # 3. 计算裁剪出的区域应该粘贴到 result_image 的哪个位置
            #    这部分的坐标是相对于 result_image 左上角的 (0,0)
            paste_x = max(0, x_coordinate)
            paste_y = max(0, y_coordinate)

            # --- 执行裁剪和粘贴 ---

            # 仅当存在有效的重叠区域时执行操作
            if crop_width > 0 and crop_height > 0:
                # 从 img1 裁剪出需要粘贴的部分
                region_to_paste = img1.crop(
                    (crop_x_start, crop_y_start, crop_x_end, crop_y_end)
                )

                # 准备蒙版 (mask) - 仅当顶层图片有 alpha 时需要
                mask = None
                if has_alpha1:
                    # 确保裁剪出的区域也是 RGBA 模式，然后提取 alpha 通道作为蒙版
                    # L mode P mode RGBA mode
                    if region_to_paste.mode not in ("RGBA", "LA"):
                        region_to_paste = region_to_paste.convert("RGBA")
                    mask = region_to_paste.split()[-1]  # 获取 alpha 通道

                # 将裁剪出的区域粘贴到背景图片上
                result_image.paste(region_to_paste, (paste_x, paste_y), mask)

            # 保存最终结果
            # Pillow 会根据文件扩展名选择格式，通常能正确处理模式
            # 对于不支持 alpha 的格式（如 JPG），透明度会丢失（通常变为白色或黑色）
            result_image.save(dst_path)

    except FileNotFoundError as e:
        # 提供更明确的错误信息，指出哪个文件未找到
        missing_file = src_path1 if not os.path.exists(src_path1) else src_path2
        raise FileNotFoundError(f"源文件未找到: {missing_file}") from e
    except Exception as e:
        raise IOError(f"处理图片 '{src_path1}' 或 '{src_path2}' 时出错: {e}") from e


def set_image_ppi(src_path, dst_path, target_ppi=300):
    """调整图片的PPI（每英寸像素数），保持总像素数不变，支持JPEG和TIFF格式

    :param str src_path: 源图片路径
    :param str dst_path: 目标图片路径
    :param int target_ppi: 目标PPI值，默认300
    """
    # 打开图片
    image = Image.open(src_path)

    # 获取图片当前的像素尺寸
    width_px, height_px = image.size

    # 计算新的物理尺寸（英寸）
    width_inch = width_px / target_ppi
    height_inch = height_px / target_ppi

    # 准备DPI信息（在PIL中，dpi和ppi是一样的）
    dpi = (target_ppi, target_ppi)

    # 保存图片，设置新的DPI
    # 注意：不同格式对DPI信息的支持不同，JPEG、TIFF等支持，PNG可能不支持
    image.save(dst_path, dpi=dpi)


def compress_to_webp(src_path, dst_path, quality=85):
    """压缩图片为webp格式，支持多种源格式

    :param str src_path: 源图片路径
    :param str dst_path: 目标图片路径
    :param int quality: 压缩质量(1-100)，数值越小压缩率越高，画质越低
    :return: 包含压缩前后信息的字典
    :rtype: dict
    """
    # 获取原始文件大小(KB)
    original_size = os.path.getsize(src_path) / 1024

    # 打开图片
    image = Image.open(src_path)
    img_format = image.format  # 保存原始格式

    # 获取文件扩展名
    file_ext = os.path.splitext(dst_path)[1].lower()
    if not file_ext:
        file_ext = os.path.splitext(src_path)[1].lower()
        dst_path = dst_path + file_ext

    # 检查是否为GIF动图
    is_animated_gif = False
    # 特殊处理MPO格式 - 强制作为静态图片处理
    if (img_format == "GIF" or file_ext == ".gif") and img_format != "MPO":
        try:
            is_animated_gif = hasattr(image, "n_frames") and image.n_frames > 1
        except Exception:
            pass

    # GIF动图不压缩
    if is_animated_gif:
        # GIF动图直接复制，不改变格式也不压缩
        try:
            shutil.copy2(src_path, dst_path)
            # 验证文件是否成功复制
            if not os.path.exists(dst_path):
                raise FileNotFoundError(f"复制文件失败: {dst_path}")
        except Exception as e:
            raise IOError(f"复制文件时出错 {src_path} -> {dst_path}: {e}")

        # 获取复制后文件大小(KB)
        compressed_size = os.path.getsize(dst_path) / 1024

        # 返回信息，保持与其他格式相同的结构
        result = {
            "original_path": src_path,
            "compressed_path": dst_path,
            "original_size": round(original_size, 2),
            "compressed_size": round(compressed_size, 2),
            "compression_ratio": 0.0,  # 没有压缩，比例为0
            "quality": quality,
        }

        return result

    # 根据不同格式设置保存参数
    save_args = {}

    # 判断是否需要转换为webp
    if (
        img_format == "WEBP"
        or file_ext == ".webp"
        or img_format == "AVIF"
        or file_ext == ".avif"
    ):
        # 对于已经是webp或avif的图片，保持原格式
        if img_format == "WEBP" or file_ext == ".webp":
            save_args = {
                "format": "WEBP",
                "quality": quality,
                "method": 6,  # 压缩方法，值越大压缩率越高但速度越慢(0-6)
            }
        elif img_format == "AVIF" or file_ext == ".avif":
            try:
                save_args = {"format": "AVIF", "quality": quality}
            except Exception as e:
                print(f"AVIF格式可能不被当前Pillow版本支持: {e}")
                # 如果不支持AVIF，转为WEBP
                save_args = {"format": "WEBP", "quality": quality, "method": 6}
                dst_path = os.path.splitext(dst_path)[0] + ".webp"
    else:
        # 对于其他所有格式，转换为WEBP
        save_args = {
            "format": "WEBP",
            "quality": quality,
            "method": 6,  # 压缩方法，值越大压缩率越高但速度越慢(0-6)
        }
        # 修改目标文件扩展名为.webp
        dst_path = os.path.splitext(dst_path)[0] + ".webp"

    # 对于RGBA图像，转换为RGB格式以避免兼容性问题
    if image.mode == "RGBA":
        image = image.convert("RGB")

    # 保存压缩后的图片
    image.save(dst_path, **save_args)

    # 获取压缩后文件大小(KB)
    compressed_size = os.path.getsize(dst_path) / 1024

    # 计算压缩率
    compression_ratio = (
        (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
    )

    # 返回压缩结果信息
    result = {
        "original_path": src_path,
        "compressed_path": dst_path,
        "original_size": round(original_size, 2),
        "compressed_size": round(compressed_size, 2),
        "compression_ratio": round(compression_ratio, 2),
        "quality": quality,
    }

    return result


def gif_2_frames(src_path, dst_path):
    """将GIF转换为帧图片

    :param str src_path: 源GIF文件夹路径
    :param str dst_path: 目标帧图片文件夹路径
    """
    # 判断源文件夹有1个还是多个gif图片
    gif_count = 0
    for filename in os.listdir(src_path):
        src_format = (os.path.splitext(filename)[1])[1:]
        if src_format in ["gif"]:
            gif_count += 1

    # 遍历输入文件夹中的图片
    for filename in os.listdir(src_path):
        # 忽略隐藏文件和文件夹
        if filename.startswith("."):
            continue
        src_format = (os.path.splitext(filename)[1])[1:]
        if src_format in ["gif"]:
            # 打开图片并获取动画帧
            gif_path = os.path.join(src_path, filename)
            image = Image.open(gif_path)
            frames = image.n_frames

            # 根据源文件夹gif图片数量，分情况建立输出目录
            if gif_count > 1:
                frame_path = os.path.join(dst_path, os.path.splitext(filename)[0])
            else:
                frame_path = dst_path
            if not os.path.exists(frame_path):
                os.mkdir(frame_path)

            # 输出文件
            for i in range(frames):
                image.seek(i)
                frame_file_path = os.path.join(
                    frame_path, f"{os.path.splitext(filename)[0]}_{i}.png"
                )
                image.save(frame_file_path)

            # 打印输出结果
            if os.path.exists(frame_path):
                print(f"{gif_path} converted")
            else:
                print(f"Failed to convert {gif_path}")


def frames_2_gif(src_path, dst_path, duration=100, loop=1):
    """将帧图片转换为GIF

    :param str src_path: 源帧图片文件夹路径
    :param str dst_path: 目标GIF文件夹路径
    :param int duration: 帧间隔时间（毫秒）
    :param int loop: 是否循环播放（1为是，0为否）
    """
    # 遍历输入文件夹中的图片
    images = []
    for filename in os.listdir(src_path):
        # 忽略隐藏文件和文件夹
        if filename.startswith("."):
            continue
        src_format = (os.path.splitext(filename)[1])[1:]
        if src_format in ["jpg", "jpeg", "png", "bmp"]:
            # 打开图片并获取动画帧
            frame_path = os.path.join(src_path, filename)
            try:
                image = Image.open(frame_path)
                images.append(image)
            except Exception as e:
                print(f"Failed to open {frame_path}: {e}")

    # 按文件名数字顺序排列
    images.sort(key=lambda x: extract_number_from_filename(x.filename))

    # 检查图片尺寸是否一致
    size_set = set([img.size for img in images])
    if len(size_set) > 1:
        print("Error: Images have different sizes")
        return

    # 检查是否有图片被加载
    if not images:
        print("Error: No images found in the source directory")
        return

    # 拼合图片序列成gif动画
    duration = int(duration)
    loop = int(loop)
    images[0].save(
        os.path.join(dst_path, "output.gif"),
        save_all=True,
        optimize=False,
        compress_level=0,
        append_images=images[1:],
        duration=duration,
        loop=loop,
    )

    # 打印输出结果
    gif_path = os.path.join(dst_path, "output.gif")
    if os.path.exists(gif_path):
        print(f"{src_path} converted to gif")
    else:
        print(f"Failed to convert {src_path}")


def random_background_color(src_path, dst_path, bg_colors):
    """为透明背景PNG图片加上随机纯色背景

    :param str src_path: 源图片路径
    :param str dst_path: 目标图片路径
    :param list bg_colors: 背景色列表
    """
    # 打开原始图片
    src_image = Image.open(src_path)

    # 检查图像是否为RGBA模式
    if src_image.mode != "RGBA":
        print("图像不是RGBA模式，无法添加背景色")
        return

    # 转换为RGBA模式
    src_image = src_image.convert("RGBA")

    # 确保图像有有效的size属性
    if not hasattr(src_image, "size") or not src_image.size:
        raise ValueError(f"无法获取图像 '{src_path}' 的尺寸信息")

    # 确保size是元组类型
    if not isinstance(src_image.size, tuple):
        raise ValueError(f"图像尺寸信息格式错误: {src_image.size}")

    # 随机选择一个背景色
    bg_color = random.choice(bg_colors)

    # 创建新的图片，设置背景色
    new_image = Image.new("RGBA", src_image.size, bg_color)

    # 将原始图片粘贴到新的图片上
    new_image.paste(src_image, (0, 0), src_image)

    # 输出文件
    new_image.save(dst_path)


@dataclass
class ImageFingerprint:
    """存储单个图片的指纹和元数据。"""

    path: Path
    size_bytes: int
    width: int
    height: int
    phash: str
    dhash: str
    color_hist: np.ndarray = field(default=None, repr=False)

    @property
    def pixels(self) -> int:
        return self.width * self.height

    @property
    def resolution_str(self) -> str:
        return f"{self.width}×{self.height}"


def calculate_color_histogram(img: Image.Image, bins: int = 16) -> np.ndarray:
    """计算归一化的颜色直方图。"""
    img_array = np.array(img)
    # 处理 2 维数组（灰度图）或 4 维（带 Alpha）
    if len(img_array.shape) == 2:
        img_array = np.stack([img_array] * 3, axis=-1)
    elif len(img_array.shape) == 3 and img_array.shape[2] > 3:
        img_array = img_array[:, :, :3]

    hist = []
    for i in range(3):  # R, G, B 通道
        h, _ = np.histogram(img_array[:, :, i], bins=bins, range=(0, 256))
        hist.extend(h)
    hist = np.array(hist, dtype=np.float32)
    hist = hist / (hist.sum() + 1e-6)  # 归一化
    return hist


def get_image_fingerprint(
    image_path: str, hash_size: int = 16
) -> Optional[ImageFingerprint]:
    """获取图片的视觉指纹（Hash + Histogram）及元数据。"""
    try:
        # 使用统一函数进行验证（格式支持、存在性、完整性）
        validate_image_file(image_path)
        
        path = Path(image_path)
        with Image.open(path) as img:
            # 如有必要，转换为 RGB
            if img.mode not in ("RGB",):
                img = img.convert("RGB")

            width, height = img.size
            # 计算哈希
            phash = str(imagehash.phash(img, hash_size=hash_size))
            dhash = str(imagehash.dhash(img, hash_size=hash_size))
            # 计算颜色直方图
            color_hist = calculate_color_histogram(img)

            return ImageFingerprint(
                path=path,
                size_bytes=path.stat().st_size,
                width=width,
                height=height,
                phash=phash,
                dhash=dhash,
                color_hist=color_hist,
            )
    except Exception as e:
        print(f"  [ERROR] 无法处理图片 {image_path}: {e}")
        return None


def hamming_distance(hash1: str, hash2: str) -> int:
    """计算两个哈希之间的汉明距离。"""
    if len(hash1) != len(hash2):
        return float("inf")
    return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))


def histogram_similarity(hist1: np.ndarray, hist2: np.ndarray) -> float:
    """计算直方图相交相似度 (0-1)。"""
    return np.minimum(hist1, hist2).sum()


def find_similar_image_groups(
    images: List[ImageFingerprint], threshold: int = 6, crop_similarity: float = 0.85
) -> List[List[ImageFingerprint]]:
    """
    使用严格簇匹配对相似图片进行分组：
    1. 不再使用并查集（防止 A像B, B像C 导致 A,B,C 链式归为一组）
    2. 每张图作为簇心，寻找与其极度接近的”副本”
    """
    n = len(images)
    processed = [False] * n
    groups = []

    # 预先按分辨率降序排列，保证簇心是最高质量的那张
    sorted_indices = sorted(range(n), key=lambda i: (images[i].pixels, images[i].size_bytes), reverse=True)

    for i in sorted_indices:
        if processed[i]:
            continue

        current_group = [images[i]]
        processed[i] = True

        for j in sorted_indices:
            if processed[j]:
                continue

            # 第一阶段：Hash 严格匹配
            phash_dist = hamming_distance(images[i].phash, images[j].phash)
            dhash_dist = hamming_distance(images[i].dhash, images[j].dhash)

            # 第二阶段：直方图严格匹配
            sim = histogram_similarity(images[i].color_hist, images[j].color_hist)

            # 必须同时满足 Hash 相似且直方图极高相似，才判定为”同一张图的副本”
            # 或者 Hash 极度接近 (距离 <= 2)
            is_duplicate = (
                (phash_dist <= threshold and dhash_dist <= threshold and sim >= crop_similarity) or
                (phash_dist <= 2 or dhash_dist <= 2)
            )

            if is_duplicate:
                current_group.append(images[j])
                processed[j] = True

        if len(current_group) > 1:
            groups.append(current_group)

    return groups


def detect_faces(image_path: str, min_face_size: int = 100) -> Optional[tuple]:
    """
    使用 OpenCV Haar Cascade 检测图片中的人脸

    Args:
        image_path: 图片文件路径
        min_face_size: 最小人脸尺寸（默认100）

    Returns:
        Optional[tuple]: (center_x, center_y, radius) 如果检测到人脸
                        None 如果未检测到人脸或加载失败
    """
    try:
        import cv2
    except ImportError:
        print("[ERROR] 需要安装 opencv-python: pip install opencv-python")
        return None

    # 直接读取图片（支持中文路径）
    img_cv = cv2.imread(image_path)
    if img_cv is None:
        print(f"[ERROR] 无法读取图片: {image_path}")
        return None

    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # 加载人脸识别模型
    face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(face_cascade_path)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(min_face_size, min_face_size)
    )

    h_orig, w_orig = img_cv.shape[:2]

    if len(faces) == 0:
        # 未检测到人脸，返回中心裁剪
        center_x = w_orig // 2
        center_y = h_orig // 2
        radius = min(w_orig, h_orig) // 2
    else:
        # 取最大的人脸
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        x, y, w_face, h_face = faces[0]

        center_x = x + w_face // 2
        center_y = y + h_face // 2

        # 人脸高度占圆直径的比例，约 55%
        radius = int(h_face / 1.1)

        # 稍微下移中心点（即裁剪框上移），保留头发部分
        center_y += int(h_face * 0.05)

        # 如果裁剪框超出了顶部边界，则向下偏移以尽量保留头发
        if center_y - radius < 0:
            center_y = radius

    # 确保返回 Python int 类型（而不是 numpy.int32）
    return (int(center_x), int(center_y), int(radius))
