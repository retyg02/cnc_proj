from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_close_inline_keyboard() -> InlineKeyboardMarkup:
    builder= InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='❌ Close', callback_data='delete_message'))
    return builder.as_markup()

def get_approve_inline_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='✅ Accept', callback_data=f"approve_{telegram_id}"),
        InlineKeyboardButton(text='🚫 Block', callback_data=f"block_{telegram_id}")
    )
    return builder.as_markup()

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📊 Observing"),
        KeyboardButton(text="📜 Logs")
    )
    builder.row(
            KeyboardButton(text="👥 Access managing"),
            KeyboardButton(text="⚙️ Settings")
        )
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Admin panel is running"
    )

def get_operator_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📊 Observing"),
        KeyboardButton(text="⚠️ Report a failure")
    )
    return builder.as_markup(
        resize_keyboard=True, 
        input_field_placeholder="Operator functions are acceptable"
    )

def get_guest_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🔐 Send an access request", request_contact=True)
    )
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Access is restricted"
    )

def get_settings_inline_keyboard(notification_enabled: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    status_emoji = '✅ On' if notification_enabled else '❌ Off'
    builder.row(
        InlineKeyboardButton(text=f"🔔 Alerts: {status_emoji}", callback_data="toggle_alerts")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Close", callback_data="delete_message")
    )
    return builder.as_markup()

def get_cancel_fsm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Cancel operation", callback_data="cancel_fsm"))
    return builder.as_markup()

def get_role_management_keyboard(target_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⚙️ Make Operator", callback_data=f"set_op_{target_id}"),
        InlineKeyboardButton(text="🔑 Make Admin", callback_data=f"set_ad_{target_id}"),
        InlineKeyboardButton(text="🚫 Block (Ban)", callback_data=f"set_block_{target_id}")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_fsm")
    )
    return builder.as_markup()
