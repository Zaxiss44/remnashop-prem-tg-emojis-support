from typing import Final, Optional

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import StartMode
from aiogram_dialog.widgets.kbd import Button, CopyText, Group, ListGroup, Row, Start, Url, WebApp
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format
from magic_filter import F

from src.core.constants import DOCS, GOTO_PREFIX, PAYMENT_PREFIX, REPOSITORY, T_ME
from src.core.enums import ButtonType, PurchaseType
from src.telegram.states import DashboardUser, MainMenu, Notification, Subscription
from src.telegram.widgets import DynamicEmojiStyle, I18nEmojiStyle, I18nFormat
from src.telegram.widgets.emoji_config import get_emoji_id

CALLBACK_CHANNEL_CONFIRM: Final[str] = "channel_confirm"
CALLBACK_RULES_ACCEPT: Final[str] = "rules_accept"


async def on_custom_text_button(
    callback: "CallbackQuery",
    widget: "Button",
    dialog_manager: "DialogManager",
) -> None:
    """Handle TEXT-type custom buttons — sends the payload text as a message."""
    # item_id is set by ListGroup to the index of the clicked button
    item_id = getattr(dialog_manager, "item_id", None)
    if item_id is None:
        await callback.answer("Ошибка: кнопка не найдена", show_alert=True)
        return

    # Look up the payload from the map populated by the getter
    buttons_info = dialog_manager.dialog_data.get("text_buttons", {})
    btn_info = buttons_info.get(str(item_id))

    if not btn_info or not btn_info.get("payload"):
        await callback.answer("Текст не задан", show_alert=True)
        return

    payload = btn_info["payload"]
    disable_preview = btn_info.get("disable_web_page_preview", False)
    inline_buttons_data = btn_info.get("inline_buttons", [])
    
    i18n = dialog_manager.middleware_data.get("i18n")

    builder = InlineKeyboardBuilder()
    for ib in inline_buttons_data:
        text = ib["text"]
        if i18n and (text.startswith("btn-") or text.startswith("msg-")):
            text = i18n.get(text)
            
        cb_data = ib.get("callback_data")
        if cb_data == "back_to_menu":
            cb_data = f"{GOTO_PREFIX}{MainMenu.MAIN.state}"
            
        btn = InlineKeyboardButton(
            text=text,
            url=ib.get("url"),
            callback_data=cb_data,
        )
        if ib.get("emoji_id"):
            btn.icon_custom_emoji_id = ib["emoji_id"]
        builder.row(btn)

    reply_markup = builder.as_markup() if inline_buttons_data else None

    if callback.message:
        await callback.message.answer(
            text=payload,
            reply_markup=reply_markup,
            link_preview_options=LinkPreviewOptions(is_disabled=disable_preview) if disable_preview else None
        )
    await callback.answer()


def build_buttons_row(row: int) -> Group:
    return Group(
        ListGroup(
            Url(
                text=Format("{item.text}"),
                url=Format("{item.payload}"),
                when=F["item"].type == ButtonType.URL,
                style=DynamicEmojiStyle(emoji_id=F["item"].emoji_id),
            ),
            CopyText(
                text=Format("{item.text}"),
                copy_text=Format("{item.payload}"),
                when=F["item"].type == ButtonType.COPY,
                style=DynamicEmojiStyle(emoji_id=F["item"].emoji_id),
            ),
            WebApp(
                text=Format("{item.text}"),
                url=Format("{item.payload}"),
                when=F["item"].type == ButtonType.WEB_APP,
                style=DynamicEmojiStyle(emoji_id=F["item"].emoji_id),
            ),
            Button(
                text=Format("{item.text}"),
                id="text_send",
                on_click=on_custom_text_button,
                when=F["item"].type == ButtonType.TEXT,
                style=DynamicEmojiStyle(emoji_id=F["item"].emoji_id),
            ),
            id=f"custom_buttons_row_{row}",
            items=f"row_{row}_buttons",
            item_id_getter=lambda item: item.index,
        ),
        width=2,
    )


custom_buttons = (
    build_buttons_row(1),
    build_buttons_row(2),
    build_buttons_row(3),
)


connect_buttons = (
    WebApp(
        text=I18nFormat("btn-menu.connect"),
        url=Format("{connection_url}"),
        id="connect_miniapp",
        when=F["is_mini_app"] & F["connectable"],
        style=I18nEmojiStyle("btn-menu.connect", ButtonStyle.PRIMARY),
    ),
    Url(
        text=I18nFormat("btn-menu.connect"),
        url=Format("{connection_url}"),
        id="connect_sub_page",
        when=~F["is_mini_app"] & F["connectable"],
        style=I18nEmojiStyle("btn-menu.connect", ButtonStyle.PRIMARY),
    ),
)

