#!/usr/bin/env python3
"""
Deep Core OCR - Setup Script

This script creates the local `scripts/` directory and populates it with
the required executable scripts. It is cross-platform (Windows, macOS, Linux).

Usage:
    python setup.py

After running, edit `config.json` (copied from `config.sample.json` if not present)
with your API keys, then run:

    python scripts/ocr.py --image input.png --output output.txt
"""

import os
import shutil
import stat
import sys
from pathlib import Path


def get_skill_dir() -> Path:
    """Return the directory containing this setup script."""
    return Path(__file__).parent.resolve()


def write_text(path: Path, content: str) -> None:
    """Write text content to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  created {path}")


def make_executable(path: Path) -> None:
    """Make a file executable on Unix-like systems."""
    if os.name != "nt":
        current = path.stat().st_mode
        path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"  made executable {path}")


def copy_config_sample_if_needed(skill_dir: Path) -> None:
    """Copy config.sample.json to config.json if config.json does not exist."""
    config_path = skill_dir / "config.json"
    sample_path = skill_dir / "config.sample.json"
    if not config_path.exists() and sample_path.exists():
        shutil.copy(sample_path, config_path)
        print(f"  copied {sample_path.name} -> {config_path.name}")
        print("  IMPORTANT: edit config.json and fill in your API keys before use.")


def setup(skill_dir: Path) -> None:
    """Create scripts directory and write script files."""
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    print(f"Ensured directory: {scripts_dir}")

    # ------------------------------------------------------------------
    # scripts/requirements.txt
    # ------------------------------------------------------------------
    requirements_txt = """requests>=2.28.0
Pillow>=9.0.0
"""
    write_text(scripts_dir / "requirements.txt", requirements_txt)

    # ------------------------------------------------------------------
    # scripts/ocr.py
    # ------------------------------------------------------------------
    ocr_py = r'''#!/usr/bin/env python3
"""
Deep Core OCR Script (Multi-Provider Fallback)

Recognize text and structured information from images using multiple
vision-language / OCR providers with automatic fallback.

Supported Providers (in fallback order):
1. DeepSeek-OCR (OpenAI-compatible proxy)
2. Qwen2.5-VL (OpenAI-compatible proxy)
3. MiniMax-M3 (MiniMax API)

Supported Features:
- Plain OCR text extraction
- Structured information extraction
- Automatic provider fallback on failure
- JSON / text output

Usage:
    # Basic OCR with default provider
    python ocr.py --image document.png --output document.txt

    # Force specific provider
    python ocr.py --image document.png --provider qwen-vl --output document.txt

    # Structured extraction
    python ocr.py --image invoice.png --mode structured --output invoice.json

Configuration Priority (highest to lowest):
    1. Command line arguments
    2. Environment variables
    3. config.json file in skill directory
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


def get_skill_dir() -> Path:
    """Get the skill directory path."""
    script_dir = Path(__file__).parent
    return script_dir.parent


def load_config_file() -> Dict:
    """Load configuration from config.json file."""
    config_path = get_skill_dir() / "config.json"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config.json: {e}")
    return {}


def get_config() -> Dict:
    """Get configuration with priority: env vars > config file > defaults."""
    file_config = load_config_file()

    defaults = {
        "default_provider": "deepseek-ocr",
        "providers": {},
        "fallback_order": ["deepseek-ocr", "qwen-vl", "minimax-m3"],
        "default_ocr_prompt": "请识别图片中的所有文字，并原样输出，不要添加解释。",
        "default_structured_prompt": "请仔细识别图片内容，提取关键信息并以结构化方式输出。",
        "timeout": 180,
        "max_retries": 3
    }

    config = {**defaults, **file_config}

    if os.environ.get("DEEP_CORE_OCR_API_KEY"):
        for provider_name in config["providers"]:
            config["providers"][provider_name]["api_key"] = os.environ["DEEP_CORE_OCR_API_KEY"]
    if os.environ.get("DEEP_CORE_OCR_BASE_URL"):
        for provider_name in config["providers"]:
            config["providers"][provider_name]["base_url"] = os.environ["DEEP_CORE_OCR_BASE_URL"]
    if os.environ.get("DEEP_CORE_OCR_DEFAULT_PROVIDER"):
        config["default_provider"] = os.environ["DEEP_CORE_OCR_DEFAULT_PROVIDER"]

    return config


