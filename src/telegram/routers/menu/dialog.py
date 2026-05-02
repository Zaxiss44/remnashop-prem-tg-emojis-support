from aiogram.enums import ButtonStyle
from aiogram_dialog import Dialog, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Button,
    CopyText,
    ListGroup,
    Row,
    Start,
    SwitchInlineQueryChosenChatButton,
    SwitchTo,
    Url,
)
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format
from magic_filter import F

from src.application.common.policy import Permission
from src.core.constants import INLINE_QUERY_INVITE, PAYMENT_PREFIX
from src.core.enums import BannerName
from src.telegram.keyboards import connect_buttons, custom_buttons
from src.telegram.routers.dashboard.users.handlers import on_user_search
from src.telegram.states import Dashboard, MainMenu, Subscription
from src.telegram.utils import require_permission
from src.telegram.widgets import Banner, I18nEmojiStyle, I18nFormat, IgnoreUpdate
from src.telegram.window import Window

from .getters import (
    device_confirm_delete_getter,
    devices_getter,
    invite_about_getter,
    invite_getter,
    menu_getter,
)
from .handlers import (
    on_device_delete_all_confirm,
    on_device_delete_confirm,
    on_device_delete_request,
    on_get_trial,
    on_invite,
    on_reissue_subscription_confirm,
    on_show_qr,
    on_withdraw_points,
    show_reason,
)

menu = Window(
    Banner(BannerName.MENU),
    I18nFormat("msg-main-menu"),
    Row(
        *connect_buttons,
        Button(
            text=I18nFormat("btn-menu.connect-not-available"),
            id="not_available",
            on_click=show_reason,
            when=~F["connectable"],
        ),
        when=F["has_subscription"],
    ),
    Row(
        Button(
            text=I18nFormat("btn-menu.trial"),
            id="trial",
            on_click=on_get_trial,
            when=F["trial_available"],
            style=I18nEmojiStyle("btn-menu.trial", ButtonStyle.SUCCESS),
        ),
    ),
    Row(
        SwitchTo(
            text=I18nFormat("btn-menu.devices"),
            id="devices",
            state=MainMenu.DEVICES,
            when=F["has_device_limit"],
            style=I18nEmojiStyle("btn-menu.devices"),
        ),
        Start(
            text=I18nFormat("btn-menu.subscription"),
            id=f"{PAYMENT_PREFIX}subscription",
            state=Subscription.MAIN,
            style=I18nEmojiStyle("btn-menu.subscription"),
        ),
    ),
    Row(
        Button(
            text=I18nFormat("btn-menu.invite"),
            id="invite",
            on_click=on_invite,
            when=F["referral_enabled"],
            style=I18nEmojiStyle("btn-menu.invite"),
        ),
        SwitchInlineQueryChosenChatButton(
            text=I18nFormat("btn-menu.invite"),
            query=Format(INLINE_QUERY_INVITE),
            allow_user_chats=True,
            allow_group_chats=True,
            allow_channel_chats=True,
            id="send",
            when=~F["referral_enabled"],
            style=I18nEmojiStyle("btn-menu.invite"),
        ),
        Url(
            text=I18nFormat("btn-menu.support"),
            id="support",
            url=Format("{support_url}"),
            style=I18nEmojiStyle("btn-menu.support"),
        ),
    ),
    *custom_buttons,
    Row(
        Start(
            text=I18nFormat("btn-menu.dashboard"),
            id="dashboard",
            state=Dashboard.MAIN,
            mode=StartMode.RESET_STACK,
            when=require_permission(Permission.VIEW_DASHBOARD),
            style=I18nEmojiStyle("btn-menu.dashboard"),
        ),
    ),
    MessageInput(func=on_user_search),
    IgnoreUpdate(),
    state=MainMenu.MAIN,
    getter=menu_getter,
)

devices = Window(
    Banner(BannerName.MENU),
    I18nFormat("msg-menu-devices"),
    Row(
        Button(
            text=I18nFormat("btn-common.devices-empty"),
            id="devices_empty",
            when=~F["has_devices"],
            style=I18nEmojiStyle("btn-common.devices-empty"),
        ),
    ),
    ListGroup(
        Row(
            Button(
                text=Format("{item[label]}"),
                id="device_item",
                on_click=on_device_delete_request,
            ),
        ),
        id="devices_list",
        item_id_getter=lambda item: item["short_hwid"],
        items="devices",
        when=F["has_devices"],
    ),
    Row(
        Start(
            text=I18nFormat("btn-devices.delete-all"),
            id="delete_all",
            state=MainMenu.DEVICE_CONFIRM_DELETE_ALL,
            when=F["has_devices"],
            style=I18nEmojiStyle("btn-devices.delete-all", ButtonStyle.DANGER),
        ),
    ),
    Row(
        Start(
            text=I18nFormat("btn-devices.reissue"),
            id="reissue",
            state=MainMenu.DEVICE_CONFIRM_REISSUE,
            style=I18nEmojiStyle("btn-devices.reissue", ButtonStyle.PRIMARY),
        ),
    ),
    Row(
        SwitchTo(
            text=I18nFormat("btn-back.general"),
            id="back",
            style=I18nEmojiStyle("btn-back.general"),
            state=MainMenu.MAIN,
        ),
    ),
    IgnoreUpdate(),
    state=MainMenu.DEVICES,
    getter=devices_getter,
)

