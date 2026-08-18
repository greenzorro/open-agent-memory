"""
File: random_video_mixer.py
Project: routine
Created: 2025-10-22 01:32:14
Author: Victor Cheng
Email: hi@victor42.work
Description:
随机视频拼接脚本 - 重构版
采用职责分离的设计模式，解决单一职责问题
"""

import os
import sys
import random
import subprocess
import json
import argparse
from typing import List, Optional
import time

current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(current_dir))

from utils.basic import get_param_value, sanitize_file_name_string
from utils.path import HOME, PATH_DOWNLOADS, PATH_DOWNLOADS_FROM_WIN, platform_type

# =============================================================================
# 视频处理常量配置
# =============================================================================

# 目标分辨率
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

# 随机变换参数范围
SCALE_FACTOR_RANGE = (1.0, 1.15)  # 缩放范围
SPEED_FACTOR_RANGE = (0.95, 1.2)  # 变速范围

# 视频截取设置
MAX_SEGMENT_DURATION = 10.0  # 最大片段时长（秒）

# 色彩调整参数范围
BRIGHTNESS_RANGE = (-0.1, 0.1)  # 亮度调整范围（FFmpeg eq滤镜范围：-1.0到1.0）
CONTRAST_RANGE = (0.9, 1.1)  # 对比度调整范围（FFmpeg eq滤镜范围：-2.0到2.0）
SATURATION_RANGE = (0.9, 1.15)  # 饱和度调整范围（FFmpeg eq滤镜范围：0.0到3.0）
HUE_SHIFT_RANGE = (-0.05, 0.05)  # 色调偏移范围（弧度）

# 效果应用概率（0-1之间）
FLIP_EFFECT_PROBABILITY = 0.5  # 50%概率应用左右翻转
COLOR_EFFECT_PROBABILITY = 0.8  # 80%概率应用色彩效果
HUE_EFFECT_PROBABILITY = 0.8  # 80%概率应用色调偏移

# 路径配置
SOURCE_DIR_WINDOWS = "D:\\混剪视频素材"


# 根据用户名动态设置macOS路径
def get_macos_source_dir():
    """根据当前用户名设置macOS视频素材目录路径"""
    current_user = os.path.basename(HOME)
    if current_user == "colachan":
        # 如果是colachan用户，使用HOME + Movies路径
        return os.path.join(HOME, "Movies", "混剪视频素材")
    elif current_user == "tangyinxiao19":
        # 如果是tangyinxiao19用户，使用移动硬盘路径
        return "/Volumes/KESU33/推文变现/混剪视频素材"
    else:
        # 其他用户，使用默认的Movies路径
        return os.path.join(HOME, "Movies", "混剪视频素材")


SOURCE_DIR_MACOS = get_macos_source_dir()
SOURCE_DIR_LINUX = "/mnt/d/混剪视频素材"
TEMP_DIR_NAME = "temp"
OUTPUT_DIR = PATH_DOWNLOADS


class VideoSource:
    """视频源管理类 - 负责查找和管理视频文件"""

    def __init__(self, source_dir: str):
        self.source_dir = source_dir

    def get_category_directories(self) -> List[str]:
        """获取素材目录下的所有子目录（分类）"""
        try:
            if not os.path.exists(self.source_dir):
                print(f"素材目录不存在: {self.source_dir}")
                return []

            categories = []
            for item in os.listdir(self.source_dir):
                item_path = os.path.join(self.source_dir, item)
                if os.path.isdir(item_path):
                    categories.append(item)

            # 按名称排序
            categories.sort()
            return categories
        except Exception as e:
            print(f"获取分类目录失败: {e}")
            return []

    def find_all_videos(self, category: str = None) -> List[str]:
        """递归查找所有视频文件"""
        search_dir = self.source_dir
        if category:
            search_dir = os.path.join(self.source_dir, category)

        video_files = []
        print(f"正在搜索视频文件...")

        for root, dirs, files in os.walk(search_dir):
            for file in files:
                if file.lower().endswith(
                    (".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv")
                ):
                    # 跳过macOS隐藏文件
                    if not file.startswith("._"):
                        file_path = os.path.join(root, file)
                        video_files.append(file_path)

        print(f"找到 {len(video_files)} 个视频文件")
        return video_files

    def get_video_duration(self, video_path: str) -> float:
        """获取视频时长（秒）"""
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            video_path,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            # 优先从视频流获取时长
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    return float(stream.get("duration", 0))

            # 如果视频流没有时长信息，从格式获取
            return float(data.get("format", {}).get("duration", 0))
        except Exception as e:
            print(f"获取视频时长失败 {video_path}: {e}")
            return 0.0

    def shuffle_videos(self, videos: List[str]) -> List[str]:
        """随机打乱视频顺序"""
        shuffled = videos.copy()
        random.shuffle(shuffled)
        return shuffled