def encode_image_to_base64(image_path: str) -> str:
    """Encode image file to base64 string with data URL prefix."""
    with open(image_path, "rb") as f:
        image_data = f.read()
    base64_string = base64.b64encode(image_data).decode("utf-8")
    ext = Path(image_path).suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    mime_type = mime_types.get(ext, "image/png")
    return f"data:{mime_type};base64,{base64_string}"


def build_messages(prompt: str, image_data_url: str, mode: str = "ocr") -> List[Dict]:
    """Build chat messages for vision model."""
    if mode == "structured":
        system_msg = "你是一个信息提取助手。请基于图片内容提取结构化信息，按用户要求的格式输出。"
    else:
        system_msg = "你是一个 OCR 助手。请准确识别图片中的文字内容，原样输出，不要添加解释。"

    return [
        {"role": "system", "content": system_msg},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_data_url}}
            ]
        }
    ]


def request_openai_compatible(
    provider_config: Dict,
    prompt: str,
    image_data_url: str,
    mode: str = "ocr",
    no_proxy: bool = False,
    timeout: int = 180
) -> str:
    """Call OpenAI-compatible vision chat completions endpoint."""
    endpoint = f"{provider_config['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {provider_config['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": provider_config["model"],
        "messages": build_messages(prompt, image_data_url, mode),
        "max_tokens": 2048,
        "temperature": 0.1
    }

    proxies = None
    if no_proxy:
        proxies = {"http": None, "https": None}

    response = requests.post(
        endpoint,
        headers=headers,
        json=payload,
        timeout=timeout,
        proxies=proxies
    )
    response.raise_for_status()

    result = response.json()
    if "choices" not in result or not result["choices"]:
        raise ValueError(f"Unexpected API response format: {json.dumps(result, indent=2)}")

    return result["choices"][0]["message"]["content"]


def request_minimax(
    provider_config: Dict,
    prompt: str,
    image_data_url: str,
    mode: str = "ocr",
    no_proxy: bool = False,
    timeout: int = 180
) -> str:
    """Call MiniMax M3 chat completions endpoint."""
    endpoint = f"{provider_config['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {provider_config['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": provider_config["model"],
        "messages": build_messages(prompt, image_data_url, mode),
        "max_tokens": 2048,
        "temperature": 0.1
    }

    proxies = None
    if no_proxy:
        proxies = {"http": None, "https": None}

    response = requests.post(
        endpoint,
        headers=headers,
        json=payload,
        timeout=timeout,
        proxies=proxies
    )
    response.raise_for_status()

    result = response.json()
    if "choices" not in result or not result["choices"]:
        raise ValueError(f"Unexpected MiniMax response format: {json.dumps(result, indent=2)}")

    return result["choices"][0]["message"]["content"]


