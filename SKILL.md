---
name: deep-core-ocr
description: 使用多个 AI 视觉/多模态模型从图片中提取文字和结构化信息，支持自动降级。适用于纸质文档、桌面截图、实物影像、网页 UI、证件票据等场景。支持 DeepSeek-OCR、Qwen2.5-VL、MiniMax-M3 三个模型。
---

# Deep Core OCR Skill

使用多个 AI 视觉/多模态模型从图片中提取文字和结构化信息，支持自动降级，确保可靠的 OCR 识别能力。

## 概述

本技能支持使用多个 AI 提供商对图片进行 OCR 识别，当主提供商失败时，系统自动尝试下一个提供商，确保文字提取的可靠性。

**核心原则：先区分“纯 OCR”与“视觉理解”，再按场景选模型，复杂场景 MiniMax-M3 兜底。**

## 模型类型说明

本技能调用的模型可分为两类：

### 纯 OCR 模型

- **定义**：专门把文字从图片里“抠”出来的模型，核心是文字提取与版面还原。
- **代表**：DeepSeek-OCR
- **优势**：速度快、成本低、对印刷体和排版敏感
- **局限**：不理解图片中的物体、场景、语义关系

### 视觉理解模型

- **定义**：能“看懂”整张图的模型，可识别物体、场景、空间布局、人物关系、画面语义等；OCR 只是其能力子集。
- **代表**：Qwen2.5-VL、MiniMax-M3
- **优势**：通用性强，能处理倾斜、遮挡、杂乱背景、多语言
- **适用**：需要理解画面上下文后才能准确提取文字的任务

### 选型速查

```
只需要文字 → DeepSeek-OCR（纯 OCR）
需要理解图片再提取文字 → Qwen2.5-VL / MiniMax-M3（视觉理解）
复杂实景 / 兜底 → MiniMax-M3
```

## 支持的模型

| 模型 | 类型 | 能力档位 | 擅长 | 单次成本 | 速度 | 主用场景 |
|------|------|---------|------|---------|------|---------|
| **DeepSeek-OCR** | 纯 OCR | ⭐⭐⭐⭐ A 级 | 印刷体文档、规范手写体、票据、表格 | 低 | 快 | 纸质文档数字化 |
| **Qwen2.5-VL** | 视觉理解 | ⭐⭐⭐⭐ A 级 | 通用识别、版式理解、中英文混合、截图、界面文字 | 低 | 中 | **日常主力、通用识别** |
| **MiniMax-M3** | 视觉理解 | ⭐⭐⭐⭐⭐ S 级 | 复杂实景、多语言、小字、自然场景 | 中 | 中 | 复杂图片、兜底 |

### 场景选型速查

```
纸质文档 / 印刷体 / 票据 → DeepSeek-OCR（纯 OCR）
桌面截图 / 客户端界面 → Qwen2.5-VL（视觉理解）
实物影像 / 铭牌 / 标签 → Qwen2.5-VL / MiniMax-M3（视觉理解）
网页 UI 文案合规校验 → DeepSeek-OCR / Qwen2.5-VL
证件 / 发票 / 表格录入 → Qwen2.5-VL / MiniMax-M3（视觉理解 + 版式）
复杂实景 / 兜底 → MiniMax-M3
```

## 适用场景

使用本技能当：
- 用户需要从图片中提取文字内容
- 需要将纸质文档、票据、档案数字化
- 需要从软件截图、客户端界面中提取业务数据
- 需要识别实物上的铭牌、标签、证件信息
- 需要校验网页对外展示文案的合规性
- 需要将识别结果结构化输出为 JSON / Markdown

详细的场景指南请参考 [OCR 场景使用指南](references/ocr-scenario-guide.md)。

## 功能特性

- **多提供商降级** - 主提供商失败时自动降级
- **纯 OCR 文本提取** - 原样输出图片中的文字
- **结构化信息提取** - 按 Prompt 提取字段并输出
- **文本 / JSON 输出** - 支持两种落地格式
- **提供商选择** - 需要时可强制指定提供商
- **环境变量覆盖** - 支持通过环境变量快速切换配置

## 配置

### 配置文件

通过技能目录下的 `config.json` 配置：