class VideoTransformer:
    """视频变换器 - 负责应用随机变换"""

    def __init__(
        self,
        temp_dir: str,
        target_width: int = TARGET_WIDTH,
        target_height: int = TARGET_HEIGHT,
        debug_mode: bool = False,
    ):
        self.temp_dir = temp_dir
        self.target_width = target_width
        self.target_height = target_height
        self.debug_mode = debug_mode

    def _extract_video_segment(
        self,
        video_path: str,
        duration: float,
        max_duration: float = MAX_SEGMENT_DURATION,
    ) -> str:
        """从长视频中随机截取指定时长的片段"""
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        segment_file = os.path.join(
            self.temp_dir,
            f"{sanitize_file_name_string(base_name)}_segment_{int(time.time())}.mp4",
        )

        # 如果视频时长小于等于最大片段时长，直接返回原视频
        if duration <= max_duration:
            return video_path

        # 计算随机开始时间（确保不会超出视频长度）
        max_start_time = max(0, duration - max_duration)
        start_time = random.uniform(0, max_start_time)

        # 构建ffmpeg命令截取视频片段（使用重新编码确保时长准确）
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-ss",
            str(start_time),
            "-t",
            str(max_duration),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-r",
            "30",
            segment_file,
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)

            if os.path.exists(segment_file) and os.path.getsize(segment_file) > 1000:
                print(f"  📹 截取 {max_duration}s 片段 (从 {start_time:.2f}s 开始)")
                return segment_file
            else:
                return video_path  # 如果截取失败，返回原文件

        except subprocess.CalledProcessError as e:
            print(f"视频截取失败: {e.stderr}")
            return video_path  # 如果截取失败，返回原文件

    def apply_random_transform(
        self,
        video_path: str,
        usage_mode: str = "segment",
        max_segment_duration: float = MAX_SEGMENT_DURATION,
    ) -> str:
        """对视频应用随机变换（包括可选的长视频截取）"""
        # 首先需要获取视频时长来决定是否截取
        # 这里我们无法直接访问VideoSource，所以使用ffprobe获取时长
        try:
            cmd = [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                video_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            # 获取视频时长
            duration = 0.0
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    duration = float(stream.get("duration", 0))
                    break

            if duration == 0.0:
                duration = float(data.get("format", {}).get("duration", 0))

        except Exception as e:
            print(f"获取视频时长失败: {e}")
            duration = 0.0

        # 根据使用方式决定是否截取
        input_video = video_path
        temp_files_to_cleanup = []

        if usage_mode == "segment" and duration > max_segment_duration:
            print(
                f"  ⏰ 检测到长视频 ({duration:.2f}s)，将截取 {max_segment_duration}s 片段"
            )
            segment_file = self._extract_video_segment(
                video_path, duration, max_segment_duration
            )
            if segment_file != video_path:
                input_video = segment_file
                temp_files_to_cleanup.append(segment_file)
        elif usage_mode == "full":
            print(f"  📹 完整使用视频素材 ({duration:.2f}s)")

        # 对截取后的视频（或原视频）应用随机变换
        base_name = os.path.splitext(os.path.basename(input_video))[0]
        output_file = os.path.join(
            self.temp_dir,
            f"{sanitize_file_name_string(base_name)}_transform_{int(time.time())}.mp4",
        )

        # 随机变换参数
        scale_factor = random.uniform(*SCALE_FACTOR_RANGE)
        should_flip = random.random() < FLIP_EFFECT_PROBABILITY
        speed_factor = random.uniform(*SPEED_FACTOR_RANGE)

        # 随机色彩调整参数
        apply_color_effect = random.random() < COLOR_EFFECT_PROBABILITY
        apply_hue_effect = random.random() < HUE_EFFECT_PROBABILITY

        brightness = random.uniform(*BRIGHTNESS_RANGE) if apply_color_effect else 1.0
        contrast = random.uniform(*CONTRAST_RANGE) if apply_color_effect else 1.0
        saturation = random.uniform(*SATURATION_RANGE) if apply_color_effect else 1.0
        hue_shift = random.uniform(*HUE_SHIFT_RANGE) if apply_hue_effect else 0.0

        # 构建滤镜
        filter_str = self._build_filter_string(
            scale_factor,
            should_flip,
            speed_factor,
            brightness,
            contrast,
            saturation,
            hue_shift,
        )

        # 构建ffmpeg命令
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_video,
            "-vf",
            filter_str,
            "-af",
            f"atempo={speed_factor}",  # 音频变速处理
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-ar",
            "44100",
            "-r",
            "30",  # 固定帧率30fps
            output_file,
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)

            # 清理临时截取文件
            for temp_file in temp_files_to_cleanup:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    print(f"清理临时文件失败 {temp_file}: {e}")

            if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                return output_file
            else:
                return input_video  # 如果变换失败，返回截取后的视频或原视频

        except subprocess.CalledProcessError as e:
            print(f"视频变换失败: {e.stderr}")

            # 清理临时截取文件
            for temp_file in temp_files_to_cleanup:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    print(f"清理临时文件失败 {temp_file}: {e}")

            return input_video  # 如果变换失败，返回截取后的视频或原视频

    def _build_filter_string(
        self,
        scale_factor: float,
        should_flip: bool,
        speed_factor: float,
        brightness: float = 1.0,
        contrast: float = 1.0,
        saturation: float = 1.0,
        hue_shift: float = 0.0,
    ) -> str:
        """构建FFmpeg滤镜字符串"""
        filter_parts = []

        # 缩放滤镜
        if scale_factor > 1.0:
            new_width = int(self.target_width * scale_factor)
            new_height = int(self.target_height * scale_factor)
            filter_parts.append(
                f"scale={new_width}:{new_height}:force_original_aspect_ratio=increase"
            )
        else:
            filter_parts.append(
                f"scale={self.target_width}:{self.target_height}:force_original_aspect_ratio=increase"
            )

        # 左右翻转
        if should_flip:
            filter_parts.append("hflip")

        # 居中裁剪到目标尺寸
        filter_parts.append(
            f"crop={self.target_width}:{self.target_height}:(iw-{self.target_width})/2:(ih-{self.target_height})/2"
        )

        # 色彩调整滤镜
        if brightness != 1.0 or contrast != 1.0 or saturation != 1.0:
            filter_parts.append(
                f"eq=brightness={brightness:.2f}:contrast={contrast:.2f}:saturation={saturation:.2f}"
            )

        # 色调偏移滤镜
        if hue_shift != 0.0:
            filter_parts.append(f"hue=h={hue_shift:.2f}")

        # 设置像素格式
        filter_parts.append("format=yuv420p")

        # 添加调试信息显示（仅在调试模式下）
        if self.debug_mode:
            debug_text = (
                f"缩放:{scale_factor:.2f}x 翻转:{should_flip} 倍速:{speed_factor:.2f}x"
            )
            if brightness != 1.0 or contrast != 1.0 or saturation != 1.0:
                debug_text += f" 色彩:{brightness:.1f}/{contrast:.1f}/{saturation:.1f}"
            if hue_shift != 0.0:
                debug_text += f" 色调:{hue_shift:.2f}"
            escaped_text = (
                debug_text.replace(":", "\\:").replace("'", "\\'").replace('"', '\\"')
            )
            filter_parts.append(
                f"drawtext=text='{escaped_text}':x=20:y=20:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5"
            )

        # 组合滤镜
        filter_str = ",".join(filter_parts)

        # 倍速处理
        if speed_factor != 1.0:
            if filter_str:
                filter_str += f",setpts={1 / speed_factor}*PTS"
            else:
                filter_str = f"setpts={1 / speed_factor}*PTS"

        return filter_str


