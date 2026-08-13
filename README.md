# Deep Core OCR

> 多模型 AI 图像识别技能栈 —— 印刷体、手写体、界面文字、实物铭牌、网页文案一站式 OCR 提取。

## 项目定位

**Deep Core OCR** 是一个面向纸质文档、桌面截图、实物影像、网页 UI、证件票据等多场景的 AI OCR 识别技能。它整合多个主流多模态 / OCR 模型（DeepSeek-OCR、Qwen2.5-VL、MiniMax-M3），提供统一的图像识别入口、自动降级机制、场景化选型指南和结构化输出能力。

**核心目标**：

- **简单调用**：一条命令识别图片文字，自动处理多模型降级
- **场景化选型**：按文档 / 截图 / 实物 / 网页等场景推荐最合适的模型
- **成本可控**：日常任务用 douzimi 端点（DeepSeek-OCR / Qwen2.5-VL），复杂场景用 MiniMax-M3 兜底
- **输出可用**：支持原始 OCR 文本、结构化字段、Markdown / JSON 等多种落地格式

## 适用场景

| 场景类型 | 示例 | 推荐模型 |
|---------|------|---------|
| 纸质文档数字化 | 合同、票据、报表、档案、手写单据 | DeepSeek-OCR / Qwen2.5-VL |
| 桌面截图信息提取 | 客户端界面、后台系统、弹窗报错、日志 | Qwen2.5-VL / DeepSeek-OCR |
| 实物影像识别 | 证件、铭牌、标签、商品外包装 | Qwen2.5-VL / MiniMax-M3 |
| 网页 UI 合规校验 | 落地页文案、弹窗提示、底部声明 | DeepSeek-OCR / Qwen2.5-VL |
| 证件 / 发票 / 表格录入 | 身份证、发票、收据、报表 | Qwen2.5-VL / MiniMax-M3 |

## 模型矩阵

| 模型 | 能力档位 | 成本 | 速度 | 主用场景 | 当前状态 |
|------|---------|------|------|---------|---------|
| **DeepSeek-OCR** | ⭐⭐⭐⭐ A 级 | 低 | 快 | 印刷体文档、票据、规范手写体 | ✅ 可用（使用有效 key） |
| **Qwen2.5-VL** | ⭐⭐⭐⭐ A 级 | 低 | 中 | **日常主力、通用识别** | ✅ 可用（使用有效 key） |
| **MiniMax-M3** | ⭐⭐⭐⭐⭐ S 级 | 中 | 中 | 复杂图片、实景、多语言、兜底 | ✅ 可用 |

> **注意**：
> - `DeepSeek-OCR` 与 `Qwen2.5-VL` 均走 OpenAI 兼容的 `/v1/chat/completions` 端点，通过 `image_url` 传入 base64 图片。
> - `MiniMax-M3` 同样使用 `/v1/chat/completions`，但为 MiniMax 原生端点。
> - 实测时，若 douzimi 端点返回 `Invalid token`，请确认 API Key 拥有对应模型的调用权限；项目本身已做好端点切换与降级。

## 快速开始

### 1. 安装依赖

```bash
pip install -r scripts/requirements.txt
```

### 2. 配置 API 密钥

复制配置模板并填写密钥：

```bash
cp config.sample.json config.json
```

编辑 `config.json`：

```json
{
    "default_provider": "deepseek-ocr",
    "providers": {
        "deepseek-ocr": {
            "api_key": "sk-xxx",
            "base_url": "http://cf.douzimi.com:58728/v1",
            "model": "deepseek-ai/DeepSeek-OCR",
            "endpoint_type": "openai_compatible"
        },
        "qwen-vl": {
            "api_key": "sk-xxx",
            "base_url": "http://cf.douzimi.com:58728/v1",
            "model": "Qwen2.5-VL-7B-Instruct-Q6_K.gguf",
            "endpoint_type": "openai_compatible"
        },
        "minimax-m3": {
            "api_key": "sk-xxx",
            "base_url": "https://api.minimaxi.com/v1",
            "model": "minimax-M3",
            "endpoint_type": "minimax"
        }
    },
    "fallback_order": ["deepseek-ocr", "qwen-vl", "minimax-m3"]
}
```

