---
id: "mem-20250313-cldenv"
type: "principle"
env: "cloud"
confidence: "high"
tags: ["python", "pip", "environment", "cloud-mode", "pep668"]
---

# Cloud Mode Python 环境适配协议

## 1. 环境嗅探前置（Mandatory First Step）

在 Cloud Mode 沙盒中执行任何 Python 任务前，必须先进行环境嗅探：

```bash
# 确认当前用户和 home 目录（不要假设是 /root/）
echo "User: $(whoami), Home: $HOME"

# 确认 Python 解释器路径
which python3

# 检查 pip 可用性
python3 -m pip --version
```

**常见陷阱**：
- ❌ 假设 home 目录是 `/root/` → 实际可能是 `/home/{user}/`
- ❌ 假设 `pip` 命令可用 → PEP 668 可能已禁用系统级安装
- ❌ 假设虚拟环境完整 → `venv/` 目录存在但 `bin/pip` 可能缺失

## 2. Python 包安装标准流程

Cloud Mode 沙盒通常运行现代 Debian/Ubuntu，已启用 PEP 668 保护。正确安装流程：

```bash
# 方案 A：使用 python3 -m pip（推荐）
python3 -m pip install <package>

# 方案 B：如果 pip 不可用，先激活 ensurepip
python3 -m ensurepip --upgrade
python3 -m pip install <package>

# 方案 C：创建独立虚拟环境（如需隔离）
python3 -m venv /path/to/venv
/path/to/venv/bin/pip install <package>
```

**禁止做法**：
- ❌ `pip install <package>` → 触发 externally-managed-environment 错误
- ❌ `uv pip install` → 可能在无权限环境下失败
- ❌ `--break-system-packages` → 破坏环境隔离，可能导致后续问题

## 3. 工具箱脚本的 Cloud 适配

`lab/_toolkit/` 中的脚本依赖 `utils` 模块，但 `utils/path.py` 中的路径变量是为 Local Mode 设计的。

**Cloud Mode 下的处理策略**：
- 简单任务：直接使用原生库（如 Pillow）绕过工具箱脚本
- 复杂任务：在调用前手动覆盖路径变量，或为 Cloud Mode 创建精简版脚本

## 4. 文件输出路径约定

Cloud Mode 下所有输出文件必须写入宿主平台规定的输出目录。

通过环境嗅探确定具体路径（各平台不同，不要硬编码绝对路径）。常见模式：
- 检查平台文档或环境变量
- 确认写入权限后再执行输出操作
- 相对路径优于绝对路径