def _try_ocr_with_config(
    provider_config: Dict,
    prompt: str,
    image_data_url: str,
    mode: str,
    no_proxy: bool,
    timeout: int,
    max_retries: int,
    provider_label: str
) -> Optional[str]:
    """Try OCR with a single provider/endpoint config."""
    endpoint_type = provider_config.get("endpoint_type", "openai_compatible")

    for attempt in range(max_retries):
        try:
            if endpoint_type == "openai_compatible":
                text = request_openai_compatible(
                    provider_config=provider_config,
                    prompt=prompt,
                    image_data_url=image_data_url,
                    mode=mode,
                    no_proxy=no_proxy,
                    timeout=timeout
                )
            elif endpoint_type == "minimax":
                text = request_minimax(
                    provider_config=provider_config,
                    prompt=prompt,
                    image_data_url=image_data_url,
                    mode=mode,
                    no_proxy=no_proxy,
                    timeout=timeout
                )
            else:
                raise ValueError(f"Unknown endpoint type: {endpoint_type}")

            print(f"✓ Successfully recognized text with {provider_label}")
            return text

        except requests.exceptions.Timeout:
            print(f"✗ Attempt {attempt + 1}/{max_retries}: Request timed out")
        except requests.exceptions.ConnectionError:
            print(f"✗ Attempt {attempt + 1}/{max_retries}: Connection error")
        except requests.exceptions.HTTPError as e:
            print(f"✗ Attempt {attempt + 1}/{max_retries}: HTTP {e.response.status_code}")
            try:
                error_detail = e.response.json()
                print(f"  Error: {json.dumps(error_detail, indent=2)}")
            except:
                pass
        except Exception as e:
            print(f"✗ Attempt {attempt + 1}/{max_retries}: {str(e)}")

        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            print(f"  Waiting {wait_time}s before retry...")
            time.sleep(wait_time)

    print(f"✗ {provider_label} failed after {max_retries} attempts")
    return None


def recognize_with_fallback(
    config: Dict,
    image_path: str,
    prompt: str,
    mode: str = "ocr",
    no_proxy: bool = False,
    preferred_provider: Optional[str] = None
) -> tuple:
    """Recognize text with automatic provider fallback."""
    providers = config.get("providers", {})
    fallback_order = config.get("fallback_order", list(providers.keys()))
    timeout = config.get("timeout", 180)
    max_retries = config.get("max_retries", 3)

    if preferred_provider and preferred_provider in providers:
        provider_order = [preferred_provider] + [p for p in fallback_order if p != preferred_provider]
    else:
        provider_order = fallback_order

    image_data_url = encode_image_to_base64(image_path)
    last_error = None

    for provider_name in provider_order:
        if provider_name not in providers:
            print(f"Warning: Provider '{provider_name}' not configured, skipping...")
            continue

        provider_config = providers[provider_name]

        print(f"\n{'='*60}")
        print(f"Trying provider: {provider_name} ({provider_config.get('model', 'unknown')})")
        print(f"Endpoint type: {provider_config.get('endpoint_type', 'openai_compatible')}")
        print(f"{'='*60}")

        endpoints = provider_config.get("endpoints")
        if endpoints and isinstance(endpoints, list):
            print(f"Found {len(endpoints)} endpoint(s) for load balancing")

            for idx, endpoint in enumerate(endpoints):
                endpoint_config = {
                    **provider_config,
                    **endpoint,
                    "endpoint_type": provider_config.get("endpoint_type", "openai_compatible")
                }
                endpoint_config.pop("endpoints", None)
                endpoint_label = f"{provider_name} [endpoint {idx + 1}/{len(endpoints)}: {endpoint_config.get('base_url', 'unknown')}]"
                print(f"\n  -> Trying {endpoint_label}")

                text = _try_ocr_with_config(
                    provider_config=endpoint_config,
                    prompt=prompt,
                    image_data_url=image_data_url,
                    mode=mode,
                    no_proxy=no_proxy,
                    timeout=timeout,
                    max_retries=max_retries,
                    provider_label=endpoint_label
                )

                if text is not None:
                    return provider_name, text

            last_error = f"Provider {provider_name}: all endpoints failed"
            print(f"✗ Provider {provider_name} failed: all {len(endpoints)} endpoints exhausted")
        else:
            text = _try_ocr_with_config(
                provider_config=provider_config,
                prompt=prompt,
                image_data_url=image_data_url,
                mode=mode,
                no_proxy=no_proxy,
                timeout=timeout,
                max_retries=max_retries,
                provider_label=provider_name
            )

            if text is not None:
                return provider_name, text

            last_error = f"Provider {provider_name} failed"

    raise RuntimeError(f"All providers failed. Last error: {last_error}")