```json
{
    "default_provider": "deepseek-ocr",
    "providers": {
        "deepseek-ocr": {
            "api_key": "YOUR_DOUZIMI_API_KEY",
            "base_url": "http://cf.douzimi.com:58728/v1",
            "model": "deepseek-ai/DeepSeek-OCR",
            "endpoint_type": "openai_compatible"
        },
        "qwen-vl": {
            "api_key": "YOUR_DOUZIMI_API_KEY",
            "base_url": "http://cf.douzimi.com:58728/v1",
            "model": "Qwen2.5-VL-7B-Instruct-Q6_K.gguf",
            "endpoint_type": "openai_compatible"
        },
        "minimax-m3": {
            "api_key": "YOUR_MINIMAX_API_KEY",
            "base_url": "https://api.minimaxi.com/v1",
            "model": "minimax-M3",
            "endpoint_type": "minimax"
        }
    },
    "fallback_order": ["deepseek-ocr", "qwen-vl", "minimax-m3"],
    "default_ocr_prompt": "请识别图片中的所有文字，并原样输出，不要添加解释。",
    "default_structured_prompt": "请仔细识别图片内容，提取关键信息并以结构化方式输出。",
    "timeout": 180,
    "max_retries": 3
}
```

### 环境变量

```bash
# 覆盖所有提供商的 API Key
export DEEP_CORE_OCR_API_KEY="your-api-key"

# 覆盖所有提供商的 Base URL
export DEEP_CORE_OCR_BASE_URL="http://your-proxy/v1"

# 设置默认提供商
export DEEP_CORE_OCR_DEFAULT_PROVIDER="qwen-vl"
```

## 本地脚本生成

`scripts/` 目录为本地工作目录，默认不在 Git 中。首次使用时，在项目根目录运行：

```bash
# macOS / Linux
python3 setup.py

# Windows
python setup.py
```

该命令会创建 `scripts/` 目录并写入 `ocr.py`、`test_installation.py`、`example_usage.sh`、`requirements.txt`。详细跨平台说明请参考 [references/create-scripts-guide.md](references/create-scripts-guide.md)。

## 使用方法

### 基础 OCR

识别图片中的全部文字：

```bash
python scripts/ocr.py --image input/document.png --output output/document.txt
```

### 指定提供商

```bash
python scripts/ocr.py \
  --image input/document.png \
  --provider qwen-vl \
  --output output/document.txt
```

### 结构化提取

从发票中提取关键字段：

```bash
python scripts/ocr.py \
  --image input/invoice.png \
  --mode structured \
  --prompt "提取发票编号、金额、日期、供应商，输出 JSON" \
  --output output/invoice.json
```

### JSON 格式输出

```bash
python scripts/ocr.py \
  --image input/document.png \
  --format json \
  --output output/document.json
```

## 参数说明

| 参数 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `--image`, `-i` | 输入图片路径 | 必填 | - |
| `--output`, `-o` | 输出文件路径 | stdout | - |
| `--prompt`, `-p` | 自定义识别 Prompt | 根据 mode | - |
| `--mode`, `-m` | 识别模式 | `ocr` | `ocr`, `structured` |
| `--format` | 输出格式 | `text` | `text`, `json` |
| `--provider` | 强制指定提供商 | auto | `deepseek-ocr`, `qwen-vl`, `minimax-m3` |
| `--verbose`, `-v` | 详细输出 | false | - |
| `--no-proxy` | 绕过系统代理 | false | - |

## 降级机制

系统自动按顺序尝试提供商：

1. **deepseek-ocr** → 如果失败 → **qwen-vl**
2. **qwen-vl** → 如果失败 → **minimax-m3**
3. **minimax-m3** → 如果失败 → 错误

每个提供商最多重试 3 次，采用指数退避策略。

## Prompt 编写指南

### 基础 OCR Prompt

```
请识别图片中的所有文字，并原样输出，不要添加解释。
```

### DeepSeek-OCR 推荐 Prompt

```
请输出图片中的全部文字内容。
```

### 结构化发票 Prompt

```
请识别这张发票图片，提取以下字段并以 JSON 格式输出：
- 发票编号
- 开票日期
- 金额（含税）
- 供应商名称
- 购买方名称
```

### 网页文案合规 Prompt

```
请提取网页截图中的所有可见文字，包括按钮、弹窗、底部声明、小字提示等，
以列表形式输出，不要遗漏。
```

详细的 Prompt 编写指南请参考 [OCR Prompt 编写指南](references/ocr-prompt-guide.md)。

## 场景指南

本技能覆盖五大核心场景：

