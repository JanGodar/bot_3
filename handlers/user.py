import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from filters.filters import MyFalseFilter, MyTrueFilter
from lexicon.lexicon import LEXICON_RU


logger = logging.getLogger(__name__)

user_router = Router()


@user_router.message(CommandStart(), MyTrueFilter())
async def process_start_command(message: Message):
    logger.debug('Inside handler /start')
    button = InlineKeyboardButton(
        text='button',
        callback_data='button_pressed'
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[button]])
    await message.answer(text=LEXICON_RU['/start'],
                         reply_markup=markup)
    logger.debug('Outside handler /start')


@user_router.callback_query(F.data, MyTrueFilter())
async def process_button_click(callback: CallbackQuery):
    logger.debug('Inside handler inline_button')
    await callback.answer(text=LEXICON_RU['button_pressed'])
    logger.debug('Outside handler inline_button')


@user_router.message(F.text, MyFalseFilter())
async def process_text(message: Message):
    logger.debug('Inside handler text')
    logger.debug('Outside handler text')