def clean_output(text: str) -> str:
    """Clean model output by removing thinking tags and extracting JSON from fences."""
    import re

    # Remove <think>...</think> blocks (MiniMax-M3 reasoning)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    # Extract JSON from markdown code fence if present
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if json_match:
        candidate = json_match.group(1).strip()
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass

    return text.strip()


def save_output(text: str, output_path: Optional[str], output_format: str = "text") -> None:
    """Save OCR result to file or print to stdout."""
    text = clean_output(text)

    if output_format == "json":
        try:
            parsed = json.loads(text)
            content = json.dumps(parsed, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            content = json.dumps({"text": text}, ensure_ascii=False, indent=2)
    else:
        content = text

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\nOutput saved to: {output_path}")
    else:
        print("\n--- OCR Result ---")
        print(content)
        print("--- End ---")


def main():
    preconfig = get_config()

    parser = argparse.ArgumentParser(
        description="Recognize text from images using Deep Core OCR (multi-provider fallback)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic OCR
    python ocr.py --image document.png --output document.txt

  # Specify provider
    python ocr.py --image document.png --provider qwen-vl --output document.txt

  # Structured extraction
    python ocr.py --image invoice.png --mode structured \\
      --prompt "提取发票编号、金额、日期、供应商，输出 JSON" \\
      --output invoice.json

  # Output JSON format
    python ocr.py --image document.png --format json --output document.json

Providers (fallback order):
  1. deepseek-ocr (DeepSeek-OCR)
  2. qwen-vl (Qwen2.5-VL)
  3. minimax-m3 (MiniMax-M3)
        """
    )

    parser.add_argument("--image", "-i", required=True, help="Path to input image")
    parser.add_argument("--output", "-o", default=None, help="Output file path (default: stdout)")
    parser.add_argument("--prompt", "-p", default=None, help="Custom recognition prompt")
    parser.add_argument("--mode", "-m", default="ocr", choices=["ocr", "structured"],
                        help="Recognition mode: ocr (default) or structured")
    parser.add_argument("--format", default="text", choices=["text", "json"],
                        help="Output format: text (default) or json")
    parser.add_argument("--provider", default=None,
                        choices=list(preconfig.get("providers", {}).keys()),
                        help="Force specific provider (default: auto fallback)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--no-proxy", action="store_true", help="Bypass system proxy settings")

    args = parser.parse_args()

    config = get_config()

    # Resolve prompt
    if args.prompt:
        prompt = args.prompt
    elif args.mode == "structured":
        prompt = config.get("default_structured_prompt", preconfig["default_structured_prompt"])
    else:
        prompt = config.get("default_ocr_prompt", preconfig["default_ocr_prompt"])

    if args.verbose:
        print(f"Configuration:")
        print(f"  Default provider: {config['default_provider']}")
        print(f"  Fallback order: {config['fallback_order']}")
        print(f"  Mode: {args.mode}")
        print(f"  Output format: {args.format}")
        print(f"  Prompt: {prompt}")
        print()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Input image not found: {args.image}")
        sys.exit(1)

    try:
        provider_name, text = recognize_with_fallback(
            config=config,
            image_path=str(image_path),
            prompt=prompt,
            mode=args.mode,
            no_proxy=args.no_proxy,
            preferred_provider=args.provider
        )

        save_output(text, args.output, args.format)

        print(f"\n{'='*60}")
        print(f"✓ Success! Text recognized using {provider_name}")
        print(f"{'='*60}")

    except RuntimeError as e:
        print(f"\n{'='*60}")
        print(f"✗ Failed: {e}")
        print(f"{'='*60}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"✗ Unexpected error: {e}")
        print(f"{'='*60}")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
    write_text(scripts_dir / "ocr.py", ocr_py)
    make_executable(scripts_dir / "ocr.py")

    # ------------------------------------------------------------------
    # scripts/test_installation.py
    # ------------------------------------------------------------------
    test_installation_py = r'''#!/usr/bin/env python3
"""
Test installation script for Deep Core OCR skill.

This script verifies that:
1. All required dependencies are installed
2. Configuration file exists and is valid
3. API endpoints are reachable (optional)

Usage:
    python test_installation.py
    python test_installation.py --test-connections
"""

import sys
import json
from pathlib import Path


def test_dependencies():
    """Test if required dependencies are installed."""
    print("Testing dependencies...")
    ok = True

    try:
        import requests
        print(f"  ✓ requests library installed (version: {requests.__version__})")
    except ImportError:
        print("  ✗ requests library not found")
        print("    Install with: pip install requests")
        ok = False

    try:
        import PIL
        print(f"  ✓ Pillow library installed (version: {PIL.__version__})")
    except ImportError:
        print("  ✗ Pillow library not found")
        print("    Install with: pip install Pillow")
        ok = False

    return ok


def test_config():
    """Test if configuration file exists and is valid."""
    print("\nTesting configuration...")

    script_dir = Path(__file__).parent
    config_path = script_dir.parent / "config.json"

    if not config_path.exists():
        print(f"  ✗ Configuration file not found: {config_path}")
        print(f"    Copy config.sample.json to config.json and fill in your API keys.")
        return False

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        print(f"  ✓ Configuration file loaded")

        if "providers" not in config:
            print("  ✗ Missing 'providers' in configuration")
            return False

        providers = config["providers"]
        print(f"  ✓ Found {len(providers)} provider(s)")

        for provider_name, provider_config in providers.items():
            if "api_key" not in provider_config:
                print(f"  ✗ Provider '{provider_name}' missing 'api_key'")
                return False
            if "base_url" not in provider_config:
                print(f"  ✗ Provider '{provider_name}' missing 'base_url'")
                return False
            if "model" not in provider_config:
                print(f"  ✗ Provider '{provider_name}' missing 'model'")
                return False

            api_key = provider_config["api_key"]
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            print(f"  ✓ Provider '{provider_name}': {provider_config['model']}")
            print(f"    API Key: {masked_key}")
            print(f"    Base URL: {provider_config['base_url']}")

        if "fallback_order" in config:
            print(f"  ✓ Fallback order: {config['fallback_order']}")

        return True

    except json.JSONDecodeError as e:
        print(f"  ✗ Invalid JSON in configuration: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error reading configuration: {e}")
        return False


def test_api_endpoints(test_connections=False):
    """Test if API endpoints are reachable (optional)."""
    if not test_connections:
        print("\nSkipping API endpoint tests (use --test-connections to enable)")
        return True

    print("\nTesting API endpoints...")

    import requests

    script_dir = Path(__file__).parent
    config_path = script_dir.parent / "config.json"

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        providers = config.get("providers", {})

        for provider_name, provider_config in providers.items():
            base_url = provider_config.get("base_url", "")
            print(f"\n  Testing {provider_name} ({base_url})...")

            try:
                response = requests.get(base_url, timeout=10)
                print(f"    ✓ Endpoint reachable (status: {response.status_code})")
            except requests.exceptions.ConnectionError:
                print(f"    ✗ Connection failed")
            except requests.exceptions.Timeout:
                print(f"    ✗ Connection timed out")
            except Exception as e:
                print(f"    ✗ Error: {e}")

        return True

    except Exception as e:
        print(f"  ✗ Error testing endpoints: {e}")
        return False


def main():
    print("=" * 60)
    print("Deep Core OCR - Installation Test")
    print("=" * 60)

    test_connections = "--test-connections" in sys.argv

    results = []
    results.append(("Dependencies", test_dependencies()))
    results.append(("Configuration", test_config()))
    results.append(("API Endpoints", test_api_endpoints(test_connections)))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! Deep Core OCR is ready to use.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
'''
    write_text(scripts_dir / "test_installation.py", test_installation_py)
    make_executable(scripts_dir / "test_installation.py")

    # ------------------------------------------------------------------
    # scripts/example_usage.sh
    # ------------------------------------------------------------------
    example_usage_sh = r'''#!/bin/bash
# Example usage script for Deep Core OCR skill

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Deep Core OCR - Example Usage"
echo "=========================================="

# Example 1: Basic OCR
echo ""
echo "Example 1: Basic OCR"
echo "-------------------------------------------"
echo "Command:"
echo "  python3 $SCRIPT_DIR/ocr.py \\"
echo "    --image input/document.png \\"
echo "    --output output/document.txt"
echo ""
echo "To run this example, uncomment the lines below:"
# python3 "$SCRIPT_DIR/ocr.py" \
#   --image input/document.png \
#   --output output/document.txt

# Example 2: Specify provider
echo ""
echo "Example 2: Specify provider"
echo "-------------------------------------------"
echo "Command:"
echo "  python3 $SCRIPT_DIR/ocr.py \\"
echo "    --image input/document.png \\"
echo "    --provider qwen-vl \\"
echo "    --output output/document.txt"
echo ""
echo "To run this example, uncomment the lines below:"
# python3 "$SCRIPT_DIR/ocr.py" \
#   --image input/document.png \
#   --provider qwen-vl \
#   --output output/document.txt

# Example 3: Structured extraction
echo ""
echo "Example 3: Structured extraction"
echo "-------------------------------------------"
echo "Command:"
echo "  python3 $SCRIPT_DIR/ocr.py \\"
echo "    --image input/invoice.png \\"
echo "    --mode structured \\"
echo "    --prompt '提取发票编号、金额、日期、供应商，输出 JSON' \\"
echo "    --output output/invoice.json"
echo ""
echo "To run this example, uncomment the lines below:"
# python3 "$SCRIPT_DIR/ocr.py" \
#   --image input/invoice.png \
#   --mode structured \
#   --prompt "提取发票编号、金额、日期、供应商，输出 JSON" \
#   --output output/invoice.json

# Example 4: JSON output
echo ""
echo "Example 4: JSON output"
echo "-------------------------------------------"
echo "Command:"
echo "  python3 $SCRIPT_DIR/ocr.py \\"
echo "    --image input/document.png \\"
echo "    --format json \\"
echo "    --output output/document.json"
echo ""
echo "To run this example, uncomment the lines below:"
# python3 "$SCRIPT_DIR/ocr.py" \
#   --image input/document.png \
#   --format json \
#   --output output/document.json

# Example 5: Complex scene with MiniMax-M3
echo ""
echo "Example 5: Complex scene with MiniMax-M3"
echo "-------------------------------------------"
echo "Command:"
echo "  python3 $SCRIPT_DIR/ocr.py \\"
echo "    --image input/scene.png \\"
echo "    --provider minimax-m3 \\"
echo "    --output output/scene.txt"
echo ""
echo "To run this example, uncomment the lines below:"
# python3 "$SCRIPT_DIR/ocr.py" \
#   --image input/scene.png \
#   --provider minimax-m3 \
#   --output output/scene.txt

echo ""
echo "=========================================="
echo "For more information, see:"
echo "  - README.md for quick start"
echo "  - SKILL.md for full documentation"
echo "  - references/ocr-scenario-guide.md for scenario guide"
echo "=========================================="
'''
    write_text(scripts_dir / "example_usage.sh", example_usage_sh)
    make_executable(scripts_dir / "example_usage.sh")

    print("\nSetup complete.")


def main() -> int:
    skill_dir = get_skill_dir()
    print(f"Setting up Deep Core OCR in: {skill_dir}\n")
    setup(skill_dir)
    copy_config_sample_if_needed(skill_dir)
    print("\nNext steps:")
    print("  1. Edit config.json and fill in your API keys.")
    print("  2. Install dependencies: pip install -r scripts/requirements.txt")
    print("  3. Run: python scripts/ocr.py --image input.png --output output.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