class VideoConcatenator:
    """视频拼接器 - 负责拼接多个视频"""

    def __init__(self, temp_dir: str, output_dir: str):
        self.temp_dir = temp_dir
        self.output_dir = output_dir

    def concatenate_videos(
        self, video_list: List[str], output_filename: str
    ) -> Optional[str]:
        """拼接多个视频"""
        if not video_list:
            print("没有视频可拼接")
            return None

        output_path = os.path.join(self.output_dir, output_filename)

        # 创建临时文件列表
        list_file = os.path.join(self.temp_dir, f"concat_list_{int(time.time())}.txt")

        with open(list_file, "w", encoding="utf-8") as f:
            for video in video_list:
                # 对文件路径进行转义
                escaped_path = video.replace("'", "'\"'\"'")
                f.write(f"file '{escaped_path}'\n")

        # 使用concat拼接并重新编码确保兼容性
        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_file,
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-r",
            "30",  # 固定帧率
            output_path,
        ]

        try:
            print(f"正在拼接 {len(video_list)} 个视频片段...")
            subprocess.run(cmd, capture_output=True, text=True, check=True)

            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"视频拼接完成: {output_path}")
                # 清理临时文件列表
                if os.path.exists(list_file):
                    os.remove(list_file)
                return output_path
            else:
                print("视频拼接失败：输出文件不存在或过小")
                return None

        except subprocess.CalledProcessError as e:
            print(f"视频拼接失败: {e.stderr}")
            return None


