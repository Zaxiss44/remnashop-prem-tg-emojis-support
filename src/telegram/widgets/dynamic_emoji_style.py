from typing import Optional, Union

from aiogram.enums import ButtonStyle
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.style import BaseStyle
from magic_filter import MagicFilter


class DynamicEmojiStyle(BaseStyle):
    """Style widget that reads emoji_id dynamically from data via MagicFilter."""

    def __init__(
        self,
        emoji_id: Union[MagicFilter, str, None] = None,
        style: Optional[ButtonStyle] = None,
        when: WhenCondition = None,
    ):
        super().__init__(when=when)
        self._emoji_id = emoji_id
        self._style = style

    async def _render_style(
        self,
        data: dict,
        manager: DialogManager,
    ) -> ButtonStyle | None:
        return self._style

    async def _render_emoji(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str | None:
        if self._emoji_id is None:
            return None
        if isinstance(self._emoji_id, str):
            return self._emoji_id
        if isinstance(self._emoji_id, MagicFilter):
            result = self._emoji_id.resolve(data)
            return result if isinstance(result, str) else None
        return None


class I18nEmojiStyle(BaseStyle):
    """Style that looks up emoji_id from emoji_config.json by i18n button key.

    Usage:
        Button(
            text=I18nFormat("btn-menu.connect"),
            style=I18nEmojiStyle("btn-menu.connect"),
            ...
        )

    Configure emoji IDs in assets/emoji_config.json.
    """

    def __init__(
        self,
        i18n_key: str,
        style: Optional[ButtonStyle] = None,
        when: WhenCondition = None,
    ):
        super().__init__(when=when)
        self._i18n_key = i18n_key
        self._style = style

    async def _render_style(
        self,
        data: dict,
        manager: DialogManager,
    ) -> ButtonStyle | None:
        return self._style

    async def _render_emoji(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str | None:
        from .emoji_config import get_emoji_id

        return get_emoji_id(self._i18n_key)
