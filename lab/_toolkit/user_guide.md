# Routine AI使用手册

本手册面向AI助手，说明routine项目中所有脚本的功能和用途，便于AI作为工具执行具体任务。

## 项目概述

`routine` 是日常开发的全能工具集，提供内容创作、文件处理、数据转换、自动化任务、视频处理等多种工具。所有脚本均支持命令行参数调用，可被AI直接执行。

**核心特性：**
- 🤖 **AI友好**：所有脚本支持命令行参数，适合AI调用
- 🔄 **双模式**：命令行模式（主要）+ 交互模式（备用）
- 📦 **模块化**：核心功能封装在utils库中
- 🌐 **跨平台**：支持Windows/WSL/Linux/macOS

## 目录结构

```
routine/
├── 根目录脚本/      - 文件管理、数据转换、内容创作
├── utils/          - 核心工具函数库
├── image/          - 图像处理工具集
├── video/          - 视频处理工具集
├── music/          - 音乐处理工具集
└── tasks/          - 任务定义文档
```

## 使用方式

### 命令行参数模式（推荐）

所有脚本支持标准命令行参数，具体参数用法请用 `--help` 查看。

### 查看帮助

**查看任何脚本的参数和详细说明：**

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

### 文件管理工具

#### `folder_ungroup.py` - 文件夹解组工具
**功能：** 将嵌套文件夹中的所有文件提取到单一文件夹中
**重名规则：** 同名文件按 `_2`、`_3` 顺序保留，避免扁平化时互相覆盖

---

#### `rename_by_csv.py` - CSV批量重命名工具
**功能：** 根据CSV文件中的映射关系批量重命名文件

**CSV文件格式：** 必须包含 `name` 列，源文件名需要包含数字序号

---

#### `port_cleaner.py` - 港口清理工具
**功能：** 工作目录文件归拢与过期清理（基于港口思维）

---

### 数据转换工具

#### `convertor.py` - 通用格式转换器
**功能：** 批量转换文件格式（基于ffmpeg和Pillow）
**输入：** 支持单个文件或文件夹；文件夹模式会递归处理

**支持的格式转换：**

**图片格式转换（支持任意互转）：**
- 源格式：jpg, jpeg, jfif, png, bmp, gif, tiff, webp, avif
- 目标格式：上述格式任意互转
- jpg、jpeg 与 jfif 之间仅变更扩展名时直接复制文件，不重新编码
- PNG、WebP、AVIF 等支持透明度的目标格式会保留 alpha 通道
- 文件夹输入递归处理；转换后同名的文件按 `_2`、`_3` 顺序保留

**音频格式转换：**
- 源格式：mp3, wav, flac, aac, ogg, m4a, opus
- 目标格式：mp3, wav, flac, aac, ogg, m4a, opus

**视频格式转换：**
- 源格式：mp4, avi, wmv, mov, flv, m4a, mkv, webm, m4v
- 目标格式：mp4, mov, m4v, mkv, avi, webm, flv, wmv
- 视频转音频：可转换为 mp3, wav, flac, aac, ogg, m4a, opus
- 视频转GIF：可转换为 gif 动图（fps=15, 宽度480px, Lanczos缩放）

---

#### `html_table_2_csv.py` - HTML表格转CSV工具
**功能：** 批量将HTML文件中的表格转换为CSV格式
**输入：** 支持单个 HTML 文件或包含 HTML 文件的文件夹

---

#### `ai_studio_2_md.py` - AI Studio聊天记录转换器
**功能：** 将AI Studio的JSON聊天记录转换为格式化的Markdown文档（自动识别用户和AI的对话，生成带回合标题的格式化文档）
**输入：** 支持单个 JSON 文件或包含 JSON 文件的文件夹；文件夹模式会递归处理

---

### 内容同步工具

#### `gist_sync.py` - GitHub secret Gist 同步
**功能：** 把一份 Markdown 创建或更新为一个 secret Gist，并校验远端内容与源文件一致
**用途：** Cognition Shaper 云端 Living Surface 的展示层同步；不是通用 Git 维护，也不批量管理多个 Gist
**输入：** 单个 Markdown 文件；无既有 Gist 时创建，有既有身份时覆盖同一文件
**输出：** 标准输出 JSON（成功含 gist_id / html_url；失败含 error），不写本地产物文件
**认证：** token 只从环境变量或 dotenv 读取（`COGNITION_SHAPER_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`，或唯一的 `GITHUB_*_TOKEN`），禁止在命令行传 token
**依赖：** `utils.basic.get_param_value`；GitHub 调用本身只用标准库

---

## 核心工具函数库（utils/）

`utils/` 提供 routine 脚本复用的基础能力，包括文件处理、图像/视频处理、表格解析、OCR、浏览器自动化、音乐解析、通信、消息推送和 API 集成。

**详细说明：** 见 `utils/README.md`

---

## 图像处理工具（image/）

### `resizer.py` - 图片尺寸调整工具
**功能：** 智能调整图片尺寸，支持裁剪和留白模式
**输入：** 支持单张图片或图片文件夹

---

### `scaler.py` - 图片比例缩放工具
**功能：** 按比例缩放图片，限制在指定尺寸内
**输入：** 支持单张图片或图片文件夹

---

### `avatar_cropper.py` - 批量头像裁剪工具
**功能：** 批量将包含人脸的照片裁剪为指定尺寸的头像（支持圆形或方形）
**输入：** 支持单张图片或图片文件夹

---

### `dedup.py` - 智能图片去重工具
**功能：** 自动识别文件夹中的相似图片（包括缩放变体和裁剪变体），并保留分辨率最高的一个版本。

---

### `frames_2_gif.py` - GIF合成工具
**功能：** 将多张图片转换为GIF动画（不支持透明背景PNG序列）

---

### `gif_2_frames.py` - GIF分解工具
**功能：** 将GIF分解为单独图片帧
**输入：** 支持单个 GIF 文件或包含 GIF 文件的文件夹

---

## 视频处理工具（video/）

### `images_2_video.py` - 图片转视频工具
**功能：** 图片序列合成视频，支持交叉淡入淡出效果

---

### `random_video_mixer.py` - 随机视频混剪工具
**功能：** 随机选择视频片段进行混剪，支持完整使用或截取模式

---

### `ezgif_video_2_gif.py` - 视频转GIF工具
**功能：** 批量将视频转换为GIF并优化大小（使用 ezgif.com 在线服务），默认缩放比例为75%

---

## 音乐处理工具（music/）

### `music_list_2_txt.py` - 歌单转换工具
**功能：** HTML歌单转换为TXT导入格式（用于跨平台歌单迁移）
**输出：** TXT歌名清单，默认写入脚本目录下的 `m_list.txt`，也可以指定输出文件

---

### `Netease_free.py` - 网易云免费音乐下载工具
**功能：** 从网易云音乐歌单下载可直接获取的免费歌曲
**输出：** 可下载音乐默认保存到下载目录下的 `Netease_free`，也可以指定输出目录；不可下载歌曲写入脚本目录下的 `m_list.txt`

---

## 附录

### 获取更多帮助

- **项目说明**：见 `notes.md`
- **核心工具库**：见 `utils/README.md`
