# Toolkit 使用手册

本手册面向 AI 助手，说明工具包中所有脚本的功能和用途，便于 AI 作为工具执行具体任务。

## 项目概述

`_toolkit` 是日常开发的全能工具集，提供图像处理、视频处理、文件转换、AI API 调用等多种工具。所有脚本均支持命令行参数调用，可被 AI 直接执行。

**核心特性：**
- 🤖 **AI 友好**：所有脚本支持命令行参数，适合 AI 调用
- 🔄 **双模式**：命令行模式（主要）+ 交互模式（备用）
- 📦 **模块化**：核心功能封装在 utils 库中
- 🌐 **跨平台**：支持 Windows/Linux/macOS

## 目录结构

```
_toolkit/
├── 根目录脚本/      - 文件管理、数据转换工具
├── image/          - 图像处理工具集
├── video/          - 视频处理工具集
└── utils/          - 核心工具函数库
```

## 使用方式

### 命令行参数模式（推荐）

所有脚本支持标准命令行参数：

```bash
# 完整参数名
python script.py --source /path/to/input --output /path/to/output

# 短参数名
python script.py -s /path/to/input -o /path/to/output
```

### 查看帮助

```bash
python script.py --help
python script.py -h
```

### 交互式模式

不带任何参数运行脚本，会进入交互模式询问必需参数：

```bash
python script.py
```

---

## 根目录工具

### `folder_ungroup.py` - 文件夹解组工具
**功能：** 将嵌套文件夹中的所有文件提取到单一文件夹中

---

### `convertor.py` - 通用格式转换器
**功能：** 批量转换文件格式（基于 ffmpeg 和 Pillow）

**支持的格式转换：**

**图片格式转换（支持任意互转）：**
- 源格式：jpg, jpeg, png, bmp, gif, tiff, webp, avif
- 目标格式：上述格式任意互转

**音频格式转换：**
- 源格式：mp3, wav, flac, aac, ogg
- 目标格式：统一转换为 mp3

**视频格式转换：**
- 源格式：mp4, avi, wmv, mov, flv, m4a
- 目标格式：mp4（视频转视频）
- 视频转音频：可转换为 mp3, wav, flac, aac, ogg

---

### `ai_studio_2_md.py` - AI Studio 聊天记录转换器
**功能：** 将 AI Studio 的 JSON 聊天记录转换为格式化的 Markdown 文档（自动识别用户和 AI 的对话，生成带回合标题的格式化文档）

---

## 图像处理工具（image/）

### `resizer.py` - 图片尺寸调整工具
**功能：** 智能调整图片尺寸，支持裁剪和留白模式

---

### `scaler.py` - 图片比例缩放工具
**功能：** 按比例缩放图片，限制在指定尺寸内

---

### `avatar_cropper.py` - 批量头像裁剪工具
**功能：** 批量将包含人脸的照片裁剪为指定尺寸的头像（支持圆形或方形）

---

### `dedup.py` - 智能图片去重工具
**功能：** 自动识别文件夹中的相似图片（包括缩放变体和裁剪变体），并保留分辨率最高的一个版本。

---

### `frames_2_gif.py` - GIF 合成工具
**功能：** 将多张图片转换为 GIF 动画（不支持透明背景 PNG 序列）

---

### `gif_2_frames.py` - GIF 分解工具
**功能：** 将 GIF 分解为单独图片帧

---

## 视频处理工具（video/）

### `images_2_video.py` - 图片转视频工具
**功能：** 图片序列合成视频，支持交叉淡入淡出效果

---

### `random_video_mixer.py` - 随机视频混剪工具
**功能：** 随机选择视频片段进行混剪，支持完整使用或截取模式

**支持功能：**
- 随机变换：缩放、翻转、变速、色彩调整、色调偏移
- 使用方式：完整使用或截取片段
- 支持分类筛选

---

## 配置

### API 密钥配置

复制 `utils/keys.json.example` 为 `utils/keys.json`，填入你的 API 密钥：

```json
{
  "GROQ_API_KEY": "your_groq_api_key_here",
  "CEREBRAS_API_KEY": "your_cerebras_api_key_here",
  "TELEGRAM_BOT_TOKEN": "your_telegram_bot_token_here",
  "TELEGRAM_CHAT_ID": "your_telegram_chat_id_here"
}
```

### 路径配置

默认输出路径为 `~/Downloads`，可在 `utils/path.py` 中修改 `PATH_DOWNLOADS` 变量。

---

## 附录

### 工具链关系

```
脚本（业务逻辑）
    ↓
utils（核心函数库）
    ↓
基础依赖（FFmpeg、Pillow、OpenCV 等）
```

### 依赖安装

```bash
pip install -r requirements.txt
```

**外部依赖：**
- FFmpeg：视频处理脚本需要
