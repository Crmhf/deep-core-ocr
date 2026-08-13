# 跨平台创建 scripts 目录与脚本指南

`scripts/` 目录为本地工作目录，已加入 `.gitignore`，不会提交到 GitHub。本指南说明如何在不同操作系统和平台下创建 `scripts/` 目录并生成所需脚本文件。

## 推荐方式：使用 setup.py（跨平台）

仓库根目录提供 `setup.py`，可一键创建 `scripts/` 目录、写入脚本文件、自动设置可执行权限，并可选地复制 `config.sample.json` 为 `config.json`。

### 前置条件

- 已安装 Python 3（Windows / macOS / Linux 均可）
- 已克隆或解压 `deep-core-ocr` 仓库

### 运行 setup.py

#### Windows（命令提示符 / PowerShell）

```cmd
# 进入项目目录
cd C:\Users\YourName\.cc-switch\skills\deep-core-ocr

# 运行 setup
python setup.py
```

```powershell
# PowerShell
Set-Location C:\Users\YourName\.cc-switch\skills\deep-core-ocr
python setup.py
```

#### macOS / Linux（Terminal）

```bash
cd /Users/YourName/.cc-switch/skills/deep-core-ocr
python3 setup.py
```

### setup.py 执行内容

1. 创建 `scripts/` 目录
2. 生成以下脚本文件：
   - `scripts/ocr.py` —— 主 OCR 识别脚本
   - `scripts/requirements.txt` —— Python 依赖
   - `scripts/test_installation.py` —— 安装测试
   - `scripts/example_usage.sh` —— 使用示例（Unix）
3. 在 macOS / Linux 上为 `.py` 和 `.sh` 文件添加可执行权限
4. 若不存在 `config.json`，自动复制 `config.sample.json` 为 `config.json`

---

## 手动创建方式

如果你不想使用 `setup.py`，也可以按以下方式手动创建。

### 一、创建 scripts 目录

#### Windows

**方法 A：文件资源管理器**

1. 打开项目文件夹
2. 右键空白处 → 新建 → 文件夹
3. 命名为 `scripts`

**方法 B：命令提示符（CMD）**

```cmd
cd C:\Users\YourName\.cc-switch\skills\deep-core-ocr
mkdir scripts
```

**方法 C：PowerShell**

```powershell
New-Item -ItemType Directory -Path "C:\Users\YourName\.cc-switch\skills\deep-core-ocr\scripts"
```

#### macOS

**方法 A：Finder**

1. 打开项目文件夹
2. 右键空白处 → 新建文件夹
3. 命名为 `scripts`

**方法 B：Terminal**

```bash
cd /Users/YourName/.cc-switch/skills/deep-core-ocr
mkdir scripts
```

#### Linux

**方法 A：文件管理器**

1. 打开项目文件夹
2. 右键 → 新建文件夹
3. 命名为 `scripts`

**方法 B：Terminal**

```bash
cd /home/YourName/.cc-switch/skills/deep-core-ocr
mkdir scripts
```

---

### 二、创建脚本文件

在 `scripts/` 目录下创建以下文件（内容可从 `setup.py` 中提取，或运行 `python setup.py` 自动生成）：

| 文件名 | 用途 |
|--------|------|
| `ocr.py` | 主 OCR 脚本，支持多模型降级 |
| `requirements.txt` | Python 依赖清单 |
| `test_installation.py` | 安装与配置测试 |
| `example_usage.sh` | 使用示例（Unix） |

#### Windows 下创建文件

```cmd
cd scripts
type nul > ocr.py
type nul > requirements.txt
type nul > test_installation.py
type nul > example_usage.sh
```

然后使用记事本 / VS Code / PyCharm 等编辑器打开并粘贴对应内容。

#### macOS / Linux 下创建文件

```bash
cd scripts
touch ocr.py requirements.txt test_installation.py example_usage.sh
```

然后使用 `nano`、`vim` 或 VS Code 编辑：

```bash
nano ocr.py
```

---

### 三、设置可执行权限（仅 macOS / Linux）

如果你希望直接运行脚本，需要添加可执行权限：

```bash
cd scripts
chmod +x ocr.py test_installation.py example_usage.sh
```

验证权限：

```bash
ls -l
```

应看到类似：

```
-rwxr-xr-x  1 user  staff  16948 Aug 13 10:00 ocr.py
-rwxr-xr-x  1 user  staff   5349 Aug 13 10:00 test_installation.py
-rwxr-xr-x  1 user  staff   3052 Aug 13 10:00 example_usage.sh
```

Windows 不需要此步骤，直接通过 `python ocr.py` 运行即可。

---

## 验证 scripts 目录

无论使用哪种方式创建，完成后应验证目录结构：

```bash
# macOS / Linux
ls -la scripts/
```

```cmd
:: Windows
dir scripts\
```

期望输出：

```
scripts/
├── ocr.py
├── requirements.txt
├── test_installation.py
└── example_usage.sh
```

---

## 后续步骤

1. **安装依赖**

   ```bash
   pip install -r scripts/requirements.txt
   ```

2. **配置 API Key**

   编辑项目根目录的 `config.json`，填入你的 API Key：

   ```json
   {
       "providers": {
           "deepseek-ocr": { "api_key": "sk-...", ... },
           "qwen-vl": { "api_key": "sk-...", ... },
           "minimax-m3": { "api_key": "sk-...", ... }
       }
   }
   ```

3. **运行安装测试**

   ```bash
   python scripts/test_installation.py
   ```

4. **执行 OCR**

   ```bash
   python scripts/ocr.py --image input.png --output output.txt
   ```

---

## 常见问题

### Q1：Windows 下无法直接运行 `./scripts/ocr.py`？

Windows 默认不识别 shebang，应使用：

```cmd
python scripts\ocr.py --image input.png --output output.txt
```

### Q2：macOS / Linux 下提示 Permission denied？

说明没有可执行权限，执行：

```bash
chmod +x scripts/*.py scripts/*.sh
```

### Q3：setup.py 运行后没有看到 scripts 目录？

检查是否在项目根目录运行：

```bash
pwd
# 应显示 .../deep-core-ocr
python setup.py
```

### Q4：想重新生成 scripts？

`setup.py` 是幂等的，可以重复运行，会覆盖原有 `scripts/` 内容（注意备份自定义修改）。

```bash
python setup.py
```

---

## 平台速查表

| 操作 | Windows | macOS | Linux |
|------|---------|-------|-------|
| 创建目录 | `mkdir scripts` | `mkdir scripts` | `mkdir scripts` |
| 创建空文件 | `type nul > file.py` | `touch file.py` | `touch file.py` |
| 添加执行权限 | 不需要 | `chmod +x file.py` | `chmod +x file.py` |
| 运行 Python 脚本 | `python scripts\ocr.py` | `python3 scripts/ocr.py` | `python3 scripts/ocr.py` |
| 运行 setup | `python setup.py` | `python3 setup.py` | `python3 setup.py` |