> **重要**：`config.json` 已加入 `.gitignore`，请勿将其提交到 GitHub。

### 3. 识别图片文字

```bash
# 基础使用（自动走默认 provider 并降级）
python scripts/ocr.py --image input/invoice.png --output output/invoice.txt

# 指定模型
python scripts/ocr.py --image input/invoice.png --provider qwen-vl --output output/invoice.txt

# 结构化输出
python scripts/ocr.py --image input/invoice.png --mode structured --output output/invoice.json

# 仅输出到控制台
python scripts/ocr.py --image input/invoice.png
```

## 完整文档

- [SKILL.md](SKILL.md) - 技能主文档、使用示例、参数说明
- [references/ocr-scenario-guide.md](references/ocr-scenario-guide.md) - 五大典型场景使用指南
- [references/ocr-prompt-guide.md](references/ocr-prompt-guide.md) - OCR Prompt 编写指南
- [references/best-practices.md](references/best-practices.md) - 最佳实践汇总

## 模型可用性分析

基于 2026-08-13 的实际测试：

### ✅ DeepSeek-OCR（可用）

- **测试方式**：直接指定 provider 为 `deepseek-ocr`
- **测试结果**：使用有效 key 可识别规范印刷体
- **建议 Prompt**：`请输出图片中的全部文字内容。`

### ✅ Qwen2.5-VL（可用）

- **测试方式**：直接指定 provider 为 `qwen-vl`
- **测试结果**：使用有效 key 可精准识别印刷体与中英文混合文本
- **结论**：建议作为日常主力识别模型

### ✅ MiniMax-M3（可用）

- **测试方式**：直接指定 provider 为 `minimax-m3`
- **测试结果**：使用用户提供的 key 可正常识别图片文字
- **特点**：输出较完整，适合复杂图片与兜底

> **说明**：douzimi 端点（DeepSeek-OCR / Qwen2.5-VL）需使用拥有聊天 / 视觉模型调用权限的有效 key。配置好后，三个模型均可正常工作，并支持自动降级。

## 当前推荐用法

```bash
# 日常文档识别（优先 DeepSeek-OCR，失败自动降级到 Qwen2.5-VL）
python scripts/ocr.py \
  --image input/document.png \
  --output output/document.txt

# 复杂实景 / 兜底识别
python scripts/ocr.py \
  --image input/scene.png \
  --provider minimax-m3 \
  --output output/scene.txt

# 结构化发票识别
python scripts/ocr.py \
  --image input/invoice.png \
  --mode structured \
  --prompt "提取发票编号、金额、日期、供应商，输出 JSON" \
  --output output/invoice.json
```

## 项目结构

```
deep-core-ocr/
├── README.md                       # 本文件
├── SKILL.md                        # 技能主文档
├── config.json                     # 配置文件（本地，不提交）
├── config.sample.json              # 配置模板
├── scripts/                        # 执行脚本
│   ├── ocr.py                      # 主 OCR 脚本
│   ├── example_usage.sh            # 使用示例
│   └── test_installation.py        # 安装测试
├── references/                     # 指南文档
│   ├── ocr-scenario-guide.md       # 场景使用指南
│   ├── ocr-prompt-guide.md         # Prompt 编写指南
│   └── best-practices.md           # 最佳实践
├── output/                         # 最终输出目录
└── temp/                           # 过程文件目录
```

## 核心原则

```
日常文档 / 印刷体 → DeepSeek-OCR / Qwen2.5-VL
通用截图 / 界面文字 → Qwen2.5-VL
复杂实景 / 兜底 → MiniMax-M3
```

## 命令行参数

```
--image, -i       输入图片路径（必填）
--output, -o      输出文件路径（默认 stdout）
--prompt, -p      自定义识别 Prompt
--mode, -m        识别模式：ocr（默认）/ structured
--provider        强制指定提供商
--format          输出格式：text（默认）/ json
--no-proxy        绕过系统代理
--verbose, -v     详细输出
```

## 许可证

本技能按原样提供，用于与 Claude Code 配合使用。
