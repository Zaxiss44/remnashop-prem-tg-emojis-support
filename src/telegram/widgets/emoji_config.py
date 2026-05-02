import json
from pathlib import Path
from typing import Optional

from loguru import logger

from src.core.constants import ASSETS_DIR

_EMOJI_CONFIG_PATH: Path = ASSETS_DIR / "emoji_config.json"
_emoji_map: dict[str, str] = {}
_loaded: bool = False


def _load_emoji_config() -> None:
    global _emoji_map, _loaded

    if _loaded:
        return

    if not _EMOJI_CONFIG_PATH.exists():
        logger.debug(f"Emoji config not found at '{_EMOJI_CONFIG_PATH}', skipping")
        _loaded = True
        return

    try:
        with open(_EMOJI_CONFIG_PATH, encoding="utf-8") as f:
            raw = json.load(f)

        _emoji_map = {
            k: v for k, v in raw.items() if not k.startswith("_") and isinstance(v, str)
        }
        logger.info(f"Loaded emoji config with {len(_emoji_map)} mapping(s)")
    except Exception as e:
        logger.error(f"Failed to load emoji config: {e}")

    _loaded = True


def get_emoji_id(i18n_key: str) -> Optional[str]:
    """Get custom emoji ID for a button by its i18n key."""
    _load_emoji_config()
    return _emoji_map.get(i18n_key)


def reload_emoji_config() -> None:
    """Force reload of emoji config (e.g. after admin changes)."""
    global _loaded
    _loaded = False
    _load_emoji_config()
