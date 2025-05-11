import asyncio
import os

from aiogram import F, types
from dotenv import load_dotenv

load_dotenv()
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.environ["TELEGRAM_TOKEN"]


admins = [7860498898, 6739019257]
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from LifeManager.LM import LifeManager
from LifeManager.logger_config import logger
from LifeManager.TM import CTimer

dp = Dispatcher(storage=MemoryStorage())
lm = LifeManager()
tm = CTimer()


def is_admin(id) -> bool:
    return id in admins


# TODO: ADD await call.answer() TO EVERY INLINE BUTTON.
#! I want to work with inlines and callbacks. It is my preference.
def __keyboard():

    builder = InlineKeyboardBuilder()

    builder.button(text="DTM", callback_data="daily_task_manager")
    builder.button(text="Banking", callback_data="banking")
    builder.button(text="Chartings", callback_data="charting")

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
    await call.answer()
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
    await call.answer()
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
    await call.answer()
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
    await call.answer()
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

    await call.answer()
    if not is_admin(call.from_user.id):
        return
    global user_time_elapsed

    try:

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

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Yes", callback_data="timer_yes"),
                    InlineKeyboardButton(text="No", callback_data="timer_no"),
                ],
                [InlineKeyboardButton(text="Return", callback_data="timer")],
            ]
        )

        await call.message.answer(
            text=f"""<b>Note:</b> You can only store one time at a time. 
If you choose to store, it will replace the previous saved time.\n\n
<i>Please select an option below to proceed:</i>""",
            parse_mode="HTML",
            reply_markup=keyboard,
        )

    except:
        await call.message.answer(text="An Error HasBeen occurred. Read Log Files")
        logger.exception("Cannot End Timer in TelegramBOT.")


@dp.callback_query(F.data == "p_timer")
async def pause_timer(call: types.CallbackQuery):
    await call.answer()
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
    await call.answer()
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


@dp.callback_query(lambda x: x.data.startswith("timer_"))
async def wanna_use_time(call: types.CallbackQuery):
    response = call.data[6:]

    global user_duration  # $ For Using in the Inserting into table
    user_duration = user_time_elapsed

    if response == "yes":
        await call.answer(f"✅ Selected {user_duration} ✅")
    else:
        await call.answer(f"❌ Ignored {user_duration} ❌")

    await _timer(call)
    try:
        await call.message.delete()
    except TelegramBadRequest:
        pass  # ! This Means The message is Already deleted


# ~ -----------END |  Timer section ---------------
#! ------------START | TASKS -------------------
class TasksState(StatesGroup):
    adding_daily_tasks = State()
    parent_or_child = State()
    which_parent = State()


