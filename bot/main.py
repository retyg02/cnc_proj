import asyncio
import sys
from aiogram import Bot, Dispatcher, html, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config import TOKEN, ADMIN_ID
from db import get_user_from_db, update_user_role, register_guest, get_machines_telemetry, toggle_user_alert, get_broken_machines_to_alert, get_active_admins, get_system_action_logs
import keyboards as kb
from middlewares import AccessCheckMiddleware


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class AccessManagement(StatesGroup):
    waiting_for_user_id = State()

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
dp.message.outer_middleware(AccessCheckMiddleware())

@dp.message(AccessManagement.waiting_for_user_id)
async def process_user_id_input(message: Message, state: FSMContext):
    target_id_str = message.text
    if not target_id_str.isdigit():
        await message.answer(
            "⚠️ <b>Invalid format!</b> Please enter a valid numerical Telegram ID:",
            reply_markup=kb.get_cancel_fsm_keyboard()
        )
        return
    target_id = int(target_id_str)
    target_user = await get_user_from_db(target_id)
    if not target_user:
        await message.answer(
            f"🔍 <b>User not found!</b>\n\n"
            f"Telegram ID <code>{target_id}</code> is not registered in the database.\n"
            f"Check the ID and try again or cancel the operation:",
            reply_markup=kb.get_cancel_fsm_keyboard()
        )
        return
    await state.clear()
    await message.answer(
        f"👤 <b>User Management Card</b>\n"
        f"----------------------------------------\n"
        f"🏷️ Name: <b>{target_user['name']}</b>\n"
        f"🆔 ID: <code>{target_id}</code>\n"
        f"🔐 Current Role: <u>{target_user['role'].upper()}</u>\n"
        f"----------------------------------------\n"
        f"Select the action you want to perform:",
        reply_markup=kb.get_role_management_keyboard(target_id) 
    )

@dp.callback_query(F.data.startswith("set_op_") | F.data.startswith("set_ad_") | F.data.startswith("set_block_"))
async def process_role_change_callback(callback: CallbackQuery):
    action, target_id_str = callback.data.rsplit("_", 1)
    target_id = int(target_id_str)
    target_user = await get_user_from_db(target_id)    
    if not target_user:
        await callback.answer("⚠️ User no longer exists in database!", show_alert=True)
        return
    current_role = target_user["role"]
    if action == "set_op":
        new_role = "operator"
    elif action == "set_ad":
        new_role = "admin"
    else:
        new_role = "block"
    if current_role == "admin" and (new_role == "operator" or new_role == "block"):
        await callback.answer(
            text="❌ Security Violation!\nYou cannot demote an Administrator to an Operator or block him.", 
            show_alert=True
        )
        return 
    await update_user_role(target_id, new_role)
    await callback.message.edit_text(
        f"✅ <b>Role updated successfully!</b>\n\n"
        f"User ID: <code>{target_id}</code> (<b>{target_user['name']}</b>)\n"
        f"New system role: <u>{new_role.upper()}</u>"
    )
    try:
        if new_role == "admin":
            text_to_user = "🎉 <b>Access level upgraded!</b>\n\nYou have been appointed as an Administrator. Type /start to open Admin Panel."
            markup_to_user = kb.get_admin_keyboard()
        elif new_role == "operator":
            text_to_user = "🎉 <b>Access level updated!</b>\n\nYou have been approved as a Workshop Operator. Type /start to open Operator Panel."
            markup_to_user = kb.get_operator_keyboard()
        else:
            text_to_user = "❌ <b>Access revoked!</b>\n\nYour account has been blocked by the system administrator."
            markup_to_user = None
        await bot.send_message(chat_id=target_id, text=text_to_user, reply_markup=markup_to_user)
    except Exception as e:
        print(f"Could not notify user {target_id}: {e}")
    await callback.answer()

@dp.message(F.text == "👥 Access managing")
async def cmd_access_managing(message: Message, state: FSMContext, user_data: dict):
    await state.set_state(AccessManagement.waiting_for_user_id)    
    await message.answer(
        "👥 <b>Access Management Mode Active</b>\n\n"
        "Please enter the Telegram ID of the user you want to manage:",
        reply_markup=kb.get_cancel_fsm_keyboard() 
    )

@dp.callback_query(F.data == "cancel_fsm")
async def process_cancel_fsm(callback: CallbackQuery, state: FSMContext):
    await state.clear()    
    await callback.message.edit_text(
        "❌ <b>Operation cancelled.</b> Access management mode turned off."
    )
    await callback.answer()