class TempFileManager:
    """临时文件管理器 - 负责管理临时文件"""

    def __init__(self, temp_dir: str):
        self.temp_dir = temp_dir
        self.temp_files = []

        # 确保临时目录存在
        os.makedirs(self.temp_dir, exist_ok=True)

    def register_temp_file(self, file_path: str):
        """注册临时文件"""
        self.temp_files.append(file_path)

    def cleanup(self):
        """清理临时文件"""
        print(f"\n🧹 清理临时文件...")
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"删除临时文件失败 {temp_file}: {e}")

        # 清理空的临时目录
        try:
            if os.path.exists(self.temp_dir) and not os.listdir(self.temp_dir):
                os.rmdir(self.temp_dir)
                print(f"删除空目录: {self.temp_dir}")
        except Exception as e:
            print(f"删除临时目录失败: {e}")


class VideoMixer:
    """视频混剪器 - 主控制器类"""

    def __init__(
        self, debug_mode: bool = False, source_dir: str = None, output_dir: str = None
    ):
        # 根据平台或参数设置正确的素材目录
        self.source_dir = source_dir if source_dir else self._get_source_dir()
        self.temp_dir = os.path.join(
            output_dir if output_dir else OUTPUT_DIR, TEMP_DIR_NAME
        )
        self.output_dir = output_dir if output_dir else OUTPUT_DIR

        # 初始化各个组件
        self.video_source = VideoSource(self.source_dir)
        self.video_transformer = VideoTransformer(self.temp_dir, debug_mode=debug_mode)
        self.video_concatenator = VideoConcatenator(self.temp_dir, self.output_dir)
        self.temp_manager = TempFileManager(self.temp_dir)

        print(f"素材目录: {self.source_dir}")
        print(f"临时目录: {self.temp_dir}")
        print(f"输出目录: {self.output_dir}")

    def _get_source_dir(self):
        """根据平台返回正确的素材目录路径"""
        if platform_type == "windows":
            return SOURCE_DIR_WINDOWS
        elif platform_type == "mac":  # macOS
            return SOURCE_DIR_MACOS
        else:  # wsl, linux, 其他
            return SOURCE_DIR_LINUX

    def generate_video(
        self,
        target_duration_minutes: float,
        category: str = None,
        subcategory: str = None,
        usage_mode: str = "segment",
        max_segment_duration: float = 10.0,
    ) -> str:
        """生成随机拼接视频"""
        target_duration_seconds = target_duration_minutes * 60

        category_desc = f" - 分类: {category}" if category else ""
        subcategory_desc = f" - 子分类: {subcategory}" if subcategory else ""
        usage_desc = f" - 使用方式: {'完整使用' if usage_mode == 'full' else f'截取使用({max_segment_duration}s)'}"
        print(
            f"开始生成视频，目标时长: {target_duration_minutes} 分钟 ({target_duration_seconds} 秒){category_desc}{subcategory_desc}{usage_desc}"
        )

        # 构建搜索路径（支持二级分类）
        search_category = category
        if category and subcategory:
            search_category = os.path.join(category, subcategory)

        # 查找所有视频文件
        all_videos = self.video_source.find_all_videos(search_category)
        if not all_videos:
            category_msg = f"（分类：{category}"
            if subcategory:
                category_msg += f"/{subcategory}"
            category_msg += "）"
            if not category:
                category_msg = "（未指定分类）"
            raise RuntimeError(f"没有找到任何视频文件{category_msg}")

        # 随机打乱视频顺序
        shuffled_videos = self.video_source.shuffle_videos(all_videos)

        processed_videos = []
        current_duration = 0.0

        print("开始处理视频素材...")

        for video_path in shuffled_videos:
            if current_duration >= target_duration_seconds:
                break

            print(f"处理素材: {os.path.basename(video_path)}")

            # 获取原始视频时长
            original_duration = self.video_source.get_video_duration(video_path)

            if original_duration <= 0:
                print(f"跳过无效视频: {video_path}")
                continue

            # 应用随机变换到整个视频（传递使用方式和截取时长参数）
            transformed_video = self.video_transformer.apply_random_transform(
                video_path, usage_mode, max_segment_duration
            )

            # 注册临时文件
            if transformed_video != video_path:  # 如果是新生成的临时文件
                self.temp_manager.register_temp_file(transformed_video)

            # 获取变换后的时长
            transformed_duration = self.video_source.get_video_duration(
                transformed_video
            )

            # 直接添加整个视频
            processed_videos.append(transformed_video)
            current_duration += transformed_duration

            print(f"  添加视频，时长: {transformed_duration:.2f}s")
            print(f"  当前总时长: {current_duration:.2f}s / {target_duration_seconds}s")

        if not processed_videos:
            raise RuntimeError("没有成功处理任何视频")

        # 生成输出文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        mode_suffix = (
            "full" if usage_mode == "full" else f"seg{int(max_segment_duration)}s"
        )
        output_filename = f"random_video_mix_{mode_suffix}_{timestamp}.mp4"

        # 拼接所有处理过的视频
        output_path = self.video_concatenator.concatenate_videos(
            processed_videos, output_filename
        )

        if output_path:
            # 验证最终视频时长
            final_duration = self.video_source.get_video_duration(output_path)
            print(f"\n✅ 视频生成成功!")
            print(f"📁 输出文件: {output_path}")
            print(
                f"⏱️  最终时长: {final_duration:.2f} 秒 ({final_duration / 60:.2f} 分钟)"
            )
            print(f"🎬 使用了 {len(processed_videos)} 个视频")

            if final_duration < target_duration_seconds * 0.9:
                print(
                    f"⚠️  警告：最终时长比目标时长少约 {target_duration_seconds - final_duration:.2f} 秒"
                )

            return output_path
        else:
            raise RuntimeError("视频拼接失败")

    def cleanup(self):
        """清理临时文件"""
        self.temp_manager.cleanup()