# * -------START | add_daily_task query handler ---------
@dp.callback_query(lambda x: x.data == "add_daily_task")
async def add_daily_task(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    if not is_admin(call.from_user.id):
        return
    await call.message.answer(
        "Now Send Me The Task that you want to add, So in the future you can work on it and use adding it to the weekly table : "
    )
    await state.set_state(TasksState.adding_daily_tasks)


@dp.message(TasksState.adding_daily_tasks)
async def process_adding_daily_tasks_state(message: Message, state: FSMContext):

    builder = InlineKeyboardBuilder()

    builder.button(text="👨 Parent", callback_data="parent_task")
    builder.button(text="👶 Child", callback_data="child_task")
    builder.button(text="❌ Abort", callback_data="abort")
    builder.adjust(2)
    keyboard = builder.as_markup()

    await message.answer(
        f"""Do you want to add the `<b>{message.text}</b>` as an parent task or a child task?\n
<b>NOTE:</b> For example watching `Youtube Tutorials` about programming can be a child class for `Programming`. Or it can be a PARENT that has for example `FreeCodeCamp` as its child.\n
The Parent/Chile relation comes back at YOUR PERSPECTIVE of the subject.""",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await state.update_data(task_name=message.text)  # User Response will be store here
    await state.set_state(TasksState.parent_or_child)


@dp.callback_query(TasksState.parent_or_child)
async def process_parent_or_child_state(call: types.CallbackQuery, state: FSMContext):

    if call.data == "abort":
        return await process_abort(call, state)  # Directly call the abort handler
    await call.answer()
    await state.update_data(
        parent_or_child=call.data
    )  # User Choice parent or child wil be store here

    data = await state.get_data()
    task_name = data.get("task_name")
    task_type = data.get("parent_or_child")

    if task_type == "parent_task":
        if lm.add_daily_task(task_name=task_name):
            await call.message.answer(
                text=f"✅ The {task_name} Has Been Added Successfully to the database."
            )
            return
        await call.message.answer(
            text=f"❌ There Was An Error Wile Adding {task_name} to the database."
        )
        return

    if task_type == "child_task":
        all_parents = lm.get_all_parent_tasks()
        builder = InlineKeyboardBuilder()
        for i in all_parents:
            builder.button(text=i, callback_data=f"parent_{i}")

        builder.button(text="❌ Abort", callback_data="abort")
        builder.adjust(2)
        keyboard = builder.as_markup()

        await call.message.answer(
            "Please Choose Your Desired Parent Task:", reply_markup=keyboard
        )
        await state.update_data(task_name=task_name)
        await state.set_state(TasksState.which_parent)


@dp.callback_query(TasksState.which_parent)
async def process_which_parent_state(call: types.CallbackQuery, state: FSMContext):
    if call.data == "abort":
        return await process_abort(call, state)  # Directly call the abort handler

    await call.answer()

    await state.update_data(which_parent=call.data)
    data = await state.get_data()
    task_name = data.get("task_name")
    parent_name = data.get("which_parent")[7:]

    if lm.add_daily_task(task_name=task_name, ref_to=parent_name):
        await call.message.answer(
            text=f"✅ The {task_name} Has Been Added Successfully to the database with {parent_name} as its Parent."
        )
        await state.clear()  # Clear FSM  state
        return
    else:
        await call.message.answer(
            text=f"❌ There Was An Error Wile Adding {task_name} to the database with {parent_name} as its Parent.\nHINT: Maybe the Parent Doesn't Exists."
        )
        await state.clear()  # Clear FSM state
        return


@dp.callback_query(lambda x: x.data == "abort")
async def process_abort(call: types.CallbackQuery, state: FSMContext):
    await call.answer("Operation cancelled ❌", show_alert=True)
    await state.clear()  # Clear FSM state

    try:  #! Delete the message only if it was sent by the bot

        if call.message.from_user.id == call.bot.id:
            await call.message.delete()
    except:
        logger.exception(
            "an error while deleting the message in telegram.py's process_abort callback_query handler."
        )


# * -------END | add_daily_task query handler ---------
# $-------START | INSERT INTO WEEKLY TABLE ------
class InsertingIntoTABLE(StatesGroup):
    pass


@dp.callback_query(F.data == "insert_into_weekly_table")
async def insert_into_weekly_tables(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    try:
        if not user_duration:
            raise NameError
    except NameError:
        await call.answer(
            f"First start the TIMER, to capture the duration for your work.",
            show_alert=True,
        )
        return
    except:
        logger.exception(
            "an Exception inside telegram.py module in insert_into_weekly_tables callback query handler."
        )
        return

    await call.answer()


# $-------END | INSERT INTO WEEKLY TABLE ------
@dp.callback_query(F.data == "get_all_parent_tasks")
async def _get_all_parent_tasks(call: types.CallbackQuery):
    await call.answer()
    if not is_admin(call.from_user.id):
        return
    parents = lm.get_all_parent_tasks()

    _ = [f"{i}. {j}\n" for i, j in enumerate(parents, start=1)]
    text = "🚨 Parent <b>TASKS</b>\n\n" + "".join(_)

    await call.message.answer(text=text, parse_mode="HTML")


@dp.callback_query(F.data == "show_all_tables")
async def show_all_tables(call: types.CallbackQuery):
    await call.answer()
    if not is_admin(call.from_user.id):
        return

    tables = lm.show_all_tables()

    _ = [f"{i}. {j}\n" for i, j in enumerate(tables, start=1)]
    text = "🚨 Available <b>TABLES</b>\n\n" + "".join(_)

    await call.message.answer(text=text, parse_mode="HTML")


#! ------------END | TASKS -------------------
# ? ------------START | BACKUP -------------------
@dp.callback_query(F.data == "backup")
async def __backup(call: types.CallbackQuery):
    await call.answer()
    if not is_admin(call.from_user.id):
        return
    print(call.data)


@dp.callback_query(F.data == "restore_backup")
async def __restore_backup(call: types.CallbackQuery):
    await call.answer()
    if not is_admin(call.from_user.id):
        return
    print(call.data)


# ? ------------END | BACKUP -------------------
async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