main_menu_button = (
    Start(
        text=I18nFormat("btn-back.menu"),
        id="back_main_menu",
        state=MainMenu.MAIN,
        mode=StartMode.RESET_STACK,
        style=I18nEmojiStyle("btn-back.menu"),
    ),
)

back_main_menu_button = (
    Row(
        Start(
            text=I18nFormat("btn-back.menu-return"),
            id="back_main_menu",
            state=MainMenu.MAIN,
            mode=StartMode.RESET_STACK,
        ),
    ),
)


CLOSE_BUTTON_ID: Final[int] = -1


def get_close_notification_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="btn-common.notification-close",
        callback_data=Notification.CLOSE.state,
        icon_custom_emoji_id=get_emoji_id("btn-common.notification-close"),
    )


def get_broadcast_buttons(support_url: str, is_referral_enable: bool) -> list[InlineKeyboardButton]:
    buttons = [
        InlineKeyboardButton(
            text="btn-goto.contact-support",
            url=support_url,
        ),
        InlineKeyboardButton(
            text="btn-goto.subscription",
            callback_data=f"{GOTO_PREFIX}{Subscription.MAIN.state}",
        ),
        InlineKeyboardButton(
            text="btn-goto.promocode",
            callback_data=f"{GOTO_PREFIX}{Subscription.PROMOCODE.state}",
        ),
    ]

    if is_referral_enable:
        buttons.append(
            InlineKeyboardButton(
                text="btn-goto.invite",
                callback_data=f"{GOTO_PREFIX}{MainMenu.INVITE.state}",
            )
        )

    buttons.append(get_close_notification_button())

    return buttons


def get_renew_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="btn-goto.subscription-renew",
            callback_data=f"{GOTO_PREFIX}{PAYMENT_PREFIX}{PurchaseType.RENEW}",
        ),
    )
    return builder.as_markup()


def get_buy_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="btn-goto.subscription",
            callback_data=f"{GOTO_PREFIX}{PAYMENT_PREFIX}{PurchaseType.NEW}",
        ),
    )
    return builder.as_markup()


def get_channel_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="btn-requirement.channel-join",
            url=channel_url,
            style=ButtonStyle.PRIMARY,
            icon_custom_emoji_id=get_emoji_id("btn-requirement.channel-join"),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="btn-requirement.channel-confirm",
            callback_data=CALLBACK_CHANNEL_CONFIRM,
            style=ButtonStyle.SUCCESS,
            icon_custom_emoji_id=get_emoji_id("btn-requirement.channel-confirm"),
        ),
    )
    return builder.as_markup()


def get_rules_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="btn-requirement.rules-accept",
            callback_data=CALLBACK_RULES_ACCEPT,
            style=ButtonStyle.SUCCESS,
            icon_custom_emoji_id=get_emoji_id("btn-requirement.rules-accept"),
        ),
    )
    return builder.as_markup()


def get_contact_support_keyboard(support_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="btn-goto.contact-support", url=support_url))
    return builder.as_markup()


def get_remnashop_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="btn-remnashop-info.github", url=REPOSITORY),
        InlineKeyboardButton(text="btn-remnashop-info.telegram", url=f"{T_ME}remna_shop"),
    )

    builder.row(
        InlineKeyboardButton(
            text="btn-remnashop-info.donate",
            url="https://boosty.to/snoups",
        )
    )

    return builder.as_markup()


def get_remnashop_update_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="btn-remnashop-info.release-latest",
            url=DOCS,
            style=ButtonStyle.PRIMARY,
        ),
        InlineKeyboardButton(
            text="btn-remnashop-info.how-upgrade",
            url=f"{DOCS}/docs/ru/install/update",
            style=ButtonStyle.PRIMARY,
        ),
    )

    return builder.as_markup()


def get_user_keyboard(
    telegram_id: int,
    referrer_telegram_id: Optional[int] = None,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="btn-goto.user-profile",
            callback_data=f"{GOTO_PREFIX}{DashboardUser.MAIN.state}:{telegram_id}",
        ),
    )

    if referrer_telegram_id:
        builder.row(
            InlineKeyboardButton(
                text="btn-goto.referrer-profile",
                callback_data=f"{GOTO_PREFIX}{DashboardUser.MAIN.state}:{referrer_telegram_id}",
            ),
        )

    return builder.as_markup()


def get_boosty_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="⚡ BOOSTY",
            url="https://boosty.to/snoups",
        ),
    )

    return builder.as_markup()
