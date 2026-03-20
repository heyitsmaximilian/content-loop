#!/usr/bin/env python3
"""
Content Loop - Configuration Loader
Loads config.yaml and provides typed access to settings.
Falls back to sensible defaults if config is missing.
"""

import os
import sys
from typing import Dict, Any, Optional

# Try yaml import, fall back to basic parsing if not installed
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# Defaults matching config.example.yaml
DEFAULTS = {
    "product": "default",
    "analysis": {
        "default_lookback_days": 3,
        "min_posts_for_amendments": 3,
        "thresholds": {
            "good_views": 10000,
            "excellent_views": 50000,
            "good_engagement_rate": 0.05,
            "excellent_engagement_rate": 0.10,
            "good_conversion_rate": 0.001,
            "excellent_conversion_rate": 0.005,
            "degradation_threshold": 0.3,
        },
    },
    "experiments": {
        "default_duration": 7,
        "max_variants_per_experiment": 4,
        "min_posts_per_variant": 2,
        "max_experiment_duration": 14,
    },
    "amendments": {
        "create_backups": True,
        "auto_apply": False,
        "confidence_threshold": 0.7,
        "managed_files": ["hooks.md", "ctas.md", "images.md"],
    },
    "storage": {
        "data_dir": "data",
        "log_file": "run-log.jsonl",
        "retention_days": 90,
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge override into base, recursing into nested dicts."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _find_config_file() -> Optional[str]:
    """Search for config.yaml in standard locations."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(root, "config.yaml"),
        os.path.join(root, "config.yml"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file, merged with defaults.

    Resolution order:
      1. Explicit config_path argument
      2. CONTENT_LOOP_CONFIG env var
      3. Auto-detect config.yaml in repo root
      4. Defaults only
    """
    if config_path is None:
        config_path = os.environ.get("CONTENT_LOOP_CONFIG")
    if config_path is None:
        config_path = _find_config_file()

    if config_path and os.path.exists(config_path):
        if not HAS_YAML:
            print(
                "Warning: PyYAML not installed. Run `pip install pyyaml` to load config.yaml. Using defaults.",
                file=sys.stderr,
            )
            return DEFAULTS.copy()

        with open(config_path, "r") as f:
            user_config = yaml.safe_load(f) or {}
        return _deep_merge(DEFAULTS, user_config)

    return DEFAULTS.copy()


# ── Convenience accessors ──────────────────────────────────────

class Config:
    """Typed wrapper around the config dict."""

    def __init__(self, config_path: Optional[str] = None):
        self._data = load_config(config_path)
        self._root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # ── Product ──

    @property
    def product(self) -> str:
        return self._data.get("product", "default")

    # ── Paths ──

    @property
    def data_dir(self) -> str:
        rel = self._data.get("storage", {}).get("data_dir", "data")
        return os.path.join(self._root, rel)

    @property
    def log_file(self) -> str:
        filename = self._data.get("storage", {}).get("log_file", "run-log.jsonl")
        return os.path.join(self.data_dir, filename)

    @property
    def knowledge_dir(self) -> str:
        """Returns product-specific knowledge directory if it exists, else generic."""
        product_dir = os.path.join(self._root, "knowledge", self.product)
        if os.path.isdir(product_dir):
            return product_dir
        return os.path.join(self._root, "knowledge")

    @property
    def skills_dir(self) -> str:
        return os.path.join(self._root, "skills")

    # ── Analysis ──

    @property
    def default_lookback_days(self) -> int:
        return self._data.get("analysis", {}).get("default_lookback_days", 3)

    @property
    def min_posts_for_amendments(self) -> int:
        return self._data.get("analysis", {}).get("min_posts_for_amendments", 3)

    @property
    def thresholds(self) -> Dict[str, float]:
        return self._data.get("analysis", {}).get("thresholds", DEFAULTS["analysis"]["thresholds"])

    # ── Experiments ──

    @property
    def default_experiment_duration(self) -> int:
        return self._data.get("experiments", {}).get("default_duration", 7)

    @property
    def max_variants(self) -> int:
        return self._data.get("experiments", {}).get("max_variants_per_experiment", 4)

    # ── Amendments ──

    @property
    def create_backups(self) -> bool:
        return self._data.get("amendments", {}).get("create_backups", True)

    @property
    def auto_apply(self) -> bool:
        return self._data.get("amendments", {}).get("auto_apply", False)

    @property
    def managed_files(self):
        return self._data.get("amendments", {}).get("managed_files", ["hooks.md", "ctas.md", "images.md"])

    # ── Raw access ──

    def get(self, *keys, default=None):
        """Dot-path access: config.get('analysis', 'thresholds', 'good_views')"""
        node = self._data
        for key in keys:
            if isinstance(node, dict):
                node = node.get(key)
            else:
                return default
            if node is None:
                return default
        return node
