import asyncio
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = getenv("TELEGRAM_TOKEN")
dp = Dispatcher()

admins = [6739019257]


def __keyboard():

    builder = InlineKeyboardBuilder()

    builder.button(text="Add Daily Tasks", callback_data="add_daily_task")
    builder.button(text="Get All Parent Tasks", callback_data="get_all_parent_tasks")
    builder.button(text="Show All Tables", callback_data="show_all_tables")
    builder.button(text="Insert Task", callback_data="insert_into_weekly_table")
    builder.button(text="Start/End Timer", callback_data="timer")
    builder.button(text="Backup", callback_data="backup")
    builder.button(text="Restore backup", callback_data="restore_backup")

    builder.adjust(2)

    return builder.as_markup()


@dp.message(lambda x: x.from_user.id in admins)
async def _(msg):
    await msg.answer_sticker(
        sticker="CAACAgEAAxkBAAMeaBiC9lsHcRNZbo6neK-n0WhBtFgAAroIAAK_jJAEPvqh7iT5WyM2BA"
    )
    await msg.answer(text="🎛Panel🎛", reply_markup=__keyboard())


@dp.callback_query(
    lambda x: (x.from_user.id in admins) and (x.data == "add_daily_task")
)
def addDailyTask(call):
    print(call.data)


@dp.callback_query(
    lambda x: (x.from_user.id in admins) and (x.data == "get_all_parent_tasks")
)
def getAllParentTasks(call):
    print(call.data)


@dp.callback_query(
    lambda x: (x.from_user.id in admins) and (x.data == "show_all_tables")
)
def showAllTables(call):
    print(call.data)


@dp.callback_query(
    lambda x: (x.from_user.id in admins) and (x.data == "insert_into_weekly_table")
)
def InsertIntoWeeklyTables(call):
    print(call.data)


@dp.callback_query(lambda x: (x.from_user.id in admins) and (x.data == "timer"))
def __timer(call):
    print(call.data)


@dp.callback_query(lambda x: (x.from_user.id in admins) and (x.data == "backup"))
def __backup(call):
    print(call.data)


@dp.callback_query(
    lambda x: (x.from_user.id in admins) and (x.data == "restore_backup")
)
def __restore_backup(call):
    print(call.data)


async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