1. **纸质文档数字化归档与智能整理**
2. **桌面业务截图信息提取与汇总**
3. **实物影像信息识别与结构化录入**
4. **网页 UI 文案与内容合规校验**
5. **证件 / 发票 / 票据信息自动录入**

详细指南请参考 [OCR 场景使用指南](references/ocr-scenario-guide.md)。

## 最佳实践

### 核心原则

1. **按场景选模型**：日常文档用 DeepSeek-OCR / Qwen2.5-VL，复杂实景用 MiniMax-M3
2. **先 OCR 后整理**：先用 OCR 提取文字，再用大模型进行纠错、归类、结构化
3. **Prompt 要明确**：指定输出格式、字段、是否保留原样
4. **图片质量优先**：清晰、平整、光线均匀的图片识别率更高

### 成本控制

- DeepSeek-OCR / Qwen2.5-VL 承担 80% 日常识别任务
- MiniMax-M3 用于复杂实景和兜底
- 批量处理时设置合理的超时和重试

### 质量保证

- 对关键字段进行人工抽检
- 对低质量图片先做预处理（旋转、裁剪、增强）
- 保存原始图片和识别结果，便于追溯

完整最佳实践请参考 [最佳实践](references/best-practices.md)。

## 示例

### 识别纸质合同

```bash
python scripts/ocr.py \
  --image input/contract.png \
  --output output/contract.txt
```

### 提取软件报错信息

```bash
python scripts/ocr.py \
  --image input/error-dialog.png \
  --provider qwen-vl \
  --prompt "提取所有错误代码、错误信息和按钮文字" \
  --output output/error-info.txt
```

### 识别商品标签

```bash
python scripts/ocr.py \
  --image input/product-label.jpg \
  --provider minimax-m3 \
  --mode structured \
  --prompt "提取商品名称、规格、生产日期、批次号、条形码" \
  --output output/label.json
```

## API 集成

### OpenAI 兼容提供商（DeepSeek-OCR / Qwen2.5-VL）

使用 `/v1/chat/completions` 端点，通过 `image_url` 传入 base64 图片：

```json
{
  "model": "Qwen2.5-VL-7B-Instruct-Q6_K.gguf",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "请识别图片中的所有文字。"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
      ]
    }
  ],
  "max_tokens": 2048,
  "temperature": 0.1
}
```

### MiniMax 提供商

使用 `/v1/chat/completions` 端点：

```json
{
  "model": "minimax-M3",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "请识别图片中的所有文字。"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
      ]
    }
  ],
  "max_tokens": 2048,
  "temperature": 0.1
}
```

## 错误处理

脚本会处理：
- 缺少 API 凭证
- 网络连接问题
- 无效参数
- API 速率限制
- 文件未找到（输入图片）
- 提供商失败自动降级

## 与其他技能的集成

本技能可与以下技能配合：
- **docx skill**：将 OCR 结果写入 Word 文档
- **markdown-tools**：将识别结果整理为 Markdown
- **deep-core-image**：为文档配图生成插图
- **knowledge-base-sync**：将识别结果归档到 Obsidian

## 限制

- 需要活动的互联网连接
- API 速率限制可能基于您的提供商
- 图片内容策略适用
- 极低分辨率或严重遮挡的图片识别效果会下降
- 部分艺术字体、手写体可能识别不准确
- DeepSeek-OCR / Qwen2.5-VL 的可用性取决于 douzimi 端点和 key 权限

## 故障排除

### 所有提供商失败

- 检查 API 密钥是否正确
- 验证网络连接
- 检查 API 服务状态
- 使用 `--verbose` 获取详细错误信息

### 特定提供商失败

- 检查提供商配置
- 验证提供商服务状态
- 自动跳过到下一个提供商

### 识别质量不佳

- 尝试更换提供商
- 优化 Prompt，明确输出要求
- 提高图片质量（清晰度、光线、角度）
- 对图片进行预处理（裁剪、旋转、增强对比度）

## 参考文档

- [跨平台创建 scripts 指南](references/create-scripts-guide.md) - 不同操作系统下创建 scripts 目录与脚本
- [OCR 场景使用指南](references/ocr-scenario-guide.md) - 五大典型场景详细指南
- [OCR Prompt 编写指南](references/ocr-prompt-guide.md) - 系统的 Prompt 编写方法
- [最佳实践](references/best-practices.md) - 汇总最佳实践
