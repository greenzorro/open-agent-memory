"""
File: ocr.py
Project: routine
Created: 2025-01-15
Author: Victor Cheng
Email: hi@victor42.work
Description: OCR工具函数模块，基于RapidOCR实现图片文字识别
"""

import os
from typing import List, Union, Optional, Tuple
from pathlib import Path
from PIL import Image
import numpy as np

try:
    from rapidocr_onnxruntime import RapidOCR
except ImportError:
    RapidOCR = None


class OCRError(Exception):
    """OCR相关异常"""
    pass


class OCRWrapper:
    """RapidOCR封装类"""

    def __init__(self):
        self._ocr = None
        self._initialize_ocr()

    def _initialize_ocr(self):
        """初始化OCR引擎"""
        try:
            self._ocr = RapidOCR()
        except Exception as e:
            raise OCRError(f"OCR引擎初始化失败: {e}")

    @property
    def engine(self):
        """获取OCR引擎实例"""
        if self._ocr is None:
            self._initialize_ocr()
        return self._ocr


# 全局OCR实例
_ocr_instance = None


def _get_ocr_instance() -> OCRWrapper:
    """获取全局OCR实例"""
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = OCRWrapper()
    return _ocr_instance


def _process_batch_images(image_inputs: List[Union[str, Path, Image.Image, np.ndarray]],
                          processor_func, batch_size: Optional[int] = None,
                          error_context: str = "批量OCR") -> List:
    """公共批处理逻辑

    Args:
        image_inputs: 图片输入列表
        processor_func: 处理函数，用于处理单张图片
        batch_size: 批处理大小
        error_context: 错误上下文描述

    Returns:
        List: 处理结果列表

    Raises:
        OCRError: OCR识别失败时抛出
    """
    if not image_inputs:
        return []

    # 设置批处理大小
    if batch_size is None:
        batch_size = len(image_inputs)

    results = []

    # 分批处理
    for i in range(0, len(image_inputs), batch_size):
        batch = image_inputs[i:i + batch_size]

        for j, image_input in enumerate(batch):
            try:
                # 处理单张图片
                result = processor_func(image_input)
                results.append(result)

            except Exception as e:
                # 单张图片失败时抛出异常
                raise OCRError(f"{error_context}第{i+j+1}张图片处理失败: {e}")

    return results


def _validate_image_input(image_input: Union[str, Path, Image.Image, np.ndarray]) -> Union[str, Image.Image, np.ndarray]:
    """验证并标准化图片输入"""
    # 检查PIL Image
    if isinstance(image_input, Image.Image):
        return image_input

    # 检查numpy数组
    elif isinstance(image_input, np.ndarray):
        return image_input

    # 检查字符串或Path
    elif isinstance(image_input, (str, Path)):
        image_path = str(image_input)

        # 检查文件是否存在
        if not os.path.exists(image_path):
            raise OCRError(f"图片文件不存在: {image_path}")

        # 检查是否为文件
        if not os.path.isfile(image_path):
            raise OCRError(f"路径不是文件: {image_path}")

        # 检查文件扩展名
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in valid_extensions:
            raise OCRError(f"不支持的图片格式: {ext}")

        return image_path

    else:
        raise OCRError(f"不支持的图片输入类型: {type(image_input)}")


def extract_text_from_image(image_input: Union[str, Path, Image.Image, np.ndarray]) -> str:
    """从图片中提取文字

    Args:
        image_input: 图片输入，支持文件路径、PIL Image、numpy数组

    Returns:
        str: 识别的文字内容

    Raises:
        OCRError: OCR识别失败时抛出
    """
    try:
        # 验证输入
        validated_input = _validate_image_input(image_input)

        # 获取OCR实例
        ocr_wrapper = _get_ocr_instance()
        ocr_engine = ocr_wrapper.engine

        # 执行OCR识别
        result, _ = ocr_engine(validated_input)

        if not result:
            return ""

        # 提取文字内容
        text_lines = []
        for line in result:
            if len(line) >= 2 and line[1]:  # 确保有文字内容
                text_lines.append(line[1].strip())

        text_content = "\n".join(text_lines)

        return text_content

    except Exception as e:
        if isinstance(e, OCRError):
            raise
        else:
            raise OCRError(f"OCR识别失败: {e}")


def extract_text_with_boxes(image_input: Union[str, Path, Image.Image, np.ndarray]) -> List[Tuple[List[List[float]], str, float]]:
    """从图片中提取文字和坐标信息

    Args:
        image_input: 图片输入，支持文件路径、PIL Image、numpy数组

    Returns:
        List[Tuple]: 包含坐标和文字的列表，格式为[(box, text, confidence), ...]
        其中box是4个坐标点[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]的列表

    Raises:
        OCRError: OCR识别失败时抛出
    """
    try:
        # 验证输入
        validated_input = _validate_image_input(image_input)

        # 获取OCR实例
        ocr_wrapper = _get_ocr_instance()
        ocr_engine = ocr_wrapper.engine

        # 执行OCR识别
        result, _ = ocr_engine(validated_input)

        if not result:
            return []

        # 格式化结果
        formatted_results = []
        for line in result:
            if len(line) >= 3:  # 确保有完整信息：box, text, confidence
                box, text, confidence = line[0], line[1], line[2]
                if text:  # 只返回有文字内容的结果
                    formatted_results.append((box, text.strip(), confidence))

        return formatted_results

    except Exception as e:
        if isinstance(e, OCRError):
            raise
        else:
            raise OCRError(f"OCR识别失败: {e}")


def batch_ocr_images(image_inputs: List[Union[str, Path, Image.Image, np.ndarray]],
                    batch_size: Optional[int] = None) -> List[str]:
    """批量处理多张图片的OCR识别

    Args:
        image_inputs: 图片输入列表，支持文件路径、PIL Image、numpy数组
        batch_size: 批处理大小，None表示不限制，默认设置为None

    Returns:
        List[str]: 识别结果列表，顺序与输入一致

    Raises:
        OCRError: OCR识别失败时抛出
    """
    return _process_batch_images(image_inputs, extract_text_from_image, batch_size, "批量OCR")


def batch_extract_text_with_boxes(image_inputs: List[Union[str, Path, Image.Image, np.ndarray]],
                                 batch_size: Optional[int] = None) -> List[List[Tuple]]:
    """批量处理多张图片的OCR识别，返回坐标信息

    Args:
        image_inputs: 图片输入列表，支持文件路径、PIL Image、numpy数组
        batch_size: 批处理大小，None表示不限制，默认设置为None

    Returns:
        List[List[Tuple]]: 每张图片的识别结果列表，格式为[[(box, text, confidence), ...], ...]
        顺序与输入一致

    Raises:
        OCRError: OCR识别失败时抛出
    """
    return _process_batch_images(image_inputs, extract_text_with_boxes, batch_size, "批量OCR带坐标")





