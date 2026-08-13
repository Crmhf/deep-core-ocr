#!/usr/bin/env python3
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