device_confirm_delete = Window(
    Banner(BannerName.MENU),
    I18nFormat("msg-menu-devices-confirm-delete"),
    Row(
        Button(
            text=I18nFormat("btn-devices.confirm-delete"),
            id="confirm_delete",
            on_click=on_device_delete_confirm,
            style=I18nEmojiStyle("btn-devices.confirm-delete", ButtonStyle.DANGER),
        ),
        SwitchTo(
            text=I18nFormat("btn-common.cancel"),
            id="cancel",
            state=MainMenu.DEVICES,
            style=I18nEmojiStyle("btn-common.cancel"),
        ),
    ),
    IgnoreUpdate(),
    state=MainMenu.DEVICE_CONFIRM_DELETE,
    getter=device_confirm_delete_getter,
)

device_confirm_delete_all = Window(
    Banner(BannerName.MENU),
    I18nFormat("msg-menu-devices-confirm-delete-all"),
    Row(
        Button(
            text=I18nFormat("btn-devices.confirm-delete"),
            id="confirm_delete_all",
            on_click=on_device_delete_all_confirm,
            style=I18nEmojiStyle("btn-devices.confirm-delete", ButtonStyle.DANGER),
        ),
        SwitchTo(
            text=I18nFormat("btn-common.cancel"),
            id="cancel",
            state=MainMenu.DEVICES,
            style=I18nEmojiStyle("btn-common.cancel"),
        ),
    ),
    IgnoreUpdate(),
    state=MainMenu.DEVICE_CONFIRM_DELETE_ALL,
    getter=device_confirm_delete_getter,
)

invite = Window(
    Banner(BannerName.REFERRAL),
    I18nFormat("msg-menu-invite"),
    Row(
        SwitchTo(
            text=I18nFormat("btn-invite.about"),
            id="about",
            state=MainMenu.INVITE_ABOUT,
            style=I18nEmojiStyle("btn-invite.about"),
        ),
    ),
    Row(
        CopyText(
            text=I18nFormat("btn-invite.copy"),
            copy_text=Format("{referral_url}"),
            style=I18nEmojiStyle("btn-invite.copy"),
        ),
    ),
    Row(
        Button(
            text=I18nFormat("btn-invite.qr"),
            id="qr",
            on_click=on_show_qr,
            style=I18nEmojiStyle("btn-invite.qr"),
        ),
        SwitchInlineQueryChosenChatButton(
            text=I18nFormat("btn-invite.send"),
            query=Format(INLINE_QUERY_INVITE),
            allow_user_chats=True,
            allow_group_chats=True,
            allow_channel_chats=True,
            id="send",
            style=I18nEmojiStyle("btn-invite.send"),
        ),
    ),
    Row(
        Button(
            text=I18nFormat("btn-invite.withdraw-points"),
            id="withdraw_points",
            on_click=on_withdraw_points,
            when=~F["has_points"],
            style=I18nEmojiStyle("btn-invite.withdraw-points"),
        ),
        Url(
            text=I18nFormat("btn-invite.withdraw-points"),
            id="withdraw_points",
            url=Format("{withdraw}"),
            when=F["has_points"],
            style=I18nEmojiStyle("btn-invite.withdraw-points"),
        ),
        when=F["is_points_reward"],
    ),
    Row(
        SwitchTo(
            text=I18nFormat("btn-back.general"),
            id="back",
            style=I18nEmojiStyle("btn-back.general"),
            state=MainMenu.MAIN,
        ),
    ),
    IgnoreUpdate(),
    state=MainMenu.INVITE,
    getter=invite_getter,
)

invite_about = Window(
    Banner(BannerName.REFERRAL),
    I18nFormat("msg-menu-invite-about"),
    Row(
        SwitchTo(
            text=I18nFormat("btn-back.general"),
            id="back",
            style=I18nEmojiStyle("btn-back.general"),
            state=MainMenu.INVITE,
        ),
    ),
    IgnoreUpdate(),
    state=MainMenu.INVITE_ABOUT,
    getter=invite_about_getter,
)


device_confirm_reissue = Window(
    Banner(BannerName.MENU),
    I18nFormat("msg-menu-devices-confirm-reissue"),
    Row(
        Button(
            text=I18nFormat("btn-devices.confirm-reissue"),
            id="confirm_reissue",
            on_click=on_reissue_subscription_confirm,
            style=I18nEmojiStyle("btn-devices.confirm-reissue", ButtonStyle.DANGER),
        ),
        SwitchTo(
            text=I18nFormat("btn-devices.cancel-reissue"),
            id="cancel_reissue",
            state=MainMenu.DEVICES,
            style=I18nEmojiStyle("btn-devices.cancel-reissue"),
        ),
    ),
    IgnoreUpdate(),
    state=MainMenu.DEVICE_CONFIRM_REISSUE,
    getter=device_confirm_delete_getter,
)

router = Dialog(
    menu,
    devices,
    device_confirm_delete,
    device_confirm_delete_all,
    device_confirm_reissue,
    invite,
    invite_about,
)