def select_category(video_source: VideoSource) -> Optional[str]:
    """选择素材分类"""
    categories = video_source.get_category_directories()

    if not categories:
        print("素材目录下没有找到任何分类子目录，将使用所有素材")
        return None

    print("\n📁 可用的素材分类：")
    print("0. 使用所有素材")
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category}")

    while True:
        try:
            choice = input(f"\n请选择分类 (0-{len(categories)}): ").strip()
            choice_num = int(choice)

            if choice_num == 0:
                return None
            elif 1 <= choice_num <= len(categories):
                selected_category = categories[choice_num - 1]
                print(f"已选择分类: {selected_category}")
                return selected_category
            else:
                print(f"请输入 0-{len(categories)} 之间的数字")
        except ValueError:
            print("请输入有效的数字")


def select_subcategory(category: str, source_dir: str) -> Optional[str]:
    """选择子分类"""
    category_path = os.path.join(source_dir, category)

    try:
        if not os.path.exists(category_path):
            print(f"分类目录不存在: {category_path}")
            return None

        subcategories = []
        for item in os.listdir(category_path):
            item_path = os.path.join(category_path, item)
            if os.path.isdir(item_path):
                subcategories.append(item)

        if not subcategories:
            print(f"分类 '{category}' 下没有子目录，将使用该分类下所有素材")
            return None

        # 按名称排序
        subcategories.sort()

        print(f"\n📁 分类 '{category}' 下的子分类：")
        print("0. 选择全部子分类")
        for i, subcat in enumerate(subcategories, 1):
            print(f"{i}. {subcat}")

        while True:
            try:
                choice = input(f"\n请选择子分类 (0-{len(subcategories)}): ").strip()
                choice_num = int(choice)

                if choice_num == 0:
                    print(f"已选择分类 '{category}' 下的所有子分类")
                    return None  # None 表示选择全部
                elif 1 <= choice_num <= len(subcategories):
                    selected_subcat = subcategories[choice_num - 1]
                    print(f"已选择子分类: {selected_subcat}")
                    return selected_subcat
                else:
                    print(f"请输入 0-{len(subcategories)} 之间的数字")
            except ValueError:
                print("请输入有效的数字")

    except Exception as e:
        print(f"获取子分类失败: {e}")
        return None


