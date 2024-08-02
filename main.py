from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, PhotoSize)


BOT_TOKEN = '6894820119:AAF2RLqBpsPCCgZ09pleLFFa0rAfrXTNG7s'

redis = Redis(host='localhost')
storage = RedisStorage(redis=redis)

bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=storage)

user_dict: dict[int, dict[str, str | int | bool]] = {}

class FSMFillForm(StatesGroup):
    fill_name = State()
    fill_age = State()
    fill_gender = State()
    upload_photo = State()
    fill_education = State()
    fill_wish_news = State()


@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text='Start - press /fillform'
    )

@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Fuck off - press /fillform'
    )


@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Exit from FSM, press /fillform'
    )
    await state.clear()


@dp.message(Command(commands='fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text='Insert your name')
    await state.set_state(FSMFillForm.fill_name)


@dp.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text='Insert you age')
    await state.set_state(FSMFillForm.fill_age)


@dp.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    await message.answer(
        text='Fuck off! Insert your name!'
    )


@dp.message(StateFilter(FSMFillForm.fill_age),
            lambda x: x.text.isdigit() and 4 <= int(x.text) <= 120)
async def process_age_sent(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    male_button = InlineKeyboardButton(
        text='male',
        callback_data='male'
    )
    female_button = InlineKeyboardButton(
        text='female',
        callback_data='female'
    )
    underfined_button = InlineKeyboardButton(
        text='fuck',
        callback_data='fuck'
    )
    keyboard: list[list[InlineKeyboardButton]] = [
        [male_button, female_button],
        [underfined_button]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(
        text='Insert your sex',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.fill_gender)


@dp.message(StateFilter(FSMFillForm.fill_age))
async def warning_not_age(message: Message):
    await message.answer(
        text='Fuck off! Insert your age'
    )

@dp.callback_query(StateFilter(FSMFillForm.fill_gender),
                   F.data.in_(['male', 'female', 'underfined_gender']))
async def process_gender_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data)
    await callback.message.delete()
    await callback.message.answer(
        text='Insert your photo'
    )
    await state.set_state(FSMFillForm.upload_photo)

@dp.message(StateFilter(FSMFillForm.fill_gender))
async def warning_not_gender(message: Message):
    await message.answer(
        text='Fuck off! Insert your sex'
    )

@dp.message(StateFilter(FSMFillForm.upload_photo),
            F.photo[-1].as_('largest_photo'))
async def process_photo_sent(message: Message, state: FSMContext,
                             largest_photo: PhotoSize):
    await state.update_data(
        photo_unique_id=largest_photo.file_unique_id,
        photo_id=largest_photo.file_id
    )
    secondary_button = InlineKeyboardButton(
        text='Middle',
        callback_data='secondary'
    )
    higher_button = InlineKeyboardButton(
        text='Senior',
        callback_data='higher'
    )
    no_edu_button = InlineKeyboardButton(
        text='No',
        callback_data='No edu'
    )
    keyboard = [
        [secondary_button, higher_button],
        [no_edu_button]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(
        text='Insert education',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.fill_education)


@dp.message(StateFilter(FSMFillForm.upload_photo))
async def warnign_not_photo(message):
    await message.answer(
        text='Fuck off! Insert photo'
    )

@dp.callback_query(StateFilter(FSMFillForm.fill_education),
                   F.data.in_(['secondary', 'higher', 'no_edu']))
async def process_education_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(education=callback.data)
    yes_news_button = InlineKeyboardButton(
        text='yes',
        callback_data='yes_news'
    )
    no_news_button = InlineKeyboardButton(
        text='no',
        callback_data='no_news'
    )
    keyboard = [
        [yes_news_button, no_news_button]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await callback.message.edit_text(
        text='Do you want get news?',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.fill_wish_news)


@dp.message(StateFilter(FSMFillForm.fill_education))
async def warning_not_education(message):
    await message.answer(
        text='Fuck off! Insert education'
    )


@dp.callback_query(StateFilter(FSMFillForm.fill_wish_news),
                   F.data.in_(['yes_news', 'no_news']))
async def process_wish_news_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(wish_news=callback.data == 'yes_news')
    user_dict[callback.from_user.id] = await state.get_data()
    await state.clear()
    await callback.message.edit_text(
        text='Fuck off, get out'
    )
    await callback.message.answer(
        text='Look your data /showdata'
    )


@dp.message(StateFilter(FSMFillForm.fill_wish_news))
async def warning_not_wish_news(message):
    await message.answer(
        text='Fuck off! Insert news'
    )

@dp.message(Command(commands='showdata'), StateFilter(default_state))
async def process_showdata_command(message):
    if message.from_user.id in user_dict:
        await message.answer_photo(
            photo=user_dict[message.from_user.id]['photo_id'],
            caption=f'Name: {user_dict[message.from_user.id]["name"]}\n'
                    f'Age: {user_dict[message.from_user.id]["age"]}\n'
                    f'Sex: {user_dict[message.from_user.id]["gender"]}\n'
                    f'Education: {user_dict[message.from_user.id]["education"]}\n'
                    f'Get news: {user_dict[message.from_user.id]["wish_news"]}'
        )
    else:
        await message.answer(text='Anket doesnt excist')

@dp.message(StateFilter(default_state))
async def send_echo(message):
    await message.reply(text='I dont fucking understand you')

if __name__ == '__main__':
    dp.run_polling(bot)

#BOT FOR GET ID FROM DIFFERENT UPDATES
# from aiogram import Bot, Dispatcher
# from aiogram.types import CallbackQuery, Message

# BOT_TOKEN = '6894820119:AAF2RLqBpsPCCgZ09pleLFFa0rAfrXTNG7s'
# dp = Dispatcher()
# bot = Bot(token=BOT_TOKEN)


# @dp.message()
# async def receive_file_id(message: Message):
#     if message.voice:
#         print("voice_id", end=' - ')
#         print(message.voice.file_id)
        
#     elif message.photo:
#         print("photo_id", end=' - ')
#         print(message.photo[0].file_id)
        
#     elif message.video:
#         print("video_id", end=' - ')
#         print(message.video.file_id)
        
#     elif message.animation:
#         print("animation_id", end=' - ')
#         print(message.animation.file_id)
        
#     elif message.document:
#         print("document_id", end=' - ')
#         print(message.document.file_id)
        
#     elif message.audio:
#         print("audio_id", end=' - ')
#         print(message.audio.file_id)


# if __name__ == '__main__':
#     dp.run_polling(bot)







# BOT FOR ALL PROJECT
# import asyncio
# import logging

# from aiogram import Bot, Dispatcher
# from config_data.config import Config, load_config
# from handlers.other import other_router
# from handlers.user import user_router
# from middlewares.inner import (
#     FirstInnerMiddleware,
#     SecondInnerMiddleware,
#     ThirdInnerMiddleware,
# )
# from middlewares.outer import (
#     FirstOuterMiddleware,
#     SecondOuterMiddleware,
#     ThirdOuterMiddleware,
# )


# logging.basicConfig(
#     level=logging.DEBUG,
#     format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
#             '%(lineno)d - %(name)s - %(message)s'
# )


# logger = logging.getLogger(__name__)


# async def main() -> None:

#     config: Config = load_config()

#     bot = Bot(token=config.tg_bot.token)
#     dp = Dispatcher()

#     dp.include_router(user_router)
#     dp.include_router(other_router)

#     #For middleware
#     dp.update.outer_middleware(FirstOuterMiddleware())
#     user_router.callback_query.outer_middleware(SecondOuterMiddleware())
#     other_router.message.outer_middleware(ThirdOuterMiddleware())
#     user_router.message.outer_middleware(FirstInnerMiddleware())
#     user_router.message.middleware(SecondInnerMiddleware())
#     other_router.message.middleware(ThirdInnerMiddleware())

#     await dp.start_polling(bot)


# asyncio.run(main())