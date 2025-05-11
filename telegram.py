import asyncio
import os

from aiogram import F, types
from dotenv import load_dotenv

load_dotenv()
from aiogram import Bot, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.environ["TELEGRAM_TOKEN"]
dp = Dispatcher()

admins = [7860498898, 6739019257]
from LifeManager.LM import LifeManager
from LifeManager.logger_config import logger
from LifeManager.TM import CTimer

lm = LifeManager()
tm = CTimer()


def is_admin(id) -> bool:
    return id in admins


#! I want to work with inlines and callbacks. It is my preference.
def __keyboard():

    builder = InlineKeyboardBuilder()

    builder.button(text="DTM", callback_data="daily_task_manager")
    builder.button(text="Banking", callback_data="banking")

    builder.adjust(1)

    return builder.as_markup()


@dp.message(lambda x: x.text == "/panel" and is_admin(x.from_user.id))
async def main_panel(msg):
    global sent_sticker
    sent_sticker = await msg.answer_sticker(
        sticker="CAACAgEAAxkBAAMeaBiC9lsHcRNZbo6neK-n0WhBtFgAAroIAAK_jJAEPvqh7iT5WyM2BA"
    )
    # ~ Assign the sticker in a global variable to delete it when recalling this to prevent the un necessary pollution.

    await msg.answer(text="🎛", reply_markup=__keyboard())


@dp.callback_query(F.data == "/panel")
async def main_panel_callback(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    await call.message.delete()
    await call.bot.delete_message(
        chat_id=sent_sticker.chat.id, message_id=sent_sticker.message_id
    )
    await call.bot.send_message(call.message.chat.id, "/panel")
    await main_panel(call.message)


#! ----------- DAILY TASK MANAGER SECTION -----------
def main_dmt_keyboard():

    builder = InlineKeyboardBuilder()

    builder.button(text="Add Daily Tasks", callback_data="add_daily_task")
    builder.button(text="Get All Parent Tasks", callback_data="get_all_parent_tasks")
    builder.button(text="Show All Tables", callback_data="show_all_tables")
    builder.button(text="Insert Task", callback_data="insert_into_weekly_table")

    builder.button(text="Backup", callback_data="backup")
    builder.button(text="Restore backup", callback_data="restore_backup")
    builder.button(text="Timer", callback_data="timer")
    builder.button(text="Return", callback_data="/panel")
    builder.adjust(2)

    return builder.as_markup()


@dp.callback_query(F.data == "daily_task_manager")
async def dmt(call):
    if not is_admin(call.from_user.id):
        return

    await call.message.delete()
    await call.message.answer(text="Choose: ", reply_markup=main_dmt_keyboard())


# ~ -----------START |  Timer section ---------------
def timer_keyboard():

    builder = InlineKeyboardBuilder()

    builder.button(text="Start Timer", callback_data="s_timer")
    builder.button(text="End Timer", callback_data="e_timer")
    builder.button(text="Pause Timer", callback_data="p_timer")
    builder.button(text="Resume Timer", callback_data="r_timer")

    builder.button(text="Return", callback_data="daily_task_manager")

    builder.adjust(1)

    return builder.as_markup()


@dp.callback_query(F.data == "timer")
async def _timer(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    await call.message.delete()
    await call.message.answer(
        text="<b>NOTE: Starting New timer will overwrite the old time</b>",
        reply_markup=timer_keyboard(),
        parse_mode="HTML",
    )


@dp.callback_query(F.data == "s_timer")
async def start_timer(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    try:

        tm.start()

        await call.message.answer(
            text="⏰ Your Time Has Been <b>Started</b>!",
            parse_mode="HTML",
        )
    except:
        await call.message.answer(text="An Error HasBeen occurred. Read Log Files")
        logger.exception("Cannot Start Timer in TelegramBOT.")


@dp.callback_query(F.data == "e_timer")
async def end_timer(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    try:
        global user_time_elapsed
        user_time_elapsed = tm.time_it()
        if not user_time_elapsed:
            await call.message.answer(
                text=f"You Need To First, <b>Start</b> the timer.",
                parse_mode="HTML",
            )
            return

        await call.message.answer(
            text=f"⏰ You Timer Has Been <b>Ended</b> Successfully.\nYou'r Time: {user_time_elapsed} Seconds.",
            parse_mode="HTML",
        )

    except:
        await call.message.answer(text="An Error HasBeen occurred. Read Log Files")
        logger.exception("Cannot End Timer in TelegramBOT.")


@dp.callback_query(F.data == "p_timer")
async def pause_timer(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    try:
        tm.pause()
        await call.message.answer(
            text=f"⏰ You Timer Has Been <b>Paused</b> Successfully.",
            parse_mode="HTML",
        )

    except:
        await call.message.answer(
            text=f"You Need To First, <b>Start</b> the timer.",
            parse_mode="HTML",
        )
        logger.exception("Cannot Pause Timer in TelegramBOT.")


@dp.callback_query(F.data == "r_timer")
async def resume_timer(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    try:
        tm.resume()
        await call.message.answer(
            text=f"⏰ You Timer Has Been <b>Resumed</b> Successfully.",
            parse_mode="HTML",
        )

    except:
        await call.message.answer(
            text=f"You Need To First, <b>Start</b> the timer.",
            parse_mode="HTML",
        )
        logger.exception("Cannot Resume Timer in TelegramBOT.")


# ~ -----------END |  Timer section ---------------


@dp.callback_query(lambda x: x.data == "add_daily_task")
async def add_daily_task(call):
    if not is_admin(call.from_user.id):
        return


@dp.callback_query(F.data == "get_all_parent_tasks")
async def get_all_parent_tasks(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    print(call.data)


@dp.callback_query(F.data == "show_all_tables")
async def show_all_tables(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    tables = lm.show_all_tables()

    _ = [f"{i}. {j}\n" for i, j in enumerate(tables, start=1)]
    text = "🚨 Available <b>TABLES</b>\n\n" + "".join(_)

    await call.message.answer(text=text, parse_mode="HTML")


@dp.callback_query(F.data == "insert_into_weekly_table")
async def insert_into_weekly_tables(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    print(call.data)


@dp.callback_query(F.data == "backup")
async def __backup(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    print(call.data)


@dp.callback_query(F.data == "restore_backup")
async def __restore_backup(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    print(call.data)


async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