def select_usage_mode() -> tuple:
    """选择素材使用方式"""
    print("\n🎯 选择素材使用方式：")
    print("1. 完整使用 - 不论素材多长，都完整使用")
    print("2. 截取使用 - 超过指定时长的素材随机截取片段")

    while True:
        try:
            choice = input(f"\n请选择使用方式 (1-2): ").strip()
            choice_num = int(choice)

            if choice_num == 1:
                print("已选择：完整使用所有素材")
                return "full", None
            elif choice_num == 2:
                while True:
                    try:
                        duration_input = input(
                            "请输入截取时长（秒，建议3-30秒）: "
                        ).strip()
                        max_duration = float(duration_input)
                        if max_duration <= 0:
                            print("请输入大于0的数值")
                            continue
                        if max_duration > 300:  # 5分钟上限
                            print("截取时长不宜过长，建议控制在300秒以内")
                            continue
                        print(f"已选择：截取使用，最大片段时长 {max_duration} 秒")
                        return "segment", max_duration
                    except ValueError:
                        print("请输入有效的数字")
            else:
                print("请输入 1 或 2")
        except ValueError:
            print("请输入有效的数字")


def main():
    """主函数"""
    print("🎬 随机视频拼接工具")
    print("=" * 50)

    try:
        # 创建参数解析器
        parser = argparse.ArgumentParser(
            description="随机视频拼接工具 - 随机选择素材并拼接成视频",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # 添加参数
        parser.add_argument("--duration", "-d", type=float, help="视频总时长（分钟）")
        parser.add_argument("--source", "-s", help="源文件夹路径")
        parser.add_argument("--output", "-o", help="输出目录路径")
        parser.add_argument("--category", "-c", help="分类名称（可选）")
        parser.add_argument(
            "--usage-mode",
            "-u",
            choices=["full", "segment"],
            help="使用方式：full-完整使用，segment-截取使用（CLI模式默认：segment）",
        )
        parser.add_argument(
            "--max-segment-duration",
            type=float,
            help="最大片段时长（秒，仅 usage-mode=segment 时有效）",
        )
        parser.add_argument(
            "--test", "-t", action="store_true", help="测试模式：1分钟，截取模式10秒"
        )

        # 解析参数
        args = parser.parse_args()

        # 测试模式
        test_mode = args.test

        # 源文件夹路径（命令行 > 默认值）
        default_source_dir = (
            SOURCE_DIR_WINDOWS
            if platform_type == "windows"
            else (SOURCE_DIR_MACOS if platform_type == "mac" else SOURCE_DIR_LINUX)
        )
        source_dir = get_param_value(args, "source", script_default=default_source_dir)

        # 验证源文件夹存在
        if not os.path.exists(source_dir):
            print(f"错误：源文件夹不存在: {source_dir}")
            sys.exit(1)

        # 输出目录（命令行 > 默认值）
        default_output = (
            PATH_DOWNLOADS_FROM_WIN if platform_type == "wsl" else PATH_DOWNLOADS
        )
        output_dir = get_param_value(args, "output", script_default=default_output)

        # 创建 VideoMixer
        mixer = VideoMixer(
            debug_mode=test_mode, source_dir=source_dir, output_dir=output_dir
        )

        # 视频时长
        # 判断是否为命令行模式（提供了 duration 参数）
        is_cli_mode = args.duration is not None

        # 视频时长
        if test_mode:
            target_duration = 1.0
            print("🧪 测试模式：设置为1分钟")
        else:
            target_duration = get_param_value(
                args, "duration", prompt_text="视频总时长（分钟）"
            )
            try:
                target_duration = float(target_duration)
            except (TypeError, ValueError):
                print("错误：时长必须是数字")
                sys.exit(1)
            if target_duration <= 0:
                print("错误：时长必须大于0")
                sys.exit(1)

        # 分类（可选）
        selected_category = get_param_value(args, "category", script_default=None)
        if selected_category is None and not test_mode and not is_cli_mode:
            # 交互式模式：交互式选择分类
            selected_category = select_category(mixer.video_source)

        # 子分类（交互式选择）
        selected_subcategory = None
        if selected_category:
            selected_subcategory = select_subcategory(
                selected_category, mixer.source_dir
            )

        # 使用方式
        if test_mode:
            usage_mode = "segment"
            max_segment_duration = 10.0
            print("测试模式：截取模式10秒")
        else:
            usage_mode = get_param_value(args, "usage_mode", script_default=None)
            if usage_mode is None:
                if is_cli_mode:
                    # 命令行模式但未指定使用方式，使用默认值
                    usage_mode = "segment"
                    max_segment_duration = 10.0
                else:
                    # 交互式模式：交互式选择使用方式
                    usage_mode, max_segment_duration = select_usage_mode()
            else:
                # 命令行指定了使用方式
                if usage_mode == "segment":
                    max_segment_duration = get_param_value(
                        args, "max_segment_duration", script_default=10.0
                    )
                    try:
                        max_segment_duration = float(max_segment_duration)
                    except (TypeError, ValueError):
                        print("错误：最大片段时长必须是数字")
                        sys.exit(1)
                    if max_segment_duration <= 0:
                        print("错误：最大片段时长必须大于0")
                        sys.exit(1)
                else:
                    max_segment_duration = None

        print(f"\n开始生成 {target_duration} 分钟的随机视频...")
        print("这可能需要几分钟时间，请耐心等待...\n")

        start_time = time.time()

        # 生成视频
        output_path = mixer.generate_video(
            target_duration,
            selected_category,
            selected_subcategory,
            usage_mode,
            max_segment_duration,
        )

        end_time = time.time()
        processing_time = end_time - start_time

        print(
            f"\n⏱️  处理耗时: {processing_time:.2f} 秒 ({processing_time / 60:.2f} 分钟)"
        )
        print(f"🎉 任务完成！")

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # 清理临时文件
        if "mixer" in locals():
            mixer.cleanup()


if __name__ == "__main__":
    main()