@dp.message(F.text == "📜 Logs")
async def cmd_view_logs(message: Message, user_data: dict):
    raw_logs = await get_system_action_logs()    
    if not raw_logs:
        await message.answer("📭 <b>System event logs are empty.</b>")
        return
    file_content = "=== PRODUCTION TELEMETRY SYSTEM LOGS ===\n\n"
    for log in raw_logs:
        timestamp = log["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        file_content += f"[{timestamp}] User ID: {log['telegram_id']} -> {log['action_text']}\n"
    text_bytes = file_content.encode("utf-8")    
    document_file = BufferedInputFile(text_bytes, filename="system_logs.txt")
    await message.answer_document(
        document=document_file,
        caption="📋 <b>Current system event logs generated.</b>",
        reply_markup=kb.get_close_inline_keyboard()
    )

@dp.message(F.text == '⚙️ Settings')
async def cmd_settings(message: Message, user_data: dict):
    is_enabled = user_data.get("alerts_enabled", True)
    await message.answer(
        "⚙️ <b>Security notification config</b>",
        reply_markup=kb.get_settings_inline_keyboard(is_enabled)
    )

@dp.callback_query(F.data == 'toggle_alerts')
async def process_toggle_alerts(callback: CallbackQuery):
    user_id = callback.from_user.id
    new_status = await toggle_user_alert(user_id)
    try:
        await callback.message.edit_reply_markup(
            reply_markup=kb.get_settings_inline_keyboard(new_status)
        )
    except:
        pass
    toast_text = '🔔 Notification enabled' if new_status else '🔕 Notification disabled'
    await callback.answer(text=toast_text, show_alert=True)

@dp.callback_query(F.data == 'delete_message')
async def process_delete_message(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception as e:
        print(f"Error: {e}")

    await callback.answer()

@dp.callback_query(F.data.startswith('approve_') | F.data.startswith('block_'))
async def process_approve_callback(callback: CallbackQuery):
    action, operator_id_str = callback.data.split('_')
    operator_id = int(operator_id_str) 
    if action == 'approve':
        await update_user_role(operator_id, 'operator')
        await callback.message.edit_text(
            f"{callback.message.text}\n\n✅ <b>User has been added</b>"
        )
        try:
            await bot.send_message(
                chat_id=operator_id,
                text="🎉 <b>Access has approved</b>",
                reply_markup=kb.get_operator_keyboard()
            )
        except Exception as e:
            print(f'Error: {e}')        
    elif action == 'block':
        await update_user_role(operator_id, 'block')
        await callback.message.edit_text(
            f"{callback.message.text}\n\n🚫 <b>User has been blocked</b>"
        )
        try:
            await bot.send_message(
                chat_id=operator_id,
                text="🚫 <b>Access has blocked</b>",
                reply_markup=None
            )
        except Exception as e:
            print(f'Error: {e}')

@dp.message(F.contact)
async def handle_contact(message: Message):
    user_id = message.contact.user_id
    phone_number = message.contact.phone_number
    real_name = message.contact.first_name
    if user_id != message.from_user.id:
        await message.answer(
            "⚠️ <b>Verification error</b>\n\n"
            "You should send YOUR real contact tapping button below the textarea"
        )
        return
    await register_guest(user_id, real_name, phone_number)
    await bot.send_message(
        chat_id=ADMIN_ID,
        text="🔔 <b>New application</b>\n\n"
            f"👤 Name: {html.bold(real_name)}\n"
            f"📱 Phone: {html.bold(phone_number)}\n"
            f"🆔 TG_id: <code>{user_id}</code>",
        reply_markup=kb.get_approve_inline_keyboard(user_id)
    )
    await message.answer(
        "⏳ <b>Application has sent...</b>", reply_markup=None
    )

@dp.message(CommandStart())
async def cmd_start(message: Message):   
    user_id = message.from_user.id
    first_name = message.from_user.first_name    
    user_data = await get_user_from_db(user_id)    
    if user_data:
        role = user_data['role']
        if role == 'admin':
            await message.answer(
                f"Hello, {html.bold(first_name)} ({html.underline('admin')})\n", reply_markup=kb.get_admin_keyboard()
            )
        elif role == 'operator':
            await message.answer(
                f"Hello, {html.bold(first_name)} ({html.underline('operator')})\n", reply_markup=kb.get_operator_keyboard()
            )
    else:
        await message.answer(
            f"Your role is a guest\n\n"        
            f"🚫 Access forbidden, {html.bold(first_name)}.\n\n"
            f"Telegram ID (<code>{user_id}</code>) is not signed up in the system.", reply_markup=kb.get_guest_keyboard()
        )

@dp.message(F.text == '📊 Observing')
async def cmd_observing(message: Message, user_data: dict):
    machines = await get_machines_telemetry()
    report = f"<b>Machines status dynamics</b>\n\n"
    report += f"------------------------------------------------------------\n"
    for item in machines:
        if item['status'] == 'working':
            status_ico = '🟢'
            status_text = f"Working (Imposure: {item['load_percent']}%)\n └ {item['details']}"
        elif item['status'] == 'idle':
            status_ico = '🟡'
            status_text = f"On-line (Empty)\n └ Error: <pre>{item['details']}</pre>"
        else:
            status_ico = '🔴'
            status_text = f"<b>Failure</b> (Imposure: {item['load_percent']}%)\n └ {item['details']}"
        report += f"{status_ico} <b>{item['name']} [ID: {item['id']}]:</b>\n └ {status_text}\n\n"
    report += f"------------------------------------------------------------\n"
    report += f"👤 Report has generated for: {html.bold(user_data['name'])}"
    await message.answer(report, reply_markup=kb.get_close_inline_keyboard())

async def background_machine_checker():
    while True:
        try:
            broken_machines = await get_broken_machines_to_alert()
            if broken_machines:
                admin_ids = await get_active_admins()
                if admin_ids:
                    for machine in broken_machines:
                        alert_text = (
                            f"🚨 <b>Machines failure</b>\n\n"
                            f"------------------------------------------------------------\n"
                            f"⚙️ Machine: <b>{machine['name']} [ID: {machine['id']}]</b>\n"
                            f"❌ Error: <pre>{machine['details']}</pre>\n"
                            f"------------------------------------------------------------\n"
                            f"⏳ Next notification will be sent not earlier then at least 4 mins"
                        )
                        for admin_id in admin_ids:
                            try:
                                await bot.send_message(chat_id=admin_id, text=alert_text)
                            except Exception as e:
                                print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        await asyncio.sleep(10)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(background_machine_checker())
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    asyncio.run(main())